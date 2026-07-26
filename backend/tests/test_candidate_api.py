import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from clipops.main import app
from clipops.models import (
    AccountProfile,
    Base,
    ClipCandidate,
    SourceContent,
    WorkflowRun,
)
from clipops.schemas import ClipScoreSchema
from clipops.scoring import save_score


@pytest.fixture
def client(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    app.state.engine = engine
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(
            [
                SourceContent(id="source", title="Source"),
                AccountProfile(id="account", name="Account", platform="Demo", details={}),
                WorkflowRun(id="workflow", status="COMPLETED"),
                ClipCandidate(id="lower", source_content_id="source", workflow_run_id="workflow", account_profile_id="account", start_seconds=0, end_seconds=10, duration_seconds=10, transcript_excerpt="Lower", reason_selected="Reason", confidence=0.5, status="DETECTED"),
                ClipCandidate(id="higher", source_content_id="source", workflow_run_id="workflow", account_profile_id="account", start_seconds=10, end_seconds=20, duration_seconds=10, transcript_excerpt="Higher", reason_selected="Reason", confidence=0.5, status="APPROVED"),
            ]
        )
        session.commit()
        for candidate_id, hook_strength in [("lower", 2), ("higher", 5)]:
            save_score(
                session,
                candidate_id,
                ClipScoreSchema(hook_strength=hook_strength, standalone_clarity=3, novelty=3, emotional_intensity=3, shareability=3, educational_value=3, brand_safety=5, editing_complexity=2, confidence=0.7),
            )
    yield TestClient(app)
    app.state.engine = None


def test_candidates_are_ranked_and_include_asset_placeholder(client: TestClient) -> None:
    response = client.get("/workflow-runs/workflow/candidates")
    assert [item["candidate_id"] for item in response.json()] == ["higher", "lower"]
    assert response.json()[0]["assets"] == []


def test_candidates_filter_by_status(client: TestClient) -> None:
    response = client.get("/workflow-runs/workflow/candidates?status=APPROVED")
    assert [item["candidate_id"] for item in response.json()] == ["higher"]


def test_missing_workflow_candidates_returns_not_found(client: TestClient) -> None:
    response = client.get("/workflow-runs/missing/candidates")
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"
