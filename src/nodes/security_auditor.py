from __future__ import annotations

from typing import Any, Dict

from src.llm.chatgroq_client import generate_security_review


def run_security_auditor(state: Dict[str, Any]) -> Dict[str, Any]:
    state["active_agent"] = "security"

    language = str(state.get("language", "python"))
    code = str(state.get("current_code") or state.get("original_code") or "")

    security_notes, source = generate_security_review(code=code, language=language)

    state["security_notes"] = security_notes
    state["state_summary"] = f"Security auditor executed (source={source})."

    execution_log = state.get("execution_log", [])
    execution_log.append(
        {
            "agent": "security",
            "source": source,
            "summary": security_notes,
        }
    )
    state["execution_log"] = execution_log

    llm_diag = state.get("llm_diagnostics", {})
    llm_diag["security"] = source
    state["llm_diagnostics"] = llm_diag

    return state