# Candidates API

`GET /workflow-runs/{workflow_run_id}/candidates` returns candidates ranked by overall score, with unscored candidates last. Optional `?status=APPROVED` filters by lifecycle status. Generated assets are returned as an empty placeholder until asset generation is implemented.
