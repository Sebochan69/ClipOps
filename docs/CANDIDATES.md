# Candidates API

`GET /workflow-runs/{workflow_run_id}/candidates` returns candidates ranked by overall score, with unscored candidates last. Optional `?status=APPROVED` filters by lifecycle status.

`GET /candidates/{candidate_id}` returns scores and editable generated assets. `PATCH /candidates/{candidate_id}/assets/{asset_id}` saves an edited asset draft.
