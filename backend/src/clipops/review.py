from uuid import uuid4

from sqlalchemy.orm import Session

from clipops.business_validation import mark_needs_review
from clipops.models import ClipCandidate, ReviewDecision


class InvalidStateTransitionError(ValueError):
    code = "INVALID_STATE_TRANSITION"


def review_candidate(session: Session, candidate_id: str, action: str, reason: str = "") -> ClipCandidate:
    candidate = session.get(ClipCandidate, candidate_id)
    if not candidate:
        raise InvalidStateTransitionError("Candidate was not found.")
    if action == "SUBMIT_FOR_REVIEW" and candidate.status == "DETECTED":
        return mark_needs_review(session, candidate_id)
    transitions = {
        ("NEEDS_REVIEW", "APPROVE"): "APPROVED",
        ("NEEDS_REVIEW", "REJECT"): "REJECTED",
        ("NEEDS_REVIEW", "EDIT"): "EDITING",
        ("APPROVED", "EDIT"): "EDITING",
    }
    status = transitions.get((candidate.status, action))
    if not status:
        raise InvalidStateTransitionError(f"Cannot {action.lower()} a candidate in {candidate.status}.")
    if action == "REJECT" and not reason:
        raise InvalidStateTransitionError("A rejection reason is required.")
    candidate.status = status
    session.add(ReviewDecision(id=str(uuid4()), candidate_id=candidate_id, decision=action, reason=reason or action,))
    session.commit()
    return candidate
