import src.nodes.orchestrator as orchestrator


def test_orchestrator_uses_llm_plan(monkeypatch):
    def fake_generate_orchestrator_plan(code: str, language: str):
        return ["security", "performance", "test", "docs"], 0.82, "LLM decided route.", "chatgroq"

    monkeypatch.setattr(orchestrator, "generate_orchestrator_plan", fake_generate_orchestrator_plan)

    state = {
        "current_code": "def f(x): return x",
        "approval_status": "not_required",
        "execution_log": [],
    }
    out = orchestrator.run_orchestrator(state)

    assert out["routing_plan"] == ["security", "performance", "test", "docs"]
    assert out["risk_score"] == 0.82
    assert out["approval_required"] is True
    assert out["execution_log"][0]["agent"] == "orchestrator"
    assert out["execution_log"][0]["source"] == "chatgroq"


def test_orchestrator_falls_back_to_rules(monkeypatch):
    def fake_generate_orchestrator_plan(code: str, language: str):
        return [], 0.0, "", "fallback_error"

    monkeypatch.setattr(orchestrator, "generate_orchestrator_plan", fake_generate_orchestrator_plan)

    state = {
        "current_code": "for i in arr:\n    for j in arr:\n        print(i, j)",
        "approval_status": "not_required",
        "execution_log": [],
    }
    out = orchestrator.run_orchestrator(state)

    assert "performance" in out["routing_plan"]
    assert "test" in out["routing_plan"]
    assert "docs" in out["routing_plan"]
    assert out["execution_log"][0]["source"] == "fallback_error"