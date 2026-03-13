from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    code: str = Field(min_length=1)
    language: str = "python"
    approval_status: str = "not_required"


class ReviewResponse(BaseModel):
    last_completed_agent: Optional[str] = None
    routing_plan: List[str] = Field(default_factory=list)
    validation: Optional[Dict[str, Any]] = None
    state_summary: str = ""
    execution_log: List[Dict[str, Any]] = Field(default_factory=list)
    llm_diagnostics: Dict[str, str] = Field(default_factory=dict)
    test_suite: str = ""
    docs: str = ""
    security_notes: str = ""
    performance_notes: str = ""
    fixed_code: str = ""
    risk_score: float = 0.0
    approval_required: bool = False
    approval_status: str = "not_required"
    pr_report_markdown: str = ""