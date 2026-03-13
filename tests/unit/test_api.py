from fastapi.testclient import TestClient

from src.api.app import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["docs_url"] == "/docs"


def test_review_endpoint():
    response = client.post(
        "/review",
        json={
            "code": "def add(a, b):\n    return a + b\n",
            "language": "python",
        },
    )
    assert response.status_code == 200

    body = response.json()
    assert body["validation"]["status"] == "pass"
    assert "Agentic PR Review" in body["pr_report_markdown"]
    assert isinstance(body["execution_log"], list)
    assert len(body["execution_log"]) >= 2
    assert isinstance(body["llm_diagnostics"], dict)