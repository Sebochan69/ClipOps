# AGENTS.md

These instructions are for pi.dev and any supporting coding agents working in the ClipOps repository.

## Required reading order

1. `AGENTS.md`
2. `CLIPOPS_MASTER_SPEC.md`
3. `CLIPOPS_ARCHITECTURE_DECISIONS.md`
4. `CLIPOPS_TICKET_BACKLOG.md`
5. The assigned feature prompt or ticket
6. Relevant source files and tests

Do not read unrelated files just because they exist. Load the smallest context needed for the assigned ticket.

## Repository rules

- Implement one approved ticket at a time.
- Preserve existing architecture unless the ticket explicitly requires a change.
- Keep backend, frontend, tests, seed data, and docs in predictable directories.
- Do not commit secrets, real client data, private transcripts, or real social-account credentials.
- Use fictional seed data and label simulated performance data clearly.

## Scope-control rules

Do not add any of the following without explicit owner approval:

- A major dependency.
- A different frontend framework.
- A new service or microservice.
- RAG or embeddings.
- Authentication.
- Cloud infrastructure.
- Automatic posting.
- Full video processing or FFmpeg clipping.
- Replacing LangGraph.
- Restructuring the repository.

## Coding standards

- Backend: Python 3.11+, FastAPI, Pydantic, SQLAlchemy, SQLite for v1.
- Frontend: React with TypeScript unless an ADR is explicitly changed.
- Prefer small modules, typed schemas, explicit errors, and deterministic business logic.
- Keep LLM provider access behind a replaceable interface.
- Keep prompts versioned and testable.
- Do not expose hidden chain-of-thought. Store concise user-facing explanations only.

## Testing requirements

Every feature must include relevant tests. Use:

- Unit tests for pure parsing, scoring, validation, and state transitions.
- API/integration tests for endpoints and persistence.
- Mock model provider tests for AI workflows.
- Malformed model-output tests where AI output is parsed.
- At least one end-to-end demo test by the final phase.

Do not claim "tests pass" without showing the command and result.

## Documentation requirements

Update docs when behavior, setup, architecture, prompts, data contracts, or limitations change. Keep README and ADRs honest. Disclose simulated data and known limitations.

## AI-output handling

- Treat model output as a draft.
- Validate model output against Pydantic schemas.
- Attempt at most one structured-output repair unless the ticket says otherwise.
- Persist `ModelRun` metadata: provider, model, prompt version, validation result, repair count, and cost/token estimate when available.
- Human review is required before queueing or publishing any generated content.

## Prohibited unsupported claims

Do not claim:

- Simulated metrics are real.
- ClipOps guarantees growth.
- A model score proves quality.
- A dashboard proves causality.
- A schema proves truth.
- A reviewer prompt is ground truth.
- The system is production-ready unless production hardening has actually been implemented and verified.

## Feature completion checklist

Before reporting completion:

- Assigned scope implemented.
- Explicit non-scope avoided.
- Tests added/updated and run.
- Error states handled.
- Documentation updated.
- Manual verification completed if UI or workflow behavior changed.
- Changed files listed.
- Evidence included.
- Known limitations stated.
- Next safe task suggested.

## Sub-agent rules

Use sub-agents sparingly. Allowed roles:

- Feature builder.
- Technical reviewer.
- Product critic.
- Documentation reviewer when needed.

Each sub-agent must receive a bounded task, relevant files, output format, and acceptance criteria. Do not spawn many agents early.

## Parallel work rules

Parallel work is allowed only when:

- Shared schemas and API contracts are stable.
- Tasks do not edit overlapping files.
- Each task has independent acceptance criteria.
- One owner is responsible for integration.

Default workflow:

```text
Select ticket
    ↓
Builder implements
    ↓
Technical review
    ↓
Focused remediation
    ↓
Product review when relevant
    ↓
Tests and documentation
    ↓
Commit
```

## Commits and handoffs

- Keep commits focused.
- Commit only after tests and documentation are updated.
- Handoff must include changed files, commands run, test results, manual verification, limitations, and next recommended ticket.
- Stop after the assigned ticket unless the owner explicitly approves the next ticket.
