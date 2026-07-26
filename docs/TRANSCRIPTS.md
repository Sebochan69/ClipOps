# Transcript parsing

The parser accepts `[00:01:23] text`, `00:01:23 - text`, `[01:02] text`, and `01:02 text`. It preserves each accepted raw line and reports malformed lines with their line number and a remediation hint.

`POST /transcripts/validate` validates at least 10 monotonic lines, persists valid transcripts, and returns warnings for gaps over 120 seconds. Errors return a code, message, field, suggested action, and line details.
