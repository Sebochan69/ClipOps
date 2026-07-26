from pydantic import BaseModel, Field

from clipops.models import CandidateStatus


class SourceContentSchema(BaseModel):
    id: str
    title: str


class TranscriptSchema(BaseModel):
    id: str
    source_content_id: str
    raw_text: str


class TranscriptSegmentSchema(BaseModel):
    id: str
    transcript_id: str
    start_seconds: int = Field(ge=0)
    end_seconds: int = Field(ge=0)
    text: str


class TranscriptValidationRequest(BaseModel):
    transcript_id: str
    source_content_id: str
    source_title: str
    raw_text: str


class ContentBriefSchema(BaseModel):
    id: str
    name: str
    objective: str
    target_audience: str
    topic_angle: str
    desired_formats: list[str]
    must_include: list[str] = []
    must_avoid: list[str] = []
    tone: str
    cta_goal: str
    brand_safety_notes: str


class AccountProfileSchema(BaseModel):
    id: str
    name: str
    platform: str
    niche: str
    audience: str
    voice: str
    content_pillars: list[str]
    format_preferences: list[str]
    risk_tolerance: str
    cta_style: str
    brand_safety_rules: list[str]
    historical_notes: str


class WorkflowRunSchema(BaseModel):
    id: str
    status: str


class ModelRunSchema(BaseModel):
    id: str
    workflow_run_id: str
    provider: str
    model: str
    prompt_version: str
    validation_result: str
    repair_count: int = Field(ge=0)


class ClipScoreSchema(BaseModel):
    hook_strength: int = Field(ge=1, le=5)
    standalone_clarity: int = Field(ge=1, le=5)
    novelty: int = Field(ge=1, le=5)
    emotional_intensity: int = Field(ge=1, le=5)
    shareability: int = Field(ge=1, le=5)
    educational_value: int = Field(ge=1, le=5)
    brand_safety: int = Field(ge=1, le=5)
    editing_complexity: int = Field(ge=1, le=5)
    overall_score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    explanation: str


class ClipCandidateSchema(BaseModel):
    id: str
    source_content_id: str
    workflow_run_id: str
    account_profile_id: str
    start_seconds: int = Field(ge=0)
    end_seconds: int = Field(ge=0)
    duration_seconds: int = Field(gt=0)
    transcript_excerpt: str
    reason_selected: str
    confidence: float = Field(ge=0, le=1)
    status: CandidateStatus = CandidateStatus.DETECTED


class GeneratedAssetSchema(BaseModel):
    id: str
    candidate_id: str
    asset_type: str
    content: str


class ReviewDecisionSchema(BaseModel):
    id: str
    candidate_id: str
    decision: str
    reason: str


class PublishingQueueItemSchema(BaseModel):
    id: str
    candidate_id: str
    account_profile_id: str
    status: str


class PerformanceRecordSchema(BaseModel):
    id: str
    queue_item_id: str
    views: int = Field(ge=0)
    engagement_rate: float = Field(ge=0)
    simulated: bool = True


class ContentExperimentSchema(BaseModel):
    id: str
    name: str
    hypothesis: str
    primary_metric: str


class WeeklyGrowthReportSchema(BaseModel):
    id: str
    week_range: str
    summary: str
    simulated: bool = True
