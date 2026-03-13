from __future__ import annotations

from typing import Any, Dict


def run_synthesizer(state: Dict[str, Any]) -> Dict[str, Any]:
    execution_log = state.get("execution_log", [])
    state["pr_report_markdown"] = (
        "# Agentic PR Review\n\n"
        "Pipeline completed.\n\n"
        f"- Last completed agent: {state.get('last_completed_agent')}\n"
        f"- Remaining plan: {state.get('routing_plan', [])}\n"
        f"- Validation: {state.get('validation')}\n"
        f"- Security notes: {state.get('security_notes', '')}\n"
        f"- Execution log entries: {len(execution_log)}\n"
    )
    return state


def run_failed(state: Dict[str, Any]) -> Dict[str, Any]:
    if state.get("approval_required") and state.get("approval_status") == "pending":
        state["pr_report_markdown"] = "Pipeline paused for human approval."
    else:
        state["pr_report_markdown"] = "Pipeline stopped due to validation failure or approval rejection."
    return state