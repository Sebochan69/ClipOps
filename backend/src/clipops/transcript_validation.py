from dataclasses import dataclass

from clipops.transcript_parser import ParsedTranscriptLine, ParseIssue, parse_transcript

MAX_SEGMENT_GAP_SECONDS = 120


@dataclass(frozen=True)
class ValidationResult:
    lines: list[ParsedTranscriptLine]
    issues: list[ParseIssue]
    warnings: list[str]


def validate_transcript(text: str, gap_warning_seconds: int = MAX_SEGMENT_GAP_SECONDS) -> ValidationResult:
    parsed = parse_transcript(text)
    if parsed.issues:
        return ValidationResult(parsed.lines, parsed.issues, [])
    issues: list[ParseIssue] = []
    if len(parsed.lines) < 10:
        issues.append(ParseIssue(0, "Transcript needs at least 10 timestamped lines.", "Add more timestamped transcript lines."))
    for previous, current in zip(parsed.lines, parsed.lines[1:], strict=False):
        if current.timestamp_seconds < previous.timestamp_seconds:
            issues.append(ParseIssue(current.line_number, "Timestamps must be monotonic.", "Move this timestamp after the previous line."))
    warnings = [
        f"Gap of {current.timestamp_seconds - previous.timestamp_seconds} seconds after line {previous.line_number}."
        for previous, current in zip(parsed.lines, parsed.lines[1:], strict=False)
        if current.timestamp_seconds - previous.timestamp_seconds > gap_warning_seconds
    ]
    return ValidationResult(parsed.lines, issues, warnings)
