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


@dataclass(frozen=True)
class CandidateInput:
    transcript_excerpt: str


@dataclass(frozen=True)
class AssetDraft:
    asset_type: str
    content: str


class ModelProvider(Protocol):
    provider_name: str
    model_name: str

    def detect_moments(self, segments: Sequence[SegmentInput]) -> list[MomentDraft]: ...

    def generate_assets(self, candidate: CandidateInput) -> list[AssetDraft]: ...


class MockModelProvider:
    provider_name = "mock"
    model_name = "deterministic-v1"

    def detect_moments(self, segments: Sequence[SegmentInput]) -> list[MomentDraft]:
        if not segments:
            return []
        moments: list[MomentDraft] = []
        for index in range(6):
            segment = segments[index % len(segments)]
            start_seconds = min(segment.end_seconds - 1, segment.start_seconds + index)
            moments.append(
                MomentDraft(
                    start_seconds=start_seconds,
                    end_seconds=max(start_seconds + 1, segment.end_seconds),
                    transcript_excerpt=segment.text,
                    reason_selected="Deterministic demo selection from a transcript segment.",
                )
            )
        return moments

    def generate_assets(self, candidate: CandidateInput) -> list[AssetDraft]:
        excerpt = candidate.transcript_excerpt[:60]
        return [
            *(AssetDraft("hook", f"Hook {number}: {excerpt}") for number in range(1, 4)),
            *(AssetDraft("title", f"Title {number}: Practical takeaway") for number in range(1, 3)),
            *(AssetDraft("caption", f"Caption {number}: {excerpt}") for number in range(1, 3)),
            AssetDraft("cta", "Save this practical idea for later."),
            AssetDraft("editing_note", "Use concise text overlays for the key takeaway."),
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
