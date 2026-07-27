# ClipOps Feature Test Script

Use this script to verify the demo path and expected outcomes across transcript import, segmentation, workflow generation, review, publishing, metrics, experiments, and weekly reports.

## Automated Smoke Test

Run from `backend`:

```bash
uv run --with httpx python scripts/feature_smoke.py
```

Expected output shape:

```text
[PASS] SRT import: blocks=20 issues=0
[PASS] Transcript validation: line_count=20 warnings=[]
[PASS] Segmentation: segments=2 ranges=0-54,60-114
[PASS] Workflow: status=COMPLETED workflow_run_id=<uuid> candidates=6 assets=54
[PASS] Workflow history: run listed model_runs=<count>
[PASS] Candidate list: rows=6 top_score=<score>
[PASS] Candidate detail/assets: assets=9 patched_asset=ok
[PASS] Review lifecycle: submit=NEEDS_REVIEW approve=APPROVED reject_requires_reason=true
[PASS] Publishing queue: queue_item_id=queue:<candidate_id> status=QUEUED
[PASS] Performance import: performance_record_id=performance:queue:<candidate_id> simulated=true
[PASS] Dashboard: simulated=true queue_status=1 (+1) approval_rate=0.167
[PASS] Experiment: name=Smoke hook comparison winner=Direct problem hook
[PASS] Weekly report: simulated=true top_clips=1 caveats=3

Feature smoke test complete.
```

By default, the script uses a temporary database and does not affect the running UI.

To seed data that the local UI can load, run:

```bash
uv run --with httpx python scripts/feature_smoke.py --local-db
```

Copy the printed `UI workflow_run_id` into the frontend Review queue panel.

When using `--local-db`, existing demo records remain in `backend/clipops.db`, so dashboard totals may be higher than the isolated example. The smoke test expects the queue count to increase by one during each run.

## Manual UI Test

Start services:

```bash
cd backend
uv run uvicorn clipops.main:app --app-dir src --reload
```

```bash
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173`.

### 1. Transcript SRT Import

Steps:

1. Enter a source title, for example `Demo 2-minute SRT`.
2. Click Browse and choose `seed-data/demo-2min.srt`.
3. Click Validate transcript.

Expected:

```text
Transcript validated: 20 timestamped lines.
```

No warnings should appear.

### 2. Segments

Steps:

1. Click Review segments.

Expected:

```text
0s-54s
<first ten caption lines joined as one segment>

60s-114s
<second ten caption lines joined as one segment>
```

ClipOps uses subtitle start timestamps for segment bounds, so the final visible starts are `54s` and `114s` even though the SRT file runs to `120s`.

### 3. Workflow History

Setup:

```bash
cd backend
uv run --with httpx python scripts/feature_smoke.py --local-db
```

Steps:

1. Copy the printed `UI workflow_run_id`.
2. In the UI, click Load runs under Workflow history.

Expected:

```text
COMPLETED
model_runs includes moment-detection-v1 and asset-generation-v1 entries
```

### 4. Review Queue

Steps:

1. Paste the `UI workflow_run_id` into Review queue > Workflow run ID.
2. Leave Status filter as All.
3. Click Load queue.

Expected:

```text
Six candidate cards appear.
Each card shows a status and transcript excerpt.
Scored candidates appear in descending score order.
```

Review actions:

```text
Submit -> status becomes NEEDS_REVIEW
Approve -> status becomes APPROVED
Reject without reason -> error
Reject with reason -> status becomes REJECTED
Edit -> status becomes EDITING where the transition is valid
```

### 5. Candidate Detail And Asset Editing

Steps:

1. Copy a candidate ID from the Review queue.
2. Paste it into Candidate detail > Candidate ID.
3. Click Load candidate.
4. Edit one generated asset textarea.
5. Click Save.

Expected:

```text
Candidate detail shows transcript excerpt, reason selected, confidence, score JSON, and 9 generated assets.
Saving an asset returns without an error and the edited text remains visible.
```

### 6. Publishing Queue

The current UI can display the publishing queue, but queueing an approved candidate is API-only.

Queue an approved candidate:

```bash
curl -X POST http://127.0.0.1:8000/candidates/<candidate_id>/queue \
  -H "Content-Type: application/json" \
  -d '{"scheduled_for":"2026-08-01T09:00:00Z"}'
```

Expected API response:

```json
{"queue_item_id":"queue:<candidate_id>","status":"QUEUED"}
```

UI steps:

1. Click Load publishing queue.

Expected:

```text
The new queued item appears with account, platform, scheduled time, status, and candidate excerpt.
Older demo queue items may also appear if the local database has been reused.
```

### 7. Simulated Performance

Import simulated performance:

```bash
curl -X POST http://127.0.0.1:8000/performance-records \
  -H "Content-Type: application/json" \
  -d '{"queue_item_id":"queue:<candidate_id>","views":1200,"engagement_rate":0.12}'
```

Expected:

```json
{"performance_record_id":"performance:queue:<candidate_id>","simulated":true}
```

### 8. Dashboard

Steps:

1. Click Load dashboard.

Expected:

```text
Simulated performance data
Approval rate: <percentage>
Queue: <count>
Account cards show health, published count, and median engagement.
```

All values are simulated and directional.

### 9. Experiments

Steps:

1. Click Create hook comparison.

Expected:

```text
Hook comparison
Question vs Statement
Simulated, small sample; no causal claim.
```

### 10. Weekly Report

Steps:

1. Click Generate weekly report.

Expected:

```text
Simulated, directional data only.
Week range is displayed.
Fleet snapshot, top clips, underperforming clips, experiment readout, workflow metrics, next experiment, backlog suggestions, and caveats are rendered as structured sections.
```

Expected caveat:

```text
The report is directional and does not prove causality, forecast growth, or guarantee results.
```

## Negative Tests

Invalid transcript:

```text
[00:00] only one
```

Expected:

```text
TRANSCRIPT_VALIDATION_ERROR
Transcript needs at least 10 timestamped lines.
```

Malformed transcript line:

```text
[00:00] valid
no timestamp
```

Expected:

```text
TRANSCRIPT_PARSE_ERROR
Line 2: Invalid timestamped line.
```

Invalid review transition:

```text
Approve a candidate that is already APPROVED.
```

Expected:

```text
INVALID_STATE_TRANSITION
```

Queue unapproved candidate:

```text
POST /candidates/<detected_candidate_id>/queue
```

Expected:

```text
BUSINESS_RULE_VALIDATION_ERROR
Only approved candidates can be queued.
```
