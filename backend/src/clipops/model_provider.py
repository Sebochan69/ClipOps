from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol
from uuid import uuid4

from sqlalchemy.orm import Session

from clipops.models import ModelRun


@dataclass(frozen=True)
class SegmentInput:
    start_seconds: int
    end_seconds: int
    text: str


@dataclass(frozen=True)
class MomentDraft:
    start_seconds: int
    end_seconds: int
    transcript_excerpt: str
    reason_selected: str


class ModelProvider(Protocol):
    provider_name: str
    model_name: str

    def detect_moments(self, segments: Sequence[SegmentInput]) -> list[MomentDraft]: ...


class MockModelProvider:
    provider_name = "mock"
    model_name = "deterministic-v1"

    def detect_moments(self, segments: Sequence[SegmentInput]) -> list[MomentDraft]:
        return [
            MomentDraft(
                start_seconds=segment.start_seconds,
                end_seconds=segment.end_seconds,
                transcript_excerpt=segment.text,
                reason_selected="Deterministic demo selection from a transcript segment.",
            )
            for segment in segments
        ]


def record_model_run(
    session: Session,
    workflow_run_id: str,
    provider: ModelProvider,
    prompt_version: str,
    validation_result: str,
    raw_output_reference: str | None = None,
    repair_count: int = 0,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    estimated_cost: float | None = None,
) -> ModelRun:
    run = ModelRun(
        id=str(uuid4()),
        workflow_run_id=workflow_run_id,
        provider=provider.provider_name,
        model=provider.model_name,
        prompt_version=prompt_version,
        validation_result=validation_result,
        repair_count=repair_count,
        raw_output_reference=raw_output_reference,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost=estimated_cost,
    )
    session.add(run)
    session.commit()
    return run
