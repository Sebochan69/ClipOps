# Workflow

The LangGraph skeleton runs `validate -> segment -> detect -> finish`. It uses the deterministic mock provider, stores a `WorkflowRun`, records model metadata, and marks invalid input as `FAILED` with a concise error.

When `source_content_id` and `account_profile_id` are provided, a completed workflow creates six `ClipCandidate` records and generated draft assets for each candidate. The workflow run ID is the batch identifier used by the frontend Review queue.

The current frontend does not start workflows directly after transcript validation. Use `scripts/feature_smoke.py --local-db` or call the backend workflow from Python to create demo candidates.
