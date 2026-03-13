from __future__ import annotations

from typing import Any, Dict

from src.llm.chatgroq_client import generate_fixed_code


def run_code_fixer(state: Dict[str, Any]) -> Dict[str, Any]:
    state["active_agent"] = "fixer"

    code = str(state.get("current_code") or state.get("original_code") or "")
    language = str(state.get("language", "python"))
    security_notes = str(state.get("security_notes", ""))
    performance_notes = str(state.get("performance_notes", ""))

    fixed_code, source = generate_fixed_code(
        code=code,
        language=language,
        security_notes=security_notes,
        performance_notes=performance_notes,
    )

    state["fixed_code"] = fixed_code
    state["current_code"] = fixed_code
    state["state_summary"] = f"Code fixer executed (source={source})."

    execution_log = list(state.get("execution_log", []))
    execution_log.append(
        {
            "agent": "fixer",
            "source": source,
            "summary": "Fixed code generated from security and performance findings.",
        }
    )
    state["execution_log"] = execution_log

    llm_diag = dict(state.get("llm_diagnostics", {}))
    llm_diag["fixer"] = source
    state["llm_diagnostics"] = llm_diag

    return state