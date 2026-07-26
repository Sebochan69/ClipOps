import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from clipops.asset_generation import REQUIRED_COUNTS
from clipops.business_validation import BusinessRuleValidationError, mark_needs_review
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


def candidate_session() -> tuple[Session, ClipCandidate]:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = Session(engine)
    session.add_all(
        [
            SourceContent(id="source", title="Source"),
            AccountProfile(id="account", name="Account", platform="Demo", details={"brand_safety_rules": ["No claims"]}),
            WorkflowRun(id="workflow", status="COMPLETED"),
            ClipCandidate(id="candidate", source_content_id="source", workflow_run_id="workflow", account_profile_id="account", start_seconds=0, end_seconds=10, duration_seconds=10, transcript_excerpt="Excerpt", reason_selected="Reason", confidence=0.5, status="DETECTED"),
        ]
    )
    session.commit()
    save_score(session, "candidate", ClipScoreSchema(hook_strength=4, standalone_clarity=4, novelty=3, emotional_intensity=3, shareability=3, educational_value=4, brand_safety=5, editing_complexity=2, confidence=0.8))
    for asset_type, count in REQUIRED_COUNTS.items():
        session.add_all(GeneratedAsset(id=f"{asset_type}-{index}", candidate_id="candidate", asset_type=asset_type, content="Draft") for index in range(count))
    session.commit()
    return session, session.get(ClipCandidate, "candidate")


def test_valid_candidate_moves_to_review() -> None:
    session, _ = candidate_session()
    assert mark_needs_review(session, "candidate").status == "NEEDS_REVIEW"


@pytest.mark.parametrize(
    ("change", "field"),
    [
        (lambda candidate, session: setattr(candidate, "end_seconds", 0), "timestamps"),
        (lambda candidate, session: session.query(GeneratedAsset).delete(), "assets"),
        (lambda candidate, session: save_score(session, "candidate", ClipScoreSchema(hook_strength=4, standalone_clarity=4, novelty=3, emotional_intensity=3, shareability=3, educational_value=4, brand_safety=2, editing_complexity=2, confidence=0.8)), "brand_safety"),
    ],
)
def test_invalid_candidate_cannot_reach_review(change, field: str) -> None:
    session, candidate = candidate_session()
    change(candidate, session)
    session.commit()
    with pytest.raises(BusinessRuleValidationError) as error:
        mark_needs_review(session, "candidate")
    assert any(violation.field == field for violation in error.value.violations)
