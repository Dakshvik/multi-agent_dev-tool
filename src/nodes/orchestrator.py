from __future__ import annotations

from typing import Any, Dict, List, Tuple

from src.llm.chatgroq_client import generate_orchestrator_plan


def _security_signal_count(text: str) -> int:
    security_keywords = [
        "auth", "token", "jwt", "password", "secret", "api_key",
        "sql", "select ", "insert ", "update ", "delete ",
        "database", "db.", "cursor", "execute(", "raw_query",
    ]
    return sum(1 for k in security_keywords if k in text)


def _performance_signal_count(text: str) -> int:
    perf_keywords = [
        "for ", "while ", "range(", "sort(", ".sort(",
        "append(", "recursion", "nested loop",
    ]
    return sum(1 for k in perf_keywords if k in text)


def _detect_nested_loop_hint(text: str) -> bool:
    return text.count("for ") >= 2 or ("for " in text and "while " in text)


def _compute_risk_score(security_hits: int, perf_hits: int, nested_loop: bool) -> float:
    score = 0.0
    score += min(0.75, security_hits * 0.15)
    score += min(0.25, perf_hits * 0.06)
    if nested_loop:
        score += 0.1
    return round(min(1.0, score), 2)


def _build_plan(text: str) -> Tuple[List[str], List[str], int, int, bool]:
    reasons: List[str] = []
    plan: List[str] = []

    security_hits = _security_signal_count(text)
    perf_hits = _performance_signal_count(text)
    nested_loop = _detect_nested_loop_hint(text)

    if security_hits > 0:
        plan.append("security")
        reasons.append(f"Security signals detected: {security_hits}")

    if perf_hits > 0 or nested_loop:
        plan.append("performance")
        reasons.append(f"Performance signals detected: {perf_hits}, nested_loop={nested_loop}")

    plan.append("test")
    reasons.append("Always include test generation.")
    plan.append("docs")
    reasons.append("Always include documentation update.")

    deduped: List[str] = []
    seen = set()
    for step in plan:
        if step not in seen:
            deduped.append(step)
            seen.add(step)

    return deduped, reasons, security_hits, perf_hits, nested_loop


def run_orchestrator(state: Dict[str, Any]) -> Dict[str, Any]:
    source_code = str(state.get("current_code") or state.get("original_code") or "")
    lowered = source_code.lower()
    language = str(state.get("language", "python"))

    llm_plan, llm_risk, llm_reasoning, llm_source = generate_orchestrator_plan(
        code=source_code,
        language=language,
    )

    if llm_source == "chatgroq" and llm_plan:
        plan = llm_plan
        risk_score = llm_risk
        reason_text = llm_reasoning or "LLM routing plan generated."
    else:
        plan, reasons, security_hits, perf_hits, nested_loop = _build_plan(lowered)
        risk_score = _compute_risk_score(security_hits, perf_hits, nested_loop)
        reason_text = " | ".join(reasons)

    # Snapshot must be immutable w.r.t later routing pops.
    plan_snapshot = list(plan)

    state["routing_plan"] = list(plan)
    state["risk_score"] = risk_score
    state["approval_required"] = risk_score >= 0.7
    state["state_summary"] = f"Orchestrator executed (source={llm_source}). {reason_text}"
    state["retry_count"] = 0
    state["active_agent"] = None

    if state["approval_required"] and state.get("approval_status") in (None, "not_required"):
        state["approval_status"] = "pending"

    execution_log = state.get("execution_log", [])
    execution_log.append(
        {
            "agent": "orchestrator",
            "source": llm_source,
            "summary": reason_text,
            "risk_score": risk_score,
            "plan": plan_snapshot,
        }
    )
    state["execution_log"] = execution_log

    llm_diag = state.get("llm_diagnostics", {})
    llm_diag["orchestrator"] = llm_source
    state["llm_diagnostics"] = llm_diag

    return state