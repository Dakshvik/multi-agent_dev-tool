from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    UNKNOWN = "unknown"


class AgentName(str, Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    FIXER = "fixer"
    TEST = "test"
    DOCS = "docs"


class ApprovalStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ValidationStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"


class ValidationResult(BaseModel):
    status: ValidationStatus
    error_type: Optional[str] = None
    error_message: str = ""
    traceback: str = ""


class PipelineState(BaseModel):
    original_code: str
    current_code: str
    language: Language = Language.UNKNOWN
    fixed_code: str = ""

    routing_plan: List[AgentName] = Field(default_factory=list)
    last_completed_agent: Optional[AgentName] = None
    active_agent: Optional[AgentName] = None

    test_suite: str = ""
    docs: str = ""
    security_notes: str = ""
    performance_notes: str = ""

    validation: Optional[ValidationResult] = None
    errors: List[str] = Field(default_factory=list)
    retry_count: int = 0
    max_retries_per_agent: int = 2

    risk_score: float = 0.0
    approval_required: bool = False
    approval_status: ApprovalStatus = ApprovalStatus.NOT_REQUIRED
    approval_notes: str = ""

    state_summary: str = ""
    execution_log: List[Dict[str, Any]] = Field(default_factory=list)
    pr_report_markdown: str = ""

    def next_agent(self) -> Optional[AgentName]:
        if not self.routing_plan:
            return None
        return self.routing_plan[0]