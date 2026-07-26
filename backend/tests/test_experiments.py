from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from clipops.main import app


def test_create_hook_experiment(tmp_path) -> None:
    app.state.engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    response = TestClient(app).post("/experiments", json={"id": "hooks", "name": "Hook test", "hypothesis": "Direct hooks improve engagement.", "primary_metric": "engagement_rate", "variant_a": "Question", "variant_b": "Statement", "confidence_note": "Simulated, small sample."})
    assert response.json()["variant_a"] == "Question"
    app.state.engine = None
