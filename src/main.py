from __future__ import annotations

from src.graph.workflow import run_pipeline


def demo_state():
    code = "def add(a, b):\n    return a + b\n"
    return {
        "original_code": code,
        "current_code": code,
        "language": "python",
        "routing_plan": [],
        "last_completed_agent": None,
        "active_agent": None,
        "test_suite": "",
        "docs": "",
        "validation": None,
        "errors": [],
        "retry_count": 0,
        "max_retries_per_agent": 2,
        "risk_score": 0.4,
        "approval_required": False,
        "approval_status": "not_required",
        "approval_notes": "",
        "pr_report_markdown": "",
    }


if __name__ == "__main__":
    final_state = run_pipeline(demo_state())
    print("Last completed:", final_state.get("last_completed_agent"))
    print("Pending agents:", final_state.get("routing_plan"))
    print("Validation:", final_state.get("validation"))
    print("Report:", final_state.get("pr_report_markdown"))