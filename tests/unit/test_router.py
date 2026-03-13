from src.graph.routes import route_after_hitl, route_after_validator, route_from_orchestrator
from src.nodes.orchestrator import run_orchestrator


def test_route_from_orchestrator_with_plan():
    state = {"routing_plan": ["security"], "approval_required": False, "approval_status": "not_required"}
    assert route_from_orchestrator(state) == "security"


def test_route_after_validator_fail_retry():
    state = {
        "validation": {"status": "fail"},
        "retry_count": 0,
        "max_retries_per_agent": 2,
        "active_agent": "test",
    }
    assert route_after_validator(state) == "test"


def test_route_after_hitl():
    assert route_after_hitl({"approval_status": "approved"}) == "synthesizer"
    assert route_after_hitl({"approval_status": "pending"}) == "failed"


def test_orchestrator_security_plan():
    state = {
        "current_code": "cursor.execute('select * from users where token = ?')",
        "approval_status": "not_required",
    }
    out = run_orchestrator(state)
    assert "security" in out["routing_plan"]
    assert "test" in out["routing_plan"]
    assert "docs" in out["routing_plan"]


def test_orchestrator_performance_plan():
    state = {
        "current_code": "for i in arr:\n    for j in arr:\n        x.append(i+j)",
        "approval_status": "not_required",
    }
    out = run_orchestrator(state)
    assert "performance" in out["routing_plan"]
    assert "test" in out["routing_plan"]
    assert "docs" in out["routing_plan"]


def test_orchestrator_high_risk_sets_pending_approval():
    state = {
        "current_code": "auth token password secret sql select update delete cursor.execute(",
        "approval_status": "not_required",
    }
    out = run_orchestrator(state)
    assert out["risk_score"] >= 0.7
    assert out["approval_required"] is True
    assert out["approval_status"] == "pending"