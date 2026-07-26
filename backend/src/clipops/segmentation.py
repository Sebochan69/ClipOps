from dataclasses import dataclass

from sqlalchemy import delete
from sqlalchemy.orm import Session

from clipops.models import TranscriptSegment
from clipops.transcript_parser import ParsedTranscriptLine, parse_transcript

MAX_SEGMENT_DURATION_SECONDS = 60


@dataclass(frozen=True)
class Segment:
    start_seconds: int
    end_seconds: int
    source_line_start: int
    source_line_end: int
    text: str


def segment_transcript(text: str, max_duration_seconds: int = MAX_SEGMENT_DURATION_SECONDS) -> list[Segment]:
    parsed = parse_transcript(text)
    if parsed.issues:
        raise ValueError("Cannot segment a transcript with parse errors.")
    groups: list[list[ParsedTranscriptLine]] = []
    for line in parsed.lines:
        if not groups or line.timestamp_seconds - groups[-1][0].timestamp_seconds >= max_duration_seconds:
            groups.append([])
        groups[-1].append(line)
    return [
        Segment(
            start_seconds=group[0].timestamp_seconds,
            end_seconds=max(group[-1].timestamp_seconds, group[0].timestamp_seconds + 1),
            source_line_start=group[0].line_number,
            source_line_end=group[-1].line_number,
            text="\n".join(line.text for line in group),
        )
        for group in groups
    ]


def persist_segments(session: Session, transcript_id: str, text: str) -> list[Segment]:
    segments = segment_transcript(text)
    session.execute(delete(TranscriptSegment).where(TranscriptSegment.transcript_id == transcript_id))
    session.add_all(
        TranscriptSegment(
            id=f"{transcript_id}:{segment.source_line_start}-{segment.source_line_end}",
            transcript_id=transcript_id,
            start_seconds=segment.start_seconds,
            end_seconds=segment.end_seconds,
            source_line_start=segment.source_line_start,
            source_line_end=segment.source_line_end,
            text=segment.text,
        )
        for segment in segments
    )
    session.commit()
    return segments
