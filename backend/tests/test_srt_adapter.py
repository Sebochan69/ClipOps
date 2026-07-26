from pathlib import Path

from clipops.srt_adapter import parse_srt
from clipops.transcript_parser import parse_transcript

FIXTURES = Path(__file__).parent / "fixtures"


def test_imports_srt_into_clipops_timestamp_format() -> None:
    result = parse_srt((FIXTURES / "demo.srt").read_text())
    assert result.issues == []
    assert result.blocks[1].text == "Second line continued."
    assert result.normalized_text == "[00:00:01] First line.\n[00:00:04] Second line continued."
    assert parse_transcript(result.normalized_text).issues == []


def test_reports_malformed_srt() -> None:
    result = parse_srt((FIXTURES / "malformed.srt").read_text())
    assert result.blocks == []
    assert result.issues[0].line_number == 1
    assert "sequence number" in result.issues[0].suggested_action
