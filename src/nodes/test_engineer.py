from __future__ import annotations

from typing import Any, Dict

from src.llm.chatgroq_client import generate_test_suite


def run_test_engineer(state: Dict[str, Any]) -> Dict[str, Any]:
    state["active_agent"] = "test"

    language = str(state.get("language", "python"))
    code = str(state.get("current_code") or state.get("original_code") or "")

    test_suite, source = generate_test_suite(code=code, language=language)

    state["test_suite"] = test_suite
    state["state_summary"] = f"Test engineer executed (source={source})."

    execution_log = state.get("execution_log", [])
    execution_log.append(
        {
            "agent": "test",
            "source": source,
            "summary": "Unit tests generated.",
        }
    )
    state["execution_log"] = execution_log

    llm_diag = state.get("llm_diagnostics", {})
    llm_diag["test"] = source
    state["llm_diagnostics"] = llm_diag

    return state