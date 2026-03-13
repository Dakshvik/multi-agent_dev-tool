import src.nodes.performance_optimizer as performance_optimizer


def test_performance_node_appends_execution_log(monkeypatch):
    def fake_generate_performance_review(code: str, language: str):
        return "Nested loop O(n^2) detected. Consider hashmap indexing.", "chatgroq"

    monkeypatch.setattr(
        performance_optimizer,
        "generate_performance_review",
        fake_generate_performance_review,
    )

    state = {
        "current_code": "for i in arr:\n    for j in arr:\n        pass",
        "language": "python",
        "execution_log": [],
    }

    out = performance_optimizer.run_performance_optimizer(state)

    assert "Nested loop" in out["performance_notes"]
    assert out["execution_log"][0]["agent"] == "performance"
    assert out["execution_log"][0]["source"] == "chatgroq"