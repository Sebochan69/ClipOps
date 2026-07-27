import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from clipops.main import app
from clipops.models import Transcript


def transcript_lines() -> str:
    return "\n".join(f"[00:{second:02d}] line {second}" for second in range(10))


def srt_lines() -> str:
    return "\n\n".join(
        f"{index + 1}\n00:00:{index:02d},000 --> 00:00:{index + 1:02d},000\nline {index}"
        for index in range(10)
    )


@pytest.fixture
def client(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    app.state.engine = engine
    yield TestClient(app)
    app.state.engine = None


def payload(raw_text: str) -> dict[str, str]:
    return {
        "transcript_id": "transcript-1",
        "source_content_id": "source-1",
        "source_title": "Demo source",
        "raw_text": raw_text,
    }


def test_frontend_origin_is_allowed(client: TestClient) -> None:
    response = client.options(
        "/transcripts/validate",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"},
    )
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_valid_transcript_is_persisted(client: TestClient) -> None:
    response = client.post("/transcripts/validate", json=payload(transcript_lines()))
    assert response.json() == {"transcript_id": "transcript-1", "line_count": 10, "warnings": []}
    with Session(app.state.engine) as session:
        assert session.get(Transcript, "transcript-1") is not None


def test_srt_transcript_is_normalized_and_persisted(client: TestClient) -> None:
    response = client.post("/transcripts/validate", json=payload(srt_lines()))
    assert response.json() == {"transcript_id": "transcript-1", "line_count": 10, "warnings": []}
    with Session(app.state.engine) as session:
        transcript = session.get(Transcript, "transcript-1")
        assert transcript is not None
        assert transcript.raw_text.startswith("[00:00:00] line 0")


def test_segments_are_available_after_validation(client: TestClient) -> None:
    client.post("/transcripts/validate", json=payload(transcript_lines()))
    response = client.get("/transcripts/transcript-1/segments")
    assert response.status_code == 200
    assert response.json()[0]["text"] == "line 0\nline 1\nline 2\nline 3\nline 4\nline 5\nline 6\nline 7\nline 8\nline 9"


def test_missing_transcript_segments_returns_not_found(client: TestClient) -> None:
    response = client.get("/transcripts/missing/segments")
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


def test_large_gap_returns_warning(client: TestClient) -> None:
    raw_text = "\n".join(["[00:00] first"] + [f"[02:{second:02d}] line" for second in range(10, 19)])
    response = client.post("/transcripts/validate", json=payload(raw_text))
    assert "Gap of 130 seconds" in response.json()["warnings"][0]


@pytest.mark.parametrize(
    ("raw_text", "code"),
    [
        ("[00:00] only one", "TRANSCRIPT_VALIDATION_ERROR"),
        ("[00:00] valid\nno timestamp", "TRANSCRIPT_PARSE_ERROR"),
        ("\n".join(["[00:10] first", "[00:09] second"] + [f"[00:{i:02d}] line" for i in range(10, 18)]), "TRANSCRIPT_VALIDATION_ERROR"),
    ],
)
def test_invalid_transcripts_return_typed_error(client: TestClient, raw_text: str, code: str) -> None:
    response = client.post("/transcripts/validate", json=payload(raw_text))
    assert response.status_code == 422
    assert response.json()["code"] == code
