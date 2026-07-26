# ClipOps

Local-first proof of concept for turning timestamped transcripts into reviewable short-form content drafts.

> All accounts, metrics, experiments, and reports are fictional or simulated. ClipOps does not process video, post to social platforms, or guarantee growth.

## What it demonstrates

- Transcript validation and deterministic segmentation.
- Mock AI moment/asset generation with structured-output validation and one repair attempt.
- Human review, mock publishing queue, simulated performance, experiments, dashboard, and weekly reports.
- FastAPI, SQLite, React/TypeScript, LangGraph, tests, and local CI checks.

## Run locally

Requirements: Python 3.11+, [uv](https://docs.astral.sh/uv/), and Node.js 20+.

```bash
cd backend
uv sync --group dev
uv run python -m clipops.seed
uv run uvicorn clipops.main:app --app-dir src --reload
```

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL, normally `http://127.0.0.1:5173`. The API is at `http://127.0.0.1:8000`.

## Checks

```bash
cd backend && uv run ruff check . && uv run pytest
cd frontend && npm run check
```

## Architecture

```text
React UI → FastAPI → SQLite
                 ↓
        LangGraph workflow → replaceable ModelProvider
                 ↓
      human review → mock queue → simulated metrics
```

See `docs/` for domain, scoring, validation, evaluation, report, and observability details.

## Limitations

No real video processing, social integration, authentication, external analytics, cloud deployment, or causal-growth claims.
