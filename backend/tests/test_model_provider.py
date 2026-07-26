from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from clipops.model_provider import MockModelProvider, SegmentInput, record_model_run
from clipops.models import Base, WorkflowRun


def test_mock_provider_is_deterministic() -> None:
    provider = MockModelProvider()
    segments = [SegmentInput(0, 30, "A useful point.")]
    assert provider.detect_moments(segments) == provider.detect_moments(segments)


def test_model_run_is_persisted() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(WorkflowRun(id="workflow", status="COMPLETE"))
        session.commit()
        run = record_model_run(session, "workflow", MockModelProvider(), "moment-detection-v1", "VALID")
        assert run.provider == "mock"
        assert session.get(type(run), run.id).prompt_version == "moment-detection-v1"
