# Five-minute demo

1. Start the backend and frontend using the README commands.
2. Upload `seed-data/demo-2min.srt` or paste `seed-data/demo-transcript.md`; validate and inspect segments.
3. Run `cd backend && uv run --with httpx python scripts/feature_smoke.py --local-db` to create a demo workflow run, candidates, draft assets, queue item, simulated performance, experiment, and report data.
4. Copy the printed `UI workflow_run_id`.
5. In the frontend, load Workflow history and point out that a completed run is the batch record for generated candidates.
6. Paste the workflow run ID into Review queue, load candidates, and submit/approve/reject a candidate.
7. Load Candidate detail to inspect score metadata and editable generated assets.
8. Load Publishing queue, Dashboard, Experiment readout, and Weekly report.
9. End by pointing out the simulated-data banner, human review gate, model-run history, and limitations.

The frontend can validate transcripts and display segments manually. Workflow generation is currently triggered through the script/API rather than a frontend button.
