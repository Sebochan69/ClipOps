from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic import ValidationError
from sqlalchemy.orm import Session

from clipops.model_provider import ModelProvider, record_model_run

T = TypeVar("T")


class ModelOutputSchemaError(ValueError):
    code = "MODEL_OUTPUT_SCHEMA_ERROR"


class ModelOutputRepairFailed(ValueError):
    code = "MODEL_OUTPUT_REPAIR_FAILED"


@dataclass(frozen=True)
class RepairResult(Generic[T]):
    value: T
    repair_count: int


def validate_with_one_repair(
    raw_output: object,
    validate: Callable[[object], T],
    repair: Callable[[object], object],
) -> RepairResult[T]:
    try:
        return RepairResult(validate(raw_output), 0)
    except (ValidationError, ValueError):
        try:
            return RepairResult(validate(repair(raw_output)), 1)
        except (ValidationError, ValueError) as error:
            raise ModelOutputRepairFailed("Model output remained invalid after one repair.") from error


def validate_and_record(
    session: Session,
    workflow_run_id: str,
    provider: ModelProvider,
    prompt_version: str,
    raw_output: object,
    validate: Callable[[object], T],
    repair: Callable[[object], object],
) -> RepairResult[T]:
    result = validate_with_one_repair(raw_output, validate, repair)
    record_model_run(
        session,
        workflow_run_id,
        provider,
        prompt_version,
        "REPAIRED" if result.repair_count else "VALID",
        repair_count=result.repair_count,
    )
    return result
