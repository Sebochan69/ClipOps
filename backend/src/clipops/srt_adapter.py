import re
from dataclasses import dataclass

from clipops.transcript_parser import ParseIssue

TIMING_PATTERN = re.compile(
    r"^(?P<start>\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+(?P<end>\d{2}:\d{2}:\d{2},\d{3})$"
)


@dataclass(frozen=True)
class SrtBlock:
    sequence: int
    start_seconds: int
    end_seconds: int
    text: str


@dataclass(frozen=True)
class SrtImportResult:
    blocks: list[SrtBlock]
    issues: list[ParseIssue]

    @property
    def normalized_text(self) -> str:
        return "\n".join(f"[{block.start_seconds // 3600:02}:{block.start_seconds % 3600 // 60:02}:{block.start_seconds % 60:02}] {block.text}" for block in self.blocks)


def _seconds(timestamp: str) -> int:
    hours, minutes, second_millis = timestamp.split(":")
    seconds, _ = second_millis.split(",")
    if int(minutes) >= 60 or int(seconds) >= 60:
        raise ValueError("minutes and seconds must be below 60")
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds)


def parse_srt(text: str) -> SrtImportResult:
    blocks: list[SrtBlock] = []
    issues: list[ParseIssue] = []
    line_offset = 0
    for raw_block in re.split(r"\r?\n\s*\r?\n", text.strip()):
        lines = raw_block.splitlines()
        block_line = line_offset + 1
        line_offset += len(lines) + 1
        if len(lines) < 3 or not lines[0].isdigit():
            issues.append(ParseIssue(block_line, "Invalid SRT block.", "Use a sequence number, timestamp range, and text."))
            continue
        timing = TIMING_PATTERN.match(lines[1])
        if not timing:
            issues.append(ParseIssue(block_line + 1, "Invalid SRT timestamp range.", "Use HH:MM:SS,mmm --> HH:MM:SS,mmm."))
            continue
        try:
            start_seconds, end_seconds = _seconds(timing["start"]), _seconds(timing["end"])
        except ValueError as error:
            issues.append(ParseIssue(block_line + 1, str(error), "Use valid SRT timestamps."))
            continue
        if end_seconds < start_seconds:
            issues.append(ParseIssue(block_line + 1, "SRT end time must follow start time.", "Correct the timestamp range."))
            continue
        blocks.append(SrtBlock(int(lines[0]), start_seconds, end_seconds, " ".join(lines[2:])))
    return SrtImportResult(blocks, issues)
