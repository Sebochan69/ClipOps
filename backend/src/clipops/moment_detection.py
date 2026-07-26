from uuid import uuid4

from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from clipops.model_provider import MomentDraft
from clipops.models import CandidateStatus, ClipCandidate

PROMPT_VERSION = "moment-detection-v1"


class MomentCandidateOutput(BaseModel):
    start_seconds: int = Field(ge=0)
    end_seconds: int = Field(gt=0)
    transcript_excerpt: str = Field(min_length=1)
    reason_selected: str = Field(min_length=1)

    @model_validator(mode="after")
    def end_follows_start(self) -> "MomentCandidateOutput":
        if self.end_seconds <= self.start_seconds:
            raise ValueError("end_seconds must follow start_seconds")
        return self


class MomentDetectionOutput(BaseModel):
    candidates: list[MomentCandidateOutput] = Field(min_length=6)


def validate_moment_output(moments: list[MomentDraft]) -> MomentDetectionOutput:
    return MomentDetectionOutput.model_validate(
        {"candidates": [moment.__dict__ for moment in moments]}
    )


def create_candidates(
    session: Session,
    workflow_run_id: str,
    source_content_id: str,
    account_profile_id: str,
    output: MomentDetectionOutput,
) -> list[ClipCandidate]:
    candidates = [
        ClipCandidate(
            id=str(uuid4()),
            source_content_id=source_content_id,
            workflow_run_id=workflow_run_id,
            account_profile_id=account_profile_id,
            start_seconds=moment.start_seconds,
            end_seconds=moment.end_seconds,
            duration_seconds=moment.end_seconds - moment.start_seconds,
            transcript_excerpt=moment.transcript_excerpt,
            reason_selected=moment.reason_selected,
            confidence=0.5,
            status=CandidateStatus.DETECTED,
        )
        for moment in output.candidates
    ]
    session.add_all(candidates)
    session.commit()
    return candidates
