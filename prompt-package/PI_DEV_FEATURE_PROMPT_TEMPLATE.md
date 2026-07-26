# pi.dev Feature Prompt Template

Use this template for one ClipOps feature at a time. Replace bracketed placeholders before sending.

## Ticket

- Ticket ID: `[TICKET-ID]`
- Feature title: `[TITLE]`
- Phase: `[PHASE]`

## User value

`[Explain what this feature lets the content operations user do.]`

## Scope

Implement only:

- `[Scope item 1]`
- `[Scope item 2]`
- `[Scope item 3]`

## Explicit non-scope

Do not implement:

- `[Non-scope item 1]`
- `[Non-scope item 2]`
- `[Future phase to avoid]`

If you discover adjacent work, document it as a follow-up ticket instead of implementing it.

## Dependencies

- Required prior tickets: `[IDs or none]`
- Required docs: `AGENTS.md`, `CLIPOPS_MASTER_SPEC.md`, `CLIPOPS_ARCHITECTURE_DECISIONS.md`
- Relevant existing files: `[Paths]`

## Expected behavior

`[Describe exact user/system behavior.]`

## Data contracts

Inputs:

- `[Field/type/validation]`

Outputs:

- `[Field/type/validation]`

Persistence changes:

- `[Tables/models/migrations or none]`

## API contracts

Endpoints to add/change:

- `[METHOD /path]` — `[request schema]` → `[response schema]`

Error cases:

- `[error code and condition]`

## UI requirements

Screens/components:

- `[Component/path]`

States to handle:

- Empty.
- Loading.
- Success.
- Failure.
- Validation error.

## AI behavior

Model-provider use:

- `[None / Mock provider / Real provider interface / LangGraph node]`

Rules:

- Validate structured output with Pydantic.
- Allow at most one repair attempt if model output is malformed.
- Store concise user-facing explanations only.
- Do not expose hidden chain-of-thought.

## Acceptance criteria

The feature is complete when:

- `[Measurable criterion 1]`
- `[Measurable criterion 2]`
- `[Measurable criterion 3]`

## Required tests

Add or update:

- Unit tests: `[required tests]`
- API/integration tests: `[required tests]`
- UI tests/build checks: `[required checks]`
- Negative/error tests: `[required tests]`

## Required documentation

Update:

- `[README/docs/ADR/spec/backlog path]`

## Reviewer checklist

The reviewer should check:

- Scope compliance.
- Architecture fit.
- Data/API contract correctness.
- Tests and test evidence.
- Error handling.
- AI-output validation.
- Simulated-data disclosure if relevant.
- Documentation accuracy.

## Completion report format

Report exactly:

1. Ticket ID and title.
2. Summary.
3. Changed files.
4. Tests added/updated.
5. Commands run and results.
6. Manual verification.
7. Known limitations.
8. Follow-up tickets.

Stop after the report.
