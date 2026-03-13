from __future__ import annotations

from typing import Any, Dict

from src.config import settings


def run_hitl_gate(state: Dict[str, Any]) -> Dict[str, Any]:
    risk_score = float(state.get("risk_score", 0.0))
    if risk_score >= settings.risk_approval_threshold:
        state["approval_required"] = True
        if state.get("approval_status") in (None, "not_required"):
            state["approval_status"] = "pending"
    return state