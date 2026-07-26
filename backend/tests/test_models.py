import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, inspect

from clipops.models import Base
from clipops.schemas import ClipScoreSchema


def test_models_create_sqlite_tables() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    assert {"source_contents", "clip_candidates", "weekly_growth_reports"} <= set(
        inspect(engine).get_table_names()
    )
    Base.metadata.drop_all(engine)


def test_clip_score_schema_validates_ranges() -> None:
    score = ClipScoreSchema(
        hook_strength=5,
        standalone_clarity=4,
        novelty=3,
        emotional_intensity=4,
        shareability=3,
        educational_value=5,
        brand_safety=5,
        editing_complexity=2,
        overall_score=82,
        confidence=0.8,
        explanation="Clear practical takeaway.",
    )
    assert score.overall_score == 82

    with pytest.raises(ValidationError):
        ClipScoreSchema(**{**score.model_dump(), "hook_strength": 6})
