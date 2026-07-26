import pytest

from clipops.transcript_parser import parse_transcript, timestamp_to_seconds


def test_parses_supported_timestamp_formats() -> None:
    result = parse_transcript(
        "[00:01:23] first\n00:01:24 - second\n[01:02] third\n01:03 fourth"
    )
    assert result.issues == []
    assert [line.timestamp_seconds for line in result.lines] == [83, 84, 62, 63]
    assert result.lines[0].raw_line == "[00:01:23] first"


def test_reports_malformed_lines_with_line_number() -> None:
    result = parse_transcript("[00:00] valid\nno timestamp\n[00:61] invalid")
    assert [issue.line_number for issue in result.issues] == [2, 3]
    assert "Use" in result.issues[0].suggested_action


@pytest.mark.parametrize(("timestamp", "seconds"), [("01:02", 62), ("02:01:02", 7262)])
def test_timestamp_conversion(timestamp: str, seconds: int) -> None:
    assert timestamp_to_seconds(timestamp) == seconds
