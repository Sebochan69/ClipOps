import pytest
from pydantic import ValidationError

from clipops.asset_generation import AssetGenerationOutput
from clipops.model_provider import CandidateInput, MockModelProvider


def test_mock_output_has_required_assets() -> None:
    assets = MockModelProvider().generate_assets(CandidateInput("Useful excerpt"))
    output = AssetGenerationOutput.model_validate({"assets": [asset.__dict__ for asset in assets]})
    assert len(output.assets) == 9


def test_malformed_asset_output_is_rejected() -> None:
    with pytest.raises(ValidationError):
        AssetGenerationOutput.model_validate({"assets": [{"asset_type": "hook", "content": "Only one"}]})
