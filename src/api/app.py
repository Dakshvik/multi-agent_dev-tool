from __future__ import annotations

from fastapi import FastAPI

from src.api.schemas import ReviewRequest, ReviewResponse
from src.graph.workflow import run_pipeline

app = FastAPI(
    title="Agentic PR Pipeline",
    version="0.1.0",
    description="Zero-to-Production Agentic PR Pipeline API",
)


def _build_initial_state(payload: ReviewRequest) -> dict:
    return {
        "original_code": payload.code,
        "current_code": payload.code,
        "fixed_code": "",
        "language": payload.language,
        "routing_plan": [],
        "last_completed_agent": None,
        "active_agent": None,
        "test_suite": "",
        "docs": "",
        "security_notes": "",
        "performance_notes": "",
        "validation": None,
        "errors": [],
        "retry_count": 0,
        "max_retries_per_agent": 2,
        "risk_score": 0.0,
        "approval_required": False,
        "approval_status": payload.approval_status,
        "approval_notes": "",
        "pr_report_markdown": "",
        "state_summary": "",
        "execution_log": [],
        "llm_diagnostics": {},
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/")
def root() -> dict:
    return {
        "name": "Agentic PR Pipeline",
        "status": "ok",
        "docs_url": "/docs",
        "health_url": "/health",
    }


@app.post("/review", response_model=ReviewResponse)
def review(payload: ReviewRequest) -> ReviewResponse:
    final_state = run_pipeline(_build_initial_state(payload))
    return ReviewResponse(
        last_completed_agent=final_state.get("last_completed_agent"),
        routing_plan=final_state.get("routing_plan", []),
        validation=final_state.get("validation"),
        state_summary=final_state.get("state_summary", ""),
        execution_log=final_state.get("execution_log", []),
        llm_diagnostics=final_state.get("llm_diagnostics", {}),
        test_suite=final_state.get("test_suite", ""),
        docs=final_state.get("docs", ""),
        security_notes=final_state.get("security_notes", ""),
        performance_notes=final_state.get("performance_notes", ""),
        fixed_code=final_state.get("fixed_code", ""),
        risk_score=float(final_state.get("risk_score", 0.0)),
        approval_required=bool(final_state.get("approval_required", False)),
        approval_status=final_state.get("approval_status", "not_required"),
        pr_report_markdown=final_state.get("pr_report_markdown", ""),
    )