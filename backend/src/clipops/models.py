from __future__ import annotations

from enum import StrEnum

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CandidateStatus(StrEnum):
    DETECTED = "DETECTED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EDITING = "EDITING"
    READY_TO_PUBLISH = "READY_TO_PUBLISH"
    PUBLISHED = "PUBLISHED"


class SourceContent(Base):
    __tablename__ = "source_contents"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String)


class Transcript(Base):
    __tablename__ = "transcripts"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    source_content_id: Mapped[str] = mapped_column(ForeignKey("source_contents.id"))
    raw_text: Mapped[str] = mapped_column(Text)


class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    transcript_id: Mapped[str] = mapped_column(ForeignKey("transcripts.id"))
    start_seconds: Mapped[int] = mapped_column(Integer)
    end_seconds: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)


class ContentBrief(Base):
    __tablename__ = "content_briefs"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    objective: Mapped[str] = mapped_column(Text)
    details: Mapped[dict[str, object]] = mapped_column(JSON)


class AccountProfile(Base):
    __tablename__ = "account_profiles"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    platform: Mapped[str] = mapped_column(String)
    details: Mapped[dict[str, object]] = mapped_column(JSON)


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    status: Mapped[str] = mapped_column(String)


class ModelRun(Base):
    __tablename__ = "model_runs"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    workflow_run_id: Mapped[str] = mapped_column(ForeignKey("workflow_runs.id"))
    provider: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String)
    prompt_version: Mapped[str] = mapped_column(String)
    validation_result: Mapped[str] = mapped_column(String)
    repair_count: Mapped[int] = mapped_column(Integer, default=0)


class ClipCandidate(Base):
    __tablename__ = "clip_candidates"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    source_content_id: Mapped[str] = mapped_column(ForeignKey("source_contents.id"))
    workflow_run_id: Mapped[str] = mapped_column(ForeignKey("workflow_runs.id"))
    account_profile_id: Mapped[str] = mapped_column(ForeignKey("account_profiles.id"))
    start_seconds: Mapped[int] = mapped_column(Integer)
    end_seconds: Mapped[int] = mapped_column(Integer)
    duration_seconds: Mapped[int] = mapped_column(Integer)
    transcript_excerpt: Mapped[str] = mapped_column(Text)
    reason_selected: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String, default=CandidateStatus.DETECTED)


class ClipScore(Base):
    __tablename__ = "clip_scores"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("clip_candidates.id"), unique=True)
    hook_strength: Mapped[int] = mapped_column(Integer)
    standalone_clarity: Mapped[int] = mapped_column(Integer)
    novelty: Mapped[int] = mapped_column(Integer)
    emotional_intensity: Mapped[int] = mapped_column(Integer)
    shareability: Mapped[int] = mapped_column(Integer)
    educational_value: Mapped[int] = mapped_column(Integer)
    brand_safety: Mapped[int] = mapped_column(Integer)
    editing_complexity: Mapped[int] = mapped_column(Integer)
    overall_score: Mapped[int] = mapped_column(Integer)
    confidence: Mapped[float] = mapped_column(Float)
    explanation: Mapped[str] = mapped_column(Text)


class GeneratedAsset(Base):
    __tablename__ = "generated_assets"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("clip_candidates.id"))
    asset_type: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)


class ReviewDecision(Base):
    __tablename__ = "review_decisions"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("clip_candidates.id"))
    decision: Mapped[str] = mapped_column(String)
    reason: Mapped[str] = mapped_column(Text)


class PublishingQueueItem(Base):
    __tablename__ = "publishing_queue_items"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("clip_candidates.id"), unique=True)
    account_profile_id: Mapped[str] = mapped_column(ForeignKey("account_profiles.id"))
    status: Mapped[str] = mapped_column(String)


class PerformanceRecord(Base):
    __tablename__ = "performance_records"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    queue_item_id: Mapped[str] = mapped_column(ForeignKey("publishing_queue_items.id"))
    views: Mapped[int] = mapped_column(Integer)
    engagement_rate: Mapped[float] = mapped_column(Float)
    simulated: Mapped[bool] = mapped_column(default=True)


class ContentExperiment(Base):
    __tablename__ = "content_experiments"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    hypothesis: Mapped[str] = mapped_column(Text)
    primary_metric: Mapped[str] = mapped_column(String)


class WeeklyGrowthReport(Base):
    __tablename__ = "weekly_growth_reports"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    week_range: Mapped[str] = mapped_column(String)
    summary: Mapped[str] = mapped_column(Text)
    simulated: Mapped[bool] = mapped_column(default=True)
