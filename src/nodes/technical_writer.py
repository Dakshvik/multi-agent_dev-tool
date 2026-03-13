from __future__ import annotations

from typing import Any, Dict

from src.llm.chatgroq_client import generate_docs_summary


def run_technical_writer(state: Dict[str, Any]) -> Dict[str, Any]:
    state["active_agent"] = "docs"

    language = str(state.get("language", "python"))
    code = str(state.get("current_code") or state.get("original_code") or "")
    security_notes = str(state.get("security_notes", ""))
    performance_notes = str(state.get("performance_notes", ""))
    test_suite = str(state.get("test_suite", ""))

    validation = state.get("validation", {})
    validation_status = ""
    if isinstance(validation, dict):
        validation_status = str(validation.get("status", "unknown"))

    docs, source = generate_docs_summary(
        code=code,
        language=language,
        security_notes=security_notes,
        performance_notes=performance_notes,
        test_suite=test_suite,
        validation_status=validation_status,
    )

    state["docs"] = docs
    state["state_summary"] = f"Technical writer executed (source={source})."

    execution_log = state.get("execution_log", [])
    execution_log.append(
        {
            "agent": "docs",
            "source": source,
            "summary": "Documentation generated.",
        }
    )
    state["execution_log"] = execution_log

    llm_diag = state.get("llm_diagnostics", {})
    llm_diag["docs"] = source
    state["llm_diagnostics"] = llm_diag

    return state