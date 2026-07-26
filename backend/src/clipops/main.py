from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from clipops.database import make_engine
from clipops.models import (
    Base,
    ClipCandidate,
    ClipScore,
    SourceContent,
    Transcript,
    TranscriptSegment,
    WorkflowRun,
)
from clipops.schemas import TranscriptValidationRequest
from clipops.segmentation import persist_segments
from clipops.transcript_validation import validate_transcript

app = FastAPI(title="ClipOps API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
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
