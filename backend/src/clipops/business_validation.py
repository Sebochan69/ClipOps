from collections import Counter
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from clipops.asset_generation import REQUIRED_COUNTS
from clipops.models import AccountProfile, ClipCandidate, ClipScore, GeneratedAsset

MIN_DURATION_SECONDS = 1
MAX_DURATION_SECONDS = 90
MIN_BRAND_SAFETY_SCORE = 3


@dataclass(frozen=True)
class BusinessRuleViolation:
    field: str
    message: str


class BusinessRuleValidationError(ValueError):
    code = "BUSINESS_RULE_VALIDATION_ERROR"

    def __init__(self, violations: list[BusinessRuleViolation]):
        super().__init__("Candidate failed business-rule validation.")
        self.violations = violations


def validate_candidate_for_review(session: Session, candidate_id: str) -> None:
    candidate = session.get(ClipCandidate, candidate_id)
    violations: list[BusinessRuleViolation] = []
    if not candidate:
        raise BusinessRuleValidationError([BusinessRuleViolation("candidate_id", "Candidate was not found.")])
    if candidate.end_seconds <= candidate.start_seconds or candidate.duration_seconds != candidate.end_seconds - candidate.start_seconds:
        violations.append(BusinessRuleViolation("timestamps", "Timestamp range and duration must agree."))
    if not MIN_DURATION_SECONDS <= candidate.duration_seconds <= MAX_DURATION_SECONDS:
        violations.append(BusinessRuleViolation("duration_seconds", "Duration must be between 1 and 90 seconds."))
    score = session.scalar(select(ClipScore).where(ClipScore.candidate_id == candidate_id))
    if not score or score.brand_safety < MIN_BRAND_SAFETY_SCORE:
        violations.append(BusinessRuleViolation("brand_safety", "Brand-safety score must be at least 3."))
    account = session.get(AccountProfile, candidate.account_profile_id)
    if not account or not account.details.get("brand_safety_rules"):
        violations.append(BusinessRuleViolation("brand_safety_rules", "Account profile needs brand-safety rules."))
    assets = session.scalars(select(GeneratedAsset).where(GeneratedAsset.candidate_id == candidate_id)).all()
    if Counter(asset.asset_type for asset in assets) != REQUIRED_COUNTS:
        violations.append(BusinessRuleViolation("assets", "Candidate is missing required generated assets."))
    if violations:
        raise BusinessRuleValidationError(violations)


def mark_needs_review(session: Session, candidate_id: str) -> ClipCandidate:
    validate_candidate_for_review(session, candidate_id)
    candidate = session.get(ClipCandidate, candidate_id)
    if candidate is None:
        raise BusinessRuleValidationError([BusinessRuleViolation("candidate_id", "Candidate was not found.")])
    candidate.status = "NEEDS_REVIEW"
    session.commit()
    return candidate
