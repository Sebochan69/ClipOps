import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from clipops.main import app
from clipops.models import Transcript


def transcript_lines() -> str:
    return "\n".join(f"[00:{second:02d}] line {second}" for second in range(10))


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


def test_valid_transcript_is_persisted(client: TestClient) -> None:
    response = client.post("/transcripts/validate", json=payload(transcript_lines()))
    assert response.json() == {"transcript_id": "transcript-1", "line_count": 10, "warnings": []}
    with Session(app.state.engine) as session:
        assert session.get(Transcript, "transcript-1") is not None


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
