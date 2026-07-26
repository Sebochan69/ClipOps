from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from clipops.main import app
from clipops.model_provider import MockModelProvider
from clipops.models import (
    AccountProfile,
    Base,
    ClipCandidate,
    ClipScore,
    ContentExperiment,
    ModelRun,
    PerformanceRecord,
    PublishingQueueItem,
    SourceContent,
    WeeklyGrowthReport,
    WorkflowRun,
)
from clipops.weekly_report import generate_weekly_report


def seed_report_fixture(session: Session) -> None:
    session.add_all(
        [
            SourceContent(id="source", title="Source"),
            AccountProfile(id="account", name="Account", platform="Demo", details={}),
            WorkflowRun(id="workflow-ok", status="COMPLETED"),
            WorkflowRun(id="workflow-failed", status="FAILED", error_message="Invalid transcript"),
            ModelRun(
                id="model-run",
                workflow_run_id="workflow-ok",
                provider="mock",
                model="deterministic-v1",
                prompt_version="asset-generation-v1",
                validation_result="VALID",
                repair_count=0,
            ),
            ClipCandidate(
                id="winner",
                source_content_id="source",
                workflow_run_id="workflow-ok",
                account_profile_id="account",
                start_seconds=0,
                end_seconds=30,
                duration_seconds=30,
                transcript_excerpt="Clear tactical lesson.",
                reason_selected="Useful",
                confidence=0.9,
                status="PUBLISHED",
            ),
            ClipCandidate(
                id="laggard",
                source_content_id="source",
                workflow_run_id="workflow-ok",
                account_profile_id="account",
                start_seconds=30,
                end_seconds=60,
                duration_seconds=30,
                transcript_excerpt="Less specific takeaway.",
                reason_selected="Useful",
                confidence=0.6,
                status="PUBLISHED",
            ),
            ClipScore(
                id="score:winner",
                candidate_id="winner",
                hook_strength=5,
                standalone_clarity=5,
                novelty=4,
                emotional_intensity=3,
                shareability=4,
                educational_value=5,
                brand_safety=5,
                editing_complexity=2,
                overall_score=88,
                confidence=0.9,
                explanation="Strongest dimension: standalone clarity.",
            ),
            ClipScore(
                id="score:laggard",
                candidate_id="laggard",
                hook_strength=2,
                standalone_clarity=3,
                novelty=2,
                emotional_intensity=2,
                shareability=2,
                educational_value=3,
                brand_safety=5,
                editing_complexity=2,
                overall_score=58,
                confidence=0.6,
                explanation="Hook is less specific.",
            ),
            PublishingQueueItem(
                id="queue:winner",
                candidate_id="winner",
                account_profile_id="account",
                status="PUBLISHED",
                scheduled_for="2026-08-05T09:00:00Z",
            ),
            PublishingQueueItem(
                id="queue:laggard",
                candidate_id="laggard",
                account_profile_id="account",
                status="PUBLISHED",
                scheduled_for="2026-08-06T09:00:00Z",
            ),
            PerformanceRecord(id="performance:winner", queue_item_id="queue:winner", views=2000, engagement_rate=0.14),
            PerformanceRecord(id="performance:laggard", queue_item_id="queue:laggard", views=500, engagement_rate=0.03),
            ContentExperiment(
                id="hooks",
                name="Hook test",
                hypothesis="Direct hooks improve engagement.",
                primary_metric="engagement_rate",
                variant_a="Question hook",
                variant_b="Direct claim hook",
                result_summary="Question hook led the simulated sample.",
                winner="Question hook",
                confidence_note="Simulated, small sample.",
            ),
        ]
    )
    session.commit()


def test_generate_weekly_report_includes_required_sections() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        seed_report_fixture(session)
        report = generate_weekly_report(session, date(2026, 8, 7))

        assert report.week_range == "2026-08-01 to 2026-08-07"
        assert report.fleet_snapshot["published_clip_count"] == 2
        assert report.top_clips[0]["candidate_id"] == "winner"
        assert report.top_clips[0]["why_it_worked"] == "Strongest dimension: standalone clarity."
        assert report.underperforming_clips[0]["candidate_id"] == "laggard"
        assert report.experiment_readout["winner"] == "Question hook"
        assert report.workflow_metrics["status_counts"] == {"COMPLETED": 1, "FAILED": 1}
        assert report.next_experiment["recommendation_source"] == "deterministic"
        assert any("simulated" in caveat.lower() for caveat in report.caveats)
        assert session.scalar(select(WeeklyGrowthReport).where(WeeklyGrowthReport.id == "weekly:2026-08-07"))


def test_weekly_report_can_use_mock_provider_recommendation() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        seed_report_fixture(session)
        report = generate_weekly_report(session, date(2026, 8, 7), provider=MockModelProvider())

        assert report.next_experiment["recommendation_source"] == "mock"
        assert report.next_experiment["name"] == "Mock weekly hook refinement"
        assert "approval rate is 100%" in report.next_experiment["rationale"]


def test_weekly_report_api_returns_structured_report(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    app.state.engine = engine
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        seed_report_fixture(session)

    response = TestClient(app).post("/weekly-reports", json={"week_end": "2026-08-07"})

    assert response.status_code == 200
    assert response.json()["id"] == "weekly:2026-08-07"
    assert response.json()["fleet_snapshot"]["published_clip_count"] == 2
    assert response.json()["experiment_readout"]["winner"] == "Question hook"
    app.state.engine = None
