from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from clipops.database import make_engine
from clipops.models import Base, SourceContent, Transcript
from clipops.schemas import TranscriptValidationRequest
from clipops.transcript_validation import validate_transcript

app = FastAPI(title="ClipOps API")
app.state.engine = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def error(code: str, message: str, field: str, suggested_action: str, details: list[dict[str, object]]) -> JSONResponse:
    return JSONResponse(
        status_code=422,
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
        session.commit()
    return {"transcript_id": request.transcript_id, "line_count": len(result.lines), "warnings": result.warnings}
