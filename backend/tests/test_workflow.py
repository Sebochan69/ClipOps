from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from clipops.models import (
    AccountProfile,
    Base,
    ClipCandidate,
    ModelRun,
    SourceContent,
    WorkflowRun,
)
from clipops.workflow import run_workflow


def valid_transcript() -> str:
    return "\n".join(f"[00:{second:02d}] line {second}" for second in range(10))


def test_workflow_runs_with_mock_provider() -> None:
    engine = create_engine("sqlite://")
    result = run_workflow(engine, valid_transcript())
    assert result["status"] == "COMPLETED"
    assert len(result["moments"]) == 6
    with Session(engine) as session:
        assert session.scalar(select(ModelRun).where(ModelRun.workflow_run_id == result["workflow_run_id"])) is not None


def test_workflow_creates_six_candidates() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(SourceContent(id="source", title="Source"))
        session.add(AccountProfile(id="account", name="Account", platform="Demo", details={}))
        session.commit()
    result = run_workflow(engine, valid_transcript(), source_content_id="source", account_profile_id="account")
    with Session(engine) as session:
        assert len(session.scalars(select(ClipCandidate).where(ClipCandidate.workflow_run_id == result["workflow_run_id"])).all()) == 6


def test_workflow_records_failed_validation() -> None:
    engine = create_engine("sqlite://")
    result = run_workflow(engine, "[00:00] too short")
    assert result["status"] == "FAILED"
    with Session(engine) as session:
        run = session.get(WorkflowRun, result["workflow_run_id"])
        assert run and run.error_message == "Transcript needs at least 10 timestamped lines."
