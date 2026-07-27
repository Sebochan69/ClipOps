# SRT Import

ClipOps supports standard `.srt` blocks containing a numeric sequence line, `HH:MM:SS,mmm --> HH:MM:SS,mmm` range, and one or more text lines. The adapter preserves block order and joins multiline subtitle text with spaces, then normalizes start times into the existing `[HH:MM:SS] text` transcript format.

The frontend Browse/drop area accepts `.srt`, `.txt`, and `.md` files. The backend validation endpoint also normalizes valid SRT input before persisting transcripts and creating segments.

Milliseconds and SRT end times are retained in parsed block metadata, but the current ClipOps transcript contract uses whole-second start timestamps. This adapter does not upload video, transcribe media, run FFmpeg, or support Whisper/Descript exports.
