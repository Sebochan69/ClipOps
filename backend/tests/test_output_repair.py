import pytest
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from clipops.model_provider import MockModelProvider
from clipops.models import Base, ModelRun, WorkflowRun
from clipops.output_repair import (
    ModelOutputRepairFailed,
    validate_and_record,
    validate_with_one_repair,
)


class Output(BaseModel):
    value: int = Field(ge=1)


def validate(raw: object) -> Output:
    return Output.model_validate(raw)


def test_malformed_output_is_repaired_once() -> None:
    result = validate_with_one_repair({"value": 0}, validate, lambda _: {"value": 1})
    assert result.value == Output(value=1)
    assert result.repair_count == 1


def test_malformed_output_fails_after_one_repair() -> None:
    with pytest.raises(ModelOutputRepairFailed):
        validate_with_one_repair({"value": 0}, validate, lambda value: value)


def test_repair_count_is_recorded() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(WorkflowRun(id="workflow", status="COMPLETED"))
        session.commit()
        validate_and_record(session, "workflow", MockModelProvider(), "test-v1", {"value": 0}, validate, lambda _: {"value": 1})
        run = session.scalar(select(ModelRun).where(ModelRun.workflow_run_id == "workflow"))
        assert run and run.repair_count == 1 and run.validation_result == "REPAIRED"
