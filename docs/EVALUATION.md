# Evaluation

## What is tested

- Timestamp parsing, validation, segmentation, scoring, state transitions, persistence, and API error paths use deterministic pytest fixtures.
- `MockModelProvider` produces deterministic moment and asset drafts for local tests.
- Structured moment and asset outputs are validated with Pydantic; malformed fixtures verify rejection and the one-attempt repair boundary.
- Workflow tests cover completed and failed validation runs, including recorded model metadata.

## Human-review boundary

Generated candidates and assets are drafts. Business validation is required before `NEEDS_REVIEW`; a human must approve a candidate before it can enter the mock publishing queue. ClipOps never automatically posts content.

## Limitations

All accounts, transcripts, metrics, experiments, and reports are fictional or simulated. Tests verify contracts and state changes, not real-world content quality, causal growth, or model reliability.
