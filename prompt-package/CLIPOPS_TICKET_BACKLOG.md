# ClipOps Ticket Backlog

Each ticket should fit one focused pi.dev session. Do not combine tickets unless the owner approves.

## Recommended implementation order

Start with `P0-T01`, then proceed through phases in order. Within a phase, complete tickets in numeric order unless dependencies are already satisfied.

## Phase 0 — Research synthesis and repository setup

### P0-T01 — Repository skeleton and developer workflow

- Objective: create the initial local-first repo structure.
- User value: gives pi.dev and reviewers a predictable project foundation.
- Dependencies: none.
- Deliverables: backend app skeleton, frontend skeleton, tests directory, docs directory, `.env.example`, seed-data directory, basic README draft.
- Acceptance criteria: repo has runnable backend and frontend placeholders; README explains setup; no ClipOps workflow logic yet.
- Tests: backend smoke test; frontend build or smoke check.
- Non-goals: domain models, AI workflow, dashboard.
- Order: first ticket.

### P0-T02 — CI and quality scripts

- Objective: add repeatable local and GitHub Actions checks.
- User value: makes completion claims evidence-based.
- Dependencies: P0-T01.
- Deliverables: test/lint/type scripts, minimal GitHub Actions workflow, documented commands.
- Acceptance criteria: CI runs backend tests and frontend checks on pull request/push.
- Tests: run configured commands locally.
- Non-goals: deployment, cloud secrets, production release.
- Order: after skeleton.

## Phase 1 — Domain models and seeded demo data

### P1-T01 — Core SQLAlchemy models and Pydantic schemas

- Objective: define v1 domain entities.
- User value: establishes the data contract for the workflow.
- Dependencies: P0-T01.
- Deliverables: models/schemas for SourceContent, Transcript, TranscriptSegment, ContentBrief, AccountProfile, ClipCandidate, ClipScore, GeneratedAsset, ReviewDecision, PublishingQueueItem, PerformanceRecord, ContentExperiment, WeeklyGrowthReport, WorkflowRun, ModelRun.
- Acceptance criteria: models create SQLite tables; schemas validate expected fixtures; entity relationships are documented.
- Tests: schema validation tests; database create/drop test.
- Non-goals: UI, model calls, business workflow.
- Order: before workflow features.

### P1-T02 — Seed fictional accounts, briefs, and demo transcript

- Objective: create safe fictional demo data.
- User value: enables a five-minute demo without private material.
- Dependencies: P1-T01.
- Deliverables: seed loader, three fictional account profiles, two content briefs, one valid timestamped transcript.
- Acceptance criteria: seed command loads data idempotently; README explains simulated/fictional data.
- Tests: seed idempotency test; no real personal/client names in seed files.
- Non-goals: performance data and experiments.
- Order: after models.

## Phase 2 — Transcript ingestion and validation

### P2-T01 — Transcript parser

- Objective: parse supported timestamped transcript formats.
- User value: lets users paste/upload transcripts safely.
- Dependencies: P1-T01.
- Deliverables: parser service, parsed line model, timestamp normalization.
- Acceptance criteria: supports specified timestamp formats; preserves source text; reports line-level parse errors.
- Tests: valid transcript fixtures, malformed line fixtures, timestamp conversion tests.
- Non-goals: segmentation, AI moment detection.
- Order: first transcript ticket.

### P2-T02 — Transcript validation API

- Objective: expose transcript validation through FastAPI.
- User value: users receive immediate feedback before running AI.
- Dependencies: P2-T01.
- Deliverables: validation endpoint, error response contracts, persistence of valid transcript.
- Acceptance criteria: invalid transcripts return typed errors; valid transcripts create Transcript records.
- Tests: API tests for valid, too-short, non-monotonic, and malformed transcripts.
- Non-goals: frontend upload UI.
- Order: after parser.

### P2-T03 — Transcript input UI

- Objective: create paste/upload UI for transcript validation.
- User value: starts the visible workflow.
- Dependencies: P2-T02.
- Deliverables: React form, validation result display, error states.
- Acceptance criteria: user can paste transcript, submit, see success/errors, and proceed only after valid input.
- Tests: frontend component or flow test; manual verification.
- Non-goals: segmentation display.
- Order: after API.

## Phase 3 — Transcript segmentation

### P3-T01 — Deterministic segmentation service

- Objective: split transcript into candidate analysis windows.
- User value: creates stable inputs for moment detection.
- Dependencies: P2-T02.
- Deliverables: segmentation rules, TranscriptSegment persistence, configuration.
- Acceptance criteria: segments have monotonic start/end times, text, duration, and source line references.
- Tests: segmentation fixture tests; boundary duration tests.
- Non-goals: AI scoring.
- Order: before AI moment detection.

### P3-T02 — Segment review API/UI

- Objective: expose generated segments for inspection.
- User value: makes the pipeline transparent.
- Dependencies: P3-T01.
- Deliverables: segments endpoint and UI list.
- Acceptance criteria: user can view segments with timestamps and text; empty/error states handled.
- Tests: API test and frontend render/build check.
- Non-goals: manual segment editing in v1 unless approved.
- Order: after segmentation service.

## Phase 4 — AI moment detection

### P4-T01 — Model provider interface and mock provider

- Objective: isolate model calls behind a replaceable contract.
- User value: enables deterministic local tests and future provider changes.
- Dependencies: P1-T01, P3-T01.
- Deliverables: `ModelProvider` interface, `MockModelProvider`, model-run metadata recording.
- Acceptance criteria: mock provider returns deterministic candidate-like output; no real API key required for tests.
- Tests: provider contract tests; ModelRun persistence tests.
- Non-goals: real provider integration.
- Order: before LangGraph workflow.

### P4-T02 — LangGraph workflow skeleton

- Objective: create explicit workflow state and nodes.
- User value: makes the AI pipeline inspectable and resumable.
- Dependencies: P4-T01.
- Deliverables: graph state schema, nodes for validate/segment/detect placeholders, run status recording.
- Acceptance criteria: graph runs end-to-end with mock provider and creates WorkflowRun records.
- Tests: graph smoke test; failed-node status test.
- Non-goals: final scoring/assets.
- Order: after provider interface.

### P4-T03 — Moment detection prompt and structured output

- Objective: generate at least six moment candidates from transcript segments.
- User value: creates core ClipOps output.
- Dependencies: P4-T02.
- Deliverables: prompt version, Pydantic output schema, candidate creation service.
- Acceptance criteria: mock workflow creates six candidates with timestamps and excerpts; real provider path is configurable but not required in CI.
- Tests: mock workflow test; malformed output test.
- Non-goals: asset generation.
- Order: after graph skeleton.

## Phase 5 — Clip scoring

### P5-T01 — Clip scoring model and aggregation

- Objective: implement score dimensions and overall score rules.
- User value: gives users a transparent candidate ranking.
- Dependencies: P4-T03.
- Deliverables: ClipScore schema/model, deterministic overall-score calculation, confidence handling.
- Acceptance criteria: every candidate has all required dimensions and a concise explanation.
- Tests: scoring aggregation tests; invalid score-range tests.
- Non-goals: analytics dashboard.
- Order: before candidate UI.

### P5-T02 — Candidate ranking API

- Objective: return ranked candidates for a workflow run.
- User value: lets frontend display strongest candidates first.
- Dependencies: P5-T01.
- Deliverables: candidates endpoint with sorting/filtering.
- Acceptance criteria: endpoint returns ranked candidates with scores and assets placeholder.
- Tests: API ranking and filter tests.
- Non-goals: review decisions.
- Order: after scoring.

## Phase 6 — Hook and content-asset generation

### P6-T01 — Asset-generation prompt and schema

- Objective: generate hooks, titles, captions, CTAs, and editing notes.
- User value: turns candidate moments into usable content drafts.
- Dependencies: P5-T01, P4-T01.
- Deliverables: asset prompt, schema, storage, mock output.
- Acceptance criteria: each candidate receives 3 hooks, 2 titles, 2 captions, 1 CTA, and editing notes.
- Tests: schema tests; mock generation workflow test.
- Non-goals: platform-specific publishing automation.
- Order: after scoring.

### P6-T02 — Candidate detail UI

- Objective: show full candidate details and editable generated assets.
- User value: makes human review practical.
- Dependencies: P5-T02, P6-T01.
- Deliverables: candidate card/detail component, editable fields, score display.
- Acceptance criteria: user can inspect timestamps, transcript excerpt, scores, explanations, and assets.
- Tests: component/render tests; manual UI verification.
- Non-goals: approval queue transitions.
- Order: before review queue.

## Phase 7 — Structured-output repair and validation

### P7-T01 — One-attempt repair loop

- Objective: repair malformed model output once.
- User value: improves reliability without hiding failures.
- Dependencies: P4-T03, P6-T01.
- Deliverables: validation/repair service, failure status, repair count in ModelRun.
- Acceptance criteria: malformed output triggers one repair; second failure returns typed error and does not create invalid records.
- Tests: malformed-first-then-valid fixture; malformed-twice fixture.
- Non-goals: unlimited retries or autonomous prompt optimization.
- Order: after AI outputs exist.

### P7-T02 — Business-rule validation

- Objective: validate timestamp ranges, duration bounds, brand-safety fields, and required assets.
- User value: prevents bad candidates from reaching review.
- Dependencies: P7-T01.
- Deliverables: validation rules and typed errors.
- Acceptance criteria: invalid ranges/assets/statuses are rejected before `NEEDS_REVIEW`.
- Tests: invalid timestamp, missing asset, unsafe-status tests.
- Non-goals: full content moderation service.
- Order: before review queue.

## Phase 8 — Human review queue

### P8-T01 — Review decision API and state transitions

- Objective: implement approve/reject/edit lifecycle.
- User value: ensures human-in-the-loop control.
- Dependencies: P7-T02.
- Deliverables: review endpoints, ReviewDecision persistence, state-transition guard.
- Acceptance criteria: only valid transitions allowed; decisions record reason and timestamp.
- Tests: approve/reject/edit API tests; invalid transition tests.
- Non-goals: multi-user reviewer identities.
- Order: before publishing queue.

### P8-T02 — Review queue UI

- Objective: create review workflow UI.
- User value: lets users edit, approve, and reject candidates.
- Dependencies: P8-T01, P6-T02.
- Deliverables: queue page, filters by status, edit/approve/reject actions.
- Acceptance criteria: user can approve three candidates and reject others with reasons.
- Tests: UI flow/build check; API integration check.
- Non-goals: bulk automation.
- Order: after review API.

## Phase 9 — Mock publishing queue

### P9-T01 — Queue approved candidates

- Objective: move approved candidates into mock publishing queue.
- User value: demonstrates handoff from review to operations.
- Dependencies: P8-T01.
- Deliverables: queue model/API, schedule fields, platform/account display.
- Acceptance criteria: only approved candidates can be queued; queue item status is visible.
- Tests: API tests for approved and non-approved queue attempts.
- Non-goals: real platform posting.
- Order: after review queue.

### P9-T02 — Publishing queue UI

- Objective: show mock queue.
- User value: makes operations workflow visible in demo.
- Dependencies: P9-T01.
- Deliverables: queue page/list, schedule/edit status controls.
- Acceptance criteria: approved candidates appear in queue with simulated publishing metadata.
- Tests: UI render/build check.
- Non-goals: calendar integration.
- Order: after queue API.

## Phase 10 — Performance-data import

### P10-T01 — Simulated performance records

- Objective: import or seed simulated metrics.
- User value: enables dashboard and experiment demo.
- Dependencies: P9-T01.
- Deliverables: performance schema/API/seed import, simulated-data disclosure field.
- Acceptance criteria: performance records link to queue items; all records are labeled simulated.
- Tests: import tests; missing/invalid metric tests.
- Non-goals: real social analytics connectors.
- Order: before dashboard.

## Phase 11 — Fleet dashboard

### P11-T01 — Metrics aggregation service

- Objective: compute content, workflow, and fleet metrics.
- User value: turns operations data into dashboard insights.
- Dependencies: P10-T01.
- Deliverables: aggregation functions and dashboard API.
- Acceptance criteria: metrics have documented formulas and denominators.
- Tests: fixture-based metric tests.
- Non-goals: causal attribution.
- Order: before dashboard UI.

### P11-T02 — Fleet dashboard UI

- Objective: display account health and fleet performance.
- User value: lets hiring reviewers understand operational outcomes quickly.
- Dependencies: P11-T01.
- Deliverables: dashboard page with cards, charts/tables, simulated-data banner.
- Acceptance criteria: shows account health, top clips, approval rate, queue status, and performance metrics.
- Tests: UI render/build check; manual demo verification.
- Non-goals: advanced BI.
- Order: after aggregation.

## Phase 12 — Experiment tracker

### P12-T01 — Experiment data model and API

- Objective: represent hook/CTA/content-pillar experiments.
- User value: shows structured content experimentation.
- Dependencies: P10-T01.
- Deliverables: experiment models/API, variant assignment link to clips.
- Acceptance criteria: can create one experiment comparing two hook types.
- Tests: API tests; invalid experiment tests.
- Non-goals: statistically rigorous experimentation engine.
- Order: after performance import.

### P12-T02 — Experiment readout UI

- Objective: show variant comparison and caveats.
- User value: makes growth thinking visible.
- Dependencies: P12-T01, P11-T01.
- Deliverables: experiment page with winner, metric comparison, caveat note.
- Acceptance criteria: readout labels simulated/small-sample limitations and proposes next test.
- Tests: UI render/build check; metric fixture test.
- Non-goals: significance testing claims.
- Order: after experiment API.

## Phase 13 — Weekly growth report

### P13-T01 — Weekly report generator

- Objective: generate structured weekly recommendation report from metrics and experiments.
- User value: turns data into operational next steps.
- Dependencies: P11-T01, P12-T01, P4-T01.
- Deliverables: report schema, deterministic summary sections, optional AI-drafted recommendations through mock provider.
- Acceptance criteria: report includes fleet snapshot, top clips, experiment readout, workflow metrics, next experiment, and caveats.
- Tests: report fixture tests; mock provider test.
- Non-goals: real forecasting or growth guarantees.
- Order: after dashboard and experiment.

### P13-T02 — Weekly report UI

- Objective: display weekly report.
- User value: completes final demo narrative.
- Dependencies: P13-T01.
- Deliverables: report page and export/copy-friendly layout.
- Acceptance criteria: report is readable in under two minutes and includes simulated-data disclosure.
- Tests: UI render/build check; manual verification.
- Non-goals: PDF export unless approved.
- Order: after generator.

## Phase 14 — Evaluation and observability

### P14-T01 — Workflow observability and run history

- Objective: make workflow runs inspectable.
- User value: supports debugging and portfolio credibility.
- Dependencies: P4-T02, P7-T01.
- Deliverables: run history API/UI, ModelRun metadata display, failure states.
- Acceptance criteria: user can see run status, node errors, repair attempts, and model metadata.
- Tests: run-history API tests; failed-run fixture.
- Non-goals: distributed tracing backend.
- Order: after core workflow.

### P14-T02 — Evaluation report

- Objective: document model/output quality checks.
- User value: shows honest AI reliability discipline.
- Dependencies: P7-T01, P13-T01.
- Deliverables: `docs/EVALUATION.md` with fixtures, limitations, and testing approach.
- Acceptance criteria: documents mock provider, malformed-output tests, human review boundary, and limitations.
- Tests: documentation link/check if available.
- Non-goals: automated LLM benchmark suite.
- Order: after workflow tests exist.

## Phase 15 — Final UX and documentation

### P15-T01 — README, demo script, screenshots plan

- Objective: make the repo understandable to a hiring manager.
- User value: improves portfolio presentation.
- Dependencies: core demo path complete.
- Deliverables: README, demo script, limitations, architecture diagram, screenshots checklist.
- Acceptance criteria: reviewer can run or understand the demo in five minutes.
- Tests: follow setup instructions on a clean local run where practical.
- Non-goals: video recording unless approved.
- Order: near final.

### P15-T02 — UX polish and accessibility pass

- Objective: improve clarity and basic accessibility.
- User value: makes dashboard/review experience credible.
- Dependencies: main UI pages complete.
- Deliverables: empty/loading/error states, labels, keyboard-friendly controls, visual hierarchy pass.
- Acceptance criteria: all main pages handle empty/loading/error states and have clear calls to action.
- Tests: frontend build/check; manual UI walkthrough.
- Non-goals: full formal accessibility audit.
- Order: final polish.

### P15-T03 — End-to-end demo test

- Objective: verify the final demo scenario.
- User value: prevents "happy path only in prose."
- Dependencies: final workflow path complete.
- Deliverables: scripted E2E or integration demo test.
- Acceptance criteria: test covers transcript input through candidates, approvals, queue, metrics, experiment, weekly report.
- Tests: the E2E test itself plus supporting fixtures.
- Non-goals: browser-matrix testing.
- Order: final gate.

## Phase 16 — Optional video ingestion

### P16-T01 — Video/transcription research spike

- Objective: evaluate future video upload/transcription/FFmpeg path.
- User value: prepares roadmap without contaminating v1.
- Dependencies: v1 complete.
- Deliverables: short design note and candidate tickets.
- Acceptance criteria: documents tradeoffs, dependencies, risks, and no implementation changes.
- Tests: none required beyond docs review.
- Non-goals: video implementation.
- Order: after v1 only.

### P16-T02 — Optional transcript import from transcription output

- Objective: ingest transcript formats from future transcription tools.
- User value: bridges v1 transcript pipeline to later video features.
- Dependencies: P16-T01 approval.
- Deliverables: parser adapter for one approved transcript export format.
- Acceptance criteria: adapter normalizes into existing Transcript model without changing core workflow.
- Tests: adapter fixture tests.
- Non-goals: transcription, clipping, video preview.
- Order: optional future.
