# Transcript parsing

The parser accepts `[00:01:23] text`, `00:01:23 - text`, `[01:02] text`, and `01:02 text`. It preserves each accepted raw line and reports malformed lines with their line number and a remediation hint. Minimum-length and monotonic-timestamp validation are the next ticket.
