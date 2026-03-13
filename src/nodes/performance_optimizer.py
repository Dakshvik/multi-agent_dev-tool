from __future__ import annotations

from typing import Any, Dict

from src.llm.chatgroq_client import generate_performance_review


def run_performance_optimizer(state: Dict[str, Any]) -> Dict[str, Any]:
    state["active_agent"] = "performance"

    language = str(state.get("language", "python"))
    code = str(state.get("current_code") or state.get("original_code") or "")

    performance_notes, source = generate_performance_review(code=code, language=language)

    state["performance_notes"] = performance_notes
    state["state_summary"] = f"Performance optimizer executed (source={source})."

    execution_log = state.get("execution_log", [])
    execution_log.append(
        {
            "agent": "performance",
            "source": source,
            "summary": performance_notes,
        }
    )
    state["execution_log"] = execution_log

    llm_diag = state.get("llm_diagnostics", {})
    llm_diag["performance"] = source
    state["llm_diagnostics"] = llm_diag

    return state