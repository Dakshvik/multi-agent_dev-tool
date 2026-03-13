import src.nodes.security_auditor as security_auditor


def test_security_node_appends_execution_log(monkeypatch):
    def fake_generate_security_review(code: str, language: str):
        return "Possible SQL injection risk. Use parameterized queries.", "chatgroq"

    monkeypatch.setattr(
        security_auditor,
        "generate_security_review",
        fake_generate_security_review,
    )

    state = {
        "current_code": "cursor.execute('select * from users')",
        "language": "python",
        "execution_log": [],
    }

    out = security_auditor.run_security_auditor(state)

    assert out["security_notes"] == "Possible SQL injection risk. Use parameterized queries."
    assert out["execution_log"][0]["agent"] == "security"
    assert out["execution_log"][0]["source"] == "chatgroq"