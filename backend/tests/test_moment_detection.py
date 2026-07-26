import pytest
from pydantic import ValidationError

from clipops.moment_detection import MomentDetectionOutput


def test_malformed_model_output_is_rejected() -> None:
    with pytest.raises(ValidationError):
        MomentDetectionOutput.model_validate(
            {"candidates": [{"start_seconds": 10, "end_seconds": 5, "transcript_excerpt": "bad", "reason_selected": "bad"}] * 6}
        )
