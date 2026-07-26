from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from clipops.models import Base, SourceContent, Transcript, TranscriptSegment
from clipops.segmentation import persist_segments, segment_transcript

TRANSCRIPT = "[00:00] zero\n[00:20] twenty\n[00:40] forty\n[01:00] sixty"


def test_segments_are_deterministic_and_bounded() -> None:
    segments = segment_transcript(TRANSCRIPT)
    assert [(item.start_seconds, item.end_seconds) for item in segments] == [(0, 40), (60, 61)]
    assert [(item.source_line_start, item.source_line_end) for item in segments] == [(1, 3), (4, 4)]
    assert all(item.end_seconds > item.start_seconds for item in segments)


def test_persist_segments_replaces_previous_segments() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(SourceContent(id="source", title="Source"))
        session.add(Transcript(id="transcript", source_content_id="source", raw_text=TRANSCRIPT))
        session.commit()
        persist_segments(session, "transcript", TRANSCRIPT)
        persist_segments(session, "transcript", TRANSCRIPT)
        assert len(session.scalars(select(TranscriptSegment)).all()) == 2
