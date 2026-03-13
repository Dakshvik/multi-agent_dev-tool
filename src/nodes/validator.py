from __future__ import annotations

import ast
from typing import Any, Dict


def _validation_fail(state: Dict[str, Any], error_type: str, message: str, trace: str = "") -> Dict[str, Any]:
    state["validation"] = {
        "status": "fail",
        "error_type": error_type,
        "error_message": message,
        "traceback": trace,
    }
    errors = state.get("errors", [])
    errors.append(message)
    state["errors"] = errors
    return state


def run_validator(state: Dict[str, Any]) -> Dict[str, Any]:
    code = state.get("current_code", "")
    language = state.get("language", "unknown")

    filler_markers = ["Here is the refactored code:", "Sure, I can help", "```"]
    for marker in filler_markers:
        if marker in code:
            state["retry_count"] = state.get("retry_count", 0) + 1
            return _validation_fail(
                state,
                "format_error",
                f"Disallowed filler/format marker found: {marker}",
            )

    if language == "python":
        try:
            ast.parse(code)
        except SyntaxError as exc:
            state["retry_count"] = state.get("retry_count", 0) + 1
            return _validation_fail(
                state,
                "syntax_error",
                str(exc),
                f"line={exc.lineno}, offset={exc.offset}",
            )

    state["validation"] = {"status": "pass"}
    state["retry_count"] = 0

    plan = state.get("routing_plan", [])
    active = state.get("active_agent")
    if plan and active and plan[0] == active:
        plan.pop(0)
        state["routing_plan"] = plan
        state["last_completed_agent"] = active

    return state