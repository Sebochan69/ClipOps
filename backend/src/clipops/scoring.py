from sqlalchemy import select
from sqlalchemy.orm import Session

from clipops.models import ClipCandidate, ClipScore
from clipops.schemas import ClipScoreSchema

WEIGHTS = {
    "hook_strength": 0.20,
    "standalone_clarity": 0.15,
    "novelty": 0.10,
    "emotional_intensity": 0.10,
    "shareability": 0.15,
    "educational_value": 0.10,
    "brand_safety": 0.15,
    "editing_complexity": 0.05,
}


def calculate_score(score: ClipScoreSchema) -> ClipScoreSchema:
    values = score.model_dump()
    weighted = sum(
        (6 - values[name] if name == "editing_complexity" else values[name]) * weight
        for name, weight in WEIGHTS.items()
    )
    strongest = max((name for name in WEIGHTS if name != "editing_complexity"), key=lambda name: values[name])
    return score.model_copy(
        update={
            "overall_score": round(weighted / 5 * 100),
            "explanation": f"Strongest dimension: {strongest.replace('_', ' ')}.",
        }
    )


def save_score(session: Session, candidate_id: str, score: ClipScoreSchema) -> ClipScore:
    calculated = calculate_score(score)
    record = session.scalar(select(ClipScore).where(ClipScore.candidate_id == candidate_id))
    fields = calculated.model_dump()
    if record is None:
        record = ClipScore(id=f"score:{candidate_id}", candidate_id=candidate_id, **fields)
        session.add(record)
    else:
        for name, value in fields.items():
            setattr(record, name, value)
    candidate = session.get(ClipCandidate, candidate_id)
    if candidate:
        candidate.confidence = calculated.confidence
    session.commit()
    return record
