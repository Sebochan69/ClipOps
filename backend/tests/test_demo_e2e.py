from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from clipops.main import app
from clipops.models import AccountProfile, Base, ClipCandidate, SourceContent
from clipops.schemas import ClipScoreSchema
from clipops.scoring import save_score
from clipops.workflow import run_workflow


def test_demo_path(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'demo.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all([
            SourceContent(id="source", title="Demo source"),
            AccountProfile(id="account", name="Demo account", platform="Demo", details={"brand_safety_rules": ["No claims"]}),
        ])
        session.commit()
    transcript = "\n".join(f"[00:{second:02d}] line {second}" for second in range(10))
    workflow = run_workflow(engine, transcript, source_content_id="source", account_profile_id="account")
    with Session(engine) as session:
        candidate = session.scalar(select(ClipCandidate).where(ClipCandidate.workflow_run_id == workflow["workflow_run_id"]))
        assert candidate
        save_score(session, candidate.id, ClipScoreSchema(hook_strength=4, standalone_clarity=4, novelty=3, emotional_intensity=3, shareability=3, educational_value=4, brand_safety=5, editing_complexity=2, confidence=0.8))
        candidate_id = candidate.id
    app.state.engine = engine
    client = TestClient(app)
    assert client.post(f"/candidates/{candidate_id}/review", json={"action": "SUBMIT_FOR_REVIEW"}).json()["status"] == "NEEDS_REVIEW"
    assert client.post(f"/candidates/{candidate_id}/review", json={"action": "APPROVE"}).json()["status"] == "APPROVED"
    queue = client.post(f"/candidates/{candidate_id}/queue", json={"scheduled_for": "2026-08-01T09:00:00Z"}).json()
    client.post("/performance-records", json={"queue_item_id": queue["queue_item_id"], "views": 1000, "engagement_rate": 0.1})
    client.post("/experiments", json={"id": "experiment", "name": "Hooks", "hypothesis": "Test hooks", "primary_metric": "engagement_rate", "variant_a": "A", "variant_b": "B", "confidence_note": "Simulated."})
    assert client.post("/weekly-reports", json={}).json()["simulated"] is True
    app.state.engine = None
