from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from clipops.database import make_engine
from clipops.models import (
    AccountProfile,
    Base,
    ClipCandidate,
    ClipScore,
    GeneratedAsset,
    PerformanceRecord,
    PublishingQueueItem,
    SourceContent,
    Transcript,
    TranscriptSegment,
    WorkflowRun,
)
from clipops.review import InvalidStateTransitionError, review_candidate
from clipops.schemas import (
    AssetUpdateRequest,
    PerformanceImportRequest,
    QueueRequest,
    ReviewRequest,
    TranscriptValidationRequest,
)
from clipops.segmentation import persist_segments
from clipops.transcript_validation import validate_transcript

app = FastAPI(title="ClipOps API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "PATCH", "POST"],
    allow_headers=["Content-Type"],
)
app.state.engine = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def error(code: str, message: str, field: str, suggested_action: str, details: list[dict[str, object]], status_code: int = 422) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"code": code, "message": message, "field": field, "suggested_action": suggested_action, "details": details},
    )


@app.post("/transcripts/validate", response_model=None)
def validate(request: TranscriptValidationRequest) -> dict[str, object] | JSONResponse:
    engine: Engine = app.state.engine or make_engine()
    Base.metadata.create_all(engine)
    result = validate_transcript(request.raw_text)
    if result.issues:
        code = "TRANSCRIPT_PARSE_ERROR" if any(issue.line_number and "Invalid" in issue.message for issue in result.issues) else "TRANSCRIPT_VALIDATION_ERROR"
        return error(
            code,
            "Transcript could not be validated.",
            "raw_text",
            "Fix the reported lines and submit again.",
            [{"line_number": issue.line_number, "message": issue.message, "suggested_action": issue.suggested_action} for issue in result.issues],
        )
    with Session(engine) as session:
        if not session.get(SourceContent, request.source_content_id):
            session.add(SourceContent(id=request.source_content_id, title=request.source_title))
        transcript = session.get(Transcript, request.transcript_id)
        if transcript:
            transcript.source_content_id = request.source_content_id
            transcript.raw_text = request.raw_text
        else:
            session.add(Transcript(id=request.transcript_id, source_content_id=request.source_content_id, raw_text=request.raw_text))
        session.flush()
        persist_segments(session, request.transcript_id, request.raw_text)
    return {"transcript_id": request.transcript_id, "line_count": len(result.lines), "warnings": result.warnings}


@app.post("/performance-records", response_model=None)
def import_performance(request: PerformanceImportRequest) -> object:
    engine: Engine = app.state.engine or make_engine()
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        queue_item = session.get(PublishingQueueItem, request.queue_item_id)
        if not queue_item:
            return error("SIMULATED_DATA_IMPORT_ERROR", "Queue item was not found.", "queue_item_id", "Queue an approved candidate before importing metrics.", [], 422)
        record = PerformanceRecord(id=f"performance:{request.queue_item_id}", queue_item_id=request.queue_item_id, views=request.views, engagement_rate=request.engagement_rate, simulated=True)
        session.merge(record)
        candidate = session.get(ClipCandidate, queue_item.candidate_id)
        if candidate:
            candidate.status = "PUBLISHED"
        session.commit()
        response = {"performance_record_id": record.id, "simulated": True}
    return response


@app.get("/publishing-queue", response_model=None)
def list_publishing_queue() -> object:
    engine: Engine = app.state.engine or make_engine()
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        rows = session.execute(
            select(PublishingQueueItem, ClipCandidate, AccountProfile)
            .join(ClipCandidate, ClipCandidate.id == PublishingQueueItem.candidate_id)
            .join(AccountProfile, AccountProfile.id == PublishingQueueItem.account_profile_id)
            .order_by(PublishingQueueItem.scheduled_for)
        ).all()
    return [
        {"queue_item_id": item.id, "status": item.status, "scheduled_for": item.scheduled_for, "account": account.name, "platform": account.platform, "candidate_excerpt": candidate.transcript_excerpt}
        for item, candidate, account in rows
    ]


@app.post("/candidates/{candidate_id}/queue", response_model=None)
def queue_candidate(candidate_id: str, request: QueueRequest) -> object:
    engine: Engine = app.state.engine or make_engine()
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        candidate = session.get(ClipCandidate, candidate_id)
        if not candidate or candidate.status != "APPROVED":
            return error("BUSINESS_RULE_VALIDATION_ERROR", "Only approved candidates can be queued.", "candidate_id", "Approve the candidate before queueing.", [], 422)
        item = PublishingQueueItem(id=f"queue:{candidate_id}", candidate_id=candidate_id, account_profile_id=candidate.account_profile_id, status="QUEUED", scheduled_for=request.scheduled_for)
        session.add(item)
        candidate.status = "READY_TO_PUBLISH"
        session.commit()
        response = {"queue_item_id": item.id, "status": item.status}
    return response


@app.post("/candidates/{candidate_id}/review", response_model=None)
def review(candidate_id: str, request: ReviewRequest) -> object:
    engine: Engine = app.state.engine or make_engine()
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        try:
            candidate = review_candidate(session, candidate_id, request.action, request.reason)
        except InvalidStateTransitionError as error_message:
            return error("INVALID_STATE_TRANSITION", str(error_message), "action", "Use a valid lifecycle action.", [], 422)
        response = {"candidate_id": candidate.id, "status": candidate.status}
    return response


@app.get("/candidates/{candidate_id}", response_model=None)
def get_candidate(candidate_id: str) -> object:
    engine: Engine = app.state.engine or make_engine()
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        candidate = session.get(ClipCandidate, candidate_id)
        if not candidate:
            return error("NOT_FOUND", "Candidate was not found.", "candidate_id", "Select a candidate from a workflow run.", [], 404)
        score = session.scalar(select(ClipScore).where(ClipScore.candidate_id == candidate_id))
        assets = session.scalars(select(GeneratedAsset).where(GeneratedAsset.candidate_id == candidate_id).order_by(GeneratedAsset.asset_type)).all()
    return {
        "candidate_id": candidate.id,
        "start_seconds": candidate.start_seconds,
        "end_seconds": candidate.end_seconds,
        "duration_seconds": candidate.duration_seconds,
        "transcript_excerpt": candidate.transcript_excerpt,
        "reason_selected": candidate.reason_selected,
        "confidence": candidate.confidence,
        "status": candidate.status,
        "scores": score and {name: getattr(score, name) for name in ("hook_strength", "standalone_clarity", "novelty", "emotional_intensity", "shareability", "educational_value", "brand_safety", "editing_complexity", "overall_score", "confidence", "explanation")},
        "assets": [{"id": asset.id, "asset_type": asset.asset_type, "content": asset.content} for asset in assets],
    }


@app.patch("/candidates/{candidate_id}/assets/{asset_id}", response_model=None)
def update_asset(candidate_id: str, asset_id: str, request: AssetUpdateRequest) -> object:
    engine: Engine = app.state.engine or make_engine()
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        asset = session.get(GeneratedAsset, asset_id)
        if not asset or asset.candidate_id != candidate_id:
            return error("NOT_FOUND", "Generated asset was not found.", "asset_id", "Load a candidate and select one of its assets.", [], 404)
        asset.content = request.content
        session.commit()
    return {"id": asset_id, "content": request.content}


@app.get("/workflow-runs/{workflow_run_id}/candidates", response_model=None)
def list_candidates(workflow_run_id: str, status: str | None = None) -> object:
    engine: Engine = app.state.engine or make_engine()
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        if not session.get(WorkflowRun, workflow_run_id):
            return error("NOT_FOUND", "Workflow run was not found.", "workflow_run_id", "Run a workflow before viewing candidates.", [], 404)
        query = select(ClipCandidate, ClipScore).outerjoin(ClipScore, ClipScore.candidate_id == ClipCandidate.id).where(
            ClipCandidate.workflow_run_id == workflow_run_id
        )
        if status:
            query = query.where(ClipCandidate.status == status)
        rows = session.execute(query).all()
    rows.sort(key=lambda row: row[1].overall_score if row[1] else -1, reverse=True)
    return [
        {
            "candidate_id": candidate.id,
            "start_seconds": candidate.start_seconds,
            "end_seconds": candidate.end_seconds,
            "duration_seconds": candidate.duration_seconds,
            "transcript_excerpt": candidate.transcript_excerpt,
            "reason_selected": candidate.reason_selected,
            "confidence": candidate.confidence,
            "status": candidate.status,
            "scores": {"overall_score": score.overall_score, "explanation": score.explanation} if score else None,
            "assets": [],
        }
        for candidate, score in rows
    ]


@app.get("/transcripts/{transcript_id}/segments", response_model=None)
def list_segments(transcript_id: str) -> object:
    engine: Engine = app.state.engine or make_engine()
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        if not session.get(Transcript, transcript_id):
            return error("NOT_FOUND", "Transcript was not found.", "transcript_id", "Validate a transcript before viewing segments.", [], 404)
        segments = session.scalars(
            select(TranscriptSegment).where(TranscriptSegment.transcript_id == transcript_id).order_by(TranscriptSegment.start_seconds)
        ).all()
    return [
        {"id": segment.id, "start_seconds": segment.start_seconds, "end_seconds": segment.end_seconds, "text": segment.text}
        for segment in segments
    ]
