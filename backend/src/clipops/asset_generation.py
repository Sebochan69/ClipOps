from collections import Counter
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator
from sqlalchemy import delete
from sqlalchemy.orm import Session

from clipops.model_provider import AssetDraft, CandidateInput, ModelProvider
from clipops.models import ClipCandidate, GeneratedAsset

PROMPT_VERSION = "asset-generation-v1"
REQUIRED_COUNTS = {"hook": 3, "title": 2, "caption": 2, "cta": 1, "editing_note": 1}


class GeneratedAssetOutput(BaseModel):
    asset_type: str
    content: str = Field(min_length=1)


class AssetGenerationOutput(BaseModel):
    assets: list[GeneratedAssetOutput]

    @model_validator(mode="after")
    def required_assets_present(self) -> "AssetGenerationOutput":
        if Counter(asset.asset_type for asset in self.assets) != REQUIRED_COUNTS:
            raise ValueError("assets must include 3 hooks, 2 titles, 2 captions, 1 CTA, and 1 editing note")
        return self


def validate_asset_output(assets: list[AssetDraft]) -> AssetGenerationOutput:
    return AssetGenerationOutput.model_validate({"assets": [asset.__dict__ for asset in assets]})


def save_assets(session: Session, candidate_id: str, output: AssetGenerationOutput) -> list[GeneratedAsset]:
    session.execute(delete(GeneratedAsset).where(GeneratedAsset.candidate_id == candidate_id))
    assets = [
        GeneratedAsset(id=str(uuid4()), candidate_id=candidate_id, asset_type=asset.asset_type, content=asset.content)
        for asset in output.assets
    ]
    session.add_all(assets)
    session.commit()
    return assets


def generate_candidate_assets(session: Session, candidate: ClipCandidate, provider: ModelProvider) -> list[GeneratedAsset]:
    output = validate_asset_output(provider.generate_assets(CandidateInput(candidate.transcript_excerpt)))
    return save_assets(session, candidate.id, output)
