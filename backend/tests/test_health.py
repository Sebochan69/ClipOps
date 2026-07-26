from fastapi.testclient import TestClient

from clipops.main import app


def test_health() -> None:
    assert TestClient(app).get("/health").json() == {"status": "ok"}
