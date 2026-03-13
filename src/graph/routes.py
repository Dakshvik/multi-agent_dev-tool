from __future__ import annotations

from typing import Any, Dict


def route_from_orchestrator(state: Dict[str, Any]) -> str:
    plan = state.get("routing_plan", [])
    if not plan:
        if state.get("approval_required") and state.get("approval_status") == "pending":
            return "hitl"
        return "synthesizer"
    return plan[0]


def route_after_validator(state: Dict[str, Any]) -> str:
    validation = state.get("validation")
    status = None

    if isinstance(validation, dict):
        status = validation.get("status")
    elif validation is not None:
        status = getattr(validation, "status", None)
        if hasattr(status, "value"):
            status = status.value

    if status == "fail":
        if state.get("retry_count", 0) < state.get("max_retries_per_agent", 2):
            return state.get("active_agent", "failed")
        return "failed"

    plan = state.get("routing_plan", [])
    if plan:
        return plan[0]

    if state.get("approval_required") and state.get("approval_status") == "pending":
        return "hitl"

    return "synthesizer"


def route_after_hitl(state: Dict[str, Any]) -> str:
    status = state.get("approval_status")
    if status == "approved":
        return "synthesizer"
    return "failed"