# Segmentation

Validated transcript lines are grouped into deterministic windows shorter than 60 seconds. Each segment stores timestamp bounds, joined text, and source-line references. Re-running segmentation replaces that transcript's prior segments.

Successful transcript validation creates segments. `GET /transcripts/{transcript_id}/segments` returns them in timestamp order; the transcript form can then display them.
