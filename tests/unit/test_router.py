from src.graph.routes import route_after_hitl, route_after_validator, route_from_orchestrator


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