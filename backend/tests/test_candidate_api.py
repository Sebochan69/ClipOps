import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from clipops.main import app
from clipops.models import (
    AccountProfile,
    Base,
    ClipCandidate,
    GeneratedAsset,
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
                ClipCandidate(id="lower", source_content_id="source", workflow_run_id="workflow", account_profile_id="account", start_seconds=0, end_seconds=10, duration_seconds=10, transcript_excerpt="Lower", reason_selected="Reason", confidence=0.5, status="NEEDS_REVIEW"),
                ClipCandidate(id="higher", source_content_id="source", workflow_run_id="workflow", account_profile_id="account", start_seconds=10, end_seconds=20, duration_seconds=10, transcript_excerpt="Higher", reason_selected="Reason", confidence=0.5, status="APPROVED"),
                GeneratedAsset(id="asset", candidate_id="higher", asset_type="hook", content="Original hook"),
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


def test_only_approved_candidate_can_be_queued(client: TestClient) -> None:
    response = client.post("/candidates/higher/queue", json={"scheduled_for": "2026-08-01T09:00:00Z"})
    assert response.json() == {"queue_item_id": "queue:higher", "status": "QUEUED"}
    assert client.get("/publishing-queue").json()[0]["account"] == "Account"
    performance = client.post("/performance-records", json={"queue_item_id": "queue:higher", "views": 1000, "engagement_rate": 0.12})
    assert performance.json() == {"performance_record_id": "performance:queue:higher", "simulated": True}
    dashboard = client.get("/dashboard").json()
    assert dashboard["simulated"] and dashboard["accounts"][0]["published_clips"] == 1
    rejected = client.post("/candidates/lower/queue", json={"scheduled_for": "2026-08-01T09:00:00Z"})
    assert rejected.json()["code"] == "BUSINESS_RULE_VALIDATION_ERROR"


def test_review_action_changes_status_and_records_decision(client: TestClient) -> None:
    response = client.post("/candidates/lower/review", json={"action": "APPROVE"})
    assert response.json() == {"candidate_id": "lower", "status": "APPROVED"}
    invalid = client.post("/candidates/higher/review", json={"action": "APPROVE"})
    assert invalid.json()["code"] == "INVALID_STATE_TRANSITION"


def test_candidate_detail_and_asset_edit(client: TestClient) -> None:
    response = client.get("/candidates/higher")
    assert response.json()["scores"]["overall_score"] > 0
    assert response.json()["assets"][0]["content"] == "Original hook"
    updated = client.patch("/candidates/higher/assets/asset", json={"content": "Edited hook"})
    assert updated.json() == {"id": "asset", "content": "Edited hook"}


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
