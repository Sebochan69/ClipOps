import re
from dataclasses import dataclass

LINE_PATTERN = re.compile(
    r"^\[?(?P<timestamp>\d{2}:\d{2}(?::\d{2})?)\]?(?:\s+-\s+|\s+)(?P<text>.+)$"
)


@dataclass(frozen=True)
class ParsedTranscriptLine:
    line_number: int
    timestamp_seconds: int
    text: str
    raw_line: str


@dataclass(frozen=True)
class ParseIssue:
    line_number: int
    message: str
    suggested_action: str


@dataclass(frozen=True)
class ParseResult:
    lines: list[ParsedTranscriptLine]
    issues: list[ParseIssue]


def timestamp_to_seconds(timestamp: str) -> int:
    parts = [int(part) for part in timestamp.split(":")]
    if len(parts) == 2:
        minutes, seconds = parts
        hours = 0
    elif len(parts) == 3:
        hours, minutes, seconds = parts
    else:
        raise ValueError("timestamp must use MM:SS or HH:MM:SS")
    if seconds >= 60 or (len(parts) == 3 and minutes >= 60):
        raise ValueError("minutes and seconds must be below 60")
    return hours * 3600 + minutes * 60 + seconds


def parse_transcript(text: str) -> ParseResult:
    lines: list[ParsedTranscriptLine] = []
    issues: list[ParseIssue] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip():
            continue
        match = LINE_PATTERN.match(raw_line)
        if not match:
            issues.append(ParseIssue(line_number, "Invalid timestamped line.", "Use [00:01:23] text or 00:01:23 - text."))
            continue
        try:
            timestamp_seconds = timestamp_to_seconds(match["timestamp"])
        except ValueError as error:
            issues.append(ParseIssue(line_number, str(error), "Use valid minute and second values."))
            continue
        lines.append(ParsedTranscriptLine(line_number, timestamp_seconds, match["text"], raw_line))
    return ParseResult(lines, issues)
