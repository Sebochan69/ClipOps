from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from clipops.models import (
    AccountProfile,
    Base,
    ClipCandidate,
    SourceContent,
    WorkflowRun,
)
from clipops.schemas import ClipScoreSchema
from clipops.scoring import calculate_score, save_score


def score_input() -> ClipScoreSchema:
    return ClipScoreSchema(
        hook_strength=5,
        standalone_clarity=4,
        novelty=3,
        emotional_intensity=4,
        shareability=3,
        educational_value=5,
        brand_safety=5,
        editing_complexity=2,
        confidence=0.8,
    )


def test_calculates_transparent_weighted_score() -> None:
    score = calculate_score(score_input())
    assert score.overall_score == 84
    assert score.explanation == "Strongest dimension: hook strength."


def test_score_is_saved_for_candidate() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(
            [
                SourceContent(id="source", title="Source"),
                AccountProfile(id="account", name="Account", platform="Demo", details={}),
                WorkflowRun(id="workflow", status="COMPLETED"),
                ClipCandidate(
                    id="candidate",
                    source_content_id="source",
                    workflow_run_id="workflow",
                    account_profile_id="account",
                    start_seconds=0,
                    end_seconds=10,
                    duration_seconds=10,
                    transcript_excerpt="Excerpt",
                    reason_selected="Reason",
                    confidence=0.5,
                    status="DETECTED",
                ),
            ]
        )
        session.commit()
        record = save_score(session, "candidate", score_input())
        assert record.overall_score == 84
        assert session.get(ClipCandidate, "candidate").confidence == 0.8
