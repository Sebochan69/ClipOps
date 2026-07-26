# Workflow

The LangGraph skeleton runs `validate → segment → detect → finish`. It uses the deterministic mock provider, stores a `WorkflowRun`, records its model call, and marks invalid input as `FAILED` with a concise error. It does not create clip candidates yet.
