from src.nodes.validator import run_validator


def test_validator_passes_valid_python():
    state = {
        "current_code": "x = 1\n",
        "language": "python",
        "errors": [],
        "routing_plan": ["test"],
        "active_agent": "test",
        "retry_count": 0,
    }
    out = run_validator(state)
    assert out["validation"]["status"] == "pass"
    assert out["routing_plan"] == []


def test_validator_fails_syntax_error():
    state = {"current_code": "def bad(:\n    pass\n", "language": "python", "errors": [], "retry_count": 0}
    out = run_validator(state)
    assert out["validation"]["status"] == "fail"
    assert out["validation"]["error_type"] == "syntax_error"
    assert out["retry_count"] == 1