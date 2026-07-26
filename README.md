# ClipOps

Local-first proof of concept for reviewing AI-assisted short-form content candidates.

> This repository will use fictional seed data and clearly labeled simulated performance data. It does not process video or publish to social platforms.

## Setup

Requirements: Python 3.11+, [uv](https://docs.astral.sh/uv/), and Node.js 20+.

```bash
cd backend
uv sync --group dev
uv run uvicorn clipops.main:app --app-dir src --reload
```

The API health check is at `http://127.0.0.1:8000/health`.

```bash
cd frontend
npm install
npm run dev
```

## Checks

```bash
cd backend && uv run pytest
cd frontend && npm run build
```

## Status

Only the project skeleton exists. See `prompt-package/` for the approved product specification and ticket backlog.
