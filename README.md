# ClipOps

Local-first proof of concept for turning timestamped transcripts into reviewable short-form content drafts.

> All accounts, metrics, experiments, and reports are fictional or simulated. ClipOps does not process video, post to social platforms, or guarantee growth.

## What It Demonstrates

- Transcript validation and deterministic segmentation.
- `.srt`, `.txt`, and `.md` transcript import in the frontend.
- Mock AI moment and asset generation with structured-output validation and one repair attempt.
- Human review, mock publishing queue, simulated performance, experiments, dashboard, and weekly reports.
- FastAPI, SQLite, React/TypeScript, LangGraph, tests, and local CI checks.

## Feature Map

ClipOps is organized around a local content-review workflow:

1. **Transcript intake**: paste or upload a timestamped transcript. Valid `.srt` files are normalized into ClipOps timestamp lines before validation.
2. **Segment review**: validated transcript lines are grouped into deterministic review segments.
3. **Workflow history**: shows transcript-processing runs, status, and model-run metadata. A completed workflow run is the batch ID for generated candidates.
4. **Review queue**: loads candidates from a workflow run so a human can submit, approve, reject, or move clips back to editing.
5. **Candidate detail**: shows a candidate's transcript excerpt, score, reason selected, and generated draft assets. Assets can be edited and saved.
6. **Publishing queue**: displays approved candidates that were added to the mock queue. No real social platform is contacted.
7. **Dashboard**: summarizes simulated approval, queue, account-health, and performance metrics.
8. **Experiment readout**: stores a simple hook/CTA/content experiment with a clear simulated-data caveat.
9. **Weekly report**: generates a structured simulated report with fleet snapshot, top clips, workflow metrics, next experiment, backlog suggestions, and caveats.

Current frontend limitation: validating a transcript and reviewing segments works in the UI, but the UI does not yet have a button that starts a workflow from the uploaded transcript. Use the smoke script below to create demo workflow runs and candidates for the Review queue.

## Run Locally

Requirements: Python 3.11+, [uv](https://docs.astral.sh/uv/), and Node.js 20+.

Start the backend:

```bash
cd backend
uv sync --group dev
uv run python -m clipops.seed
uv run uvicorn clipops.main:app --app-dir src --reload
```

Start the frontend in another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL, normally `http://127.0.0.1:5173`. The API is at `http://127.0.0.1:8000`.

If port `8000` is already in use, another backend process is running. Check it with:

```bash
ss -ltnp | grep ':8000'
```

## Demo Data And Smoke Test

The easiest end-to-end demo setup is:

```bash
cd backend
uv run --with httpx python scripts/feature_smoke.py --local-db
```

This writes demo records to `backend/clipops.db`, prints a `UI workflow_run_id`, and verifies:

- SRT import
- transcript validation
- segmentation
- workflow generation
- candidate scoring and generated assets
- review lifecycle
- mock publishing queue
- simulated performance
- dashboard
- experiment
- weekly report

Paste the printed `UI workflow_run_id` into the frontend **Review queue** panel and click **Load queue**.

For an isolated run that does not modify the UI database:

```bash
cd backend
uv run --with httpx python scripts/feature_smoke.py
```

See [docs/FEATURE_TEST_SCRIPT.md](docs/FEATURE_TEST_SCRIPT.md) for a frontend manual test script and expected outputs.

## Checks

```bash
cd backend && uv run ruff check . && uv run pytest
cd frontend && npm run check
```

## Architecture

```text
React UI -> FastAPI -> SQLite
                  |
          LangGraph workflow -> replaceable ModelProvider
                  |
        human review -> mock queue -> simulated metrics
```

See `docs/` for domain, scoring, validation, evaluation, report, observability, and feature-test details.

## Limitations

No real video processing, social integration, authentication, external analytics, cloud deployment, or causal-growth claims. All performance, experiments, and weekly reports are simulated.
