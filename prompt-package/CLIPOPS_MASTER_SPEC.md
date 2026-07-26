# ClipOps Master Spec

ClipOps is an AI-assisted short-form content operations platform. Version 1 is a polished GitHub proof of concept for an AI Content Systems Manager portfolio project.

ClipOps does not process full video in v1. It starts from timestamped transcripts, a content brief, and a target account profile.

## Product overview

ClipOps turns long-form transcript material into reviewable short-form clip candidates. It validates the transcript, segments it, detects promising moments, scores candidate clips, drafts content assets, routes everything through human review, places approved clips into a mock publishing queue, imports simulated performance data, and produces dashboard and experiment recommendations.

## Target user

Primary user: an AI Content Systems Manager or content operations lead managing a small account fleet and repeatable short-form workflow.

Secondary reviewer: a hiring manager assessing whether the project demonstrates AI workflow design, practical automation, analytics discipline, human-in-the-loop control, and clear documentation.

## Problem statement

Short-form content operations are often ad hoc: timestamps live in notes, clip ideas are subjective, account context is scattered, performance data is disconnected from content decisions, and AI-generated copy can move too quickly without review. ClipOps makes the workflow explicit, repeatable, auditable, and easy to demo.

## Portfolio objective

The project should demonstrate:

- AI-assisted content workflow design.
- Reliable automation from transcript to candidate outputs.
- Human review before publication.
- Account-fleet and experiment thinking.
- Honest analytics using simulated data.
- Maintainable FastAPI/React architecture.
- Practical documentation, tests, and demo readiness.

## Core user story

As a content operations manager, I can paste a timestamped transcript, add a brief, choose an account profile, generate clip candidates with scores and assets, approve the best options, queue them for mock publishing, inspect simulated performance, compare an experiment, and receive a weekly recommendation.

## Required features

1. Timestamped transcript input.
2. Content brief input.
3. Fictional account profile selection.
4. Transcript validation.
5. Transcript segmentation.
6. AI moment detection.
7. Clip candidate scoring.
8. Hook, title, caption, CTA, and editing-note generation.
9. Structured output validation and one repair attempt.
10. Human review queue with edit, approve, and reject.
11. Mock publishing queue.
12. Simulated performance-data import.
13. Fleet dashboard.
14. Experiment tracker.
15. Weekly growth report.
16. README, ADRs, limitations, and demo script.

## Non-goals for v1

- Full video upload or processing.
- Automatic transcription.
- FFmpeg clip generation.
- Automatic social posting.
- Authentication or multi-user accounts.
- Payments, billing, or external platform integrations.
- Cloud deployment.
- Microservices.
- Custom model training or fine-tuning.
- RAG over historical clips.
- Real growth claims.
- Hidden chain-of-thought display or requests.

## Input formats

### Timestamped transcript

Accept pasted text or uploaded `.txt`/`.md`.

Required timestamp formats:

- `[00:01:23] text`
- `00:01:23 - text`
- `[01:02] text`
- `01:02 text`

Validation requirements:

- At least 10 timestamped lines.
- Timestamps must be monotonic.
- No negative times.
- No segment gap larger than the configured warning threshold without warning.
- Transcript must preserve original text.
- Invalid lines are reported with line numbers and remediation guidance.

### Content brief

Fields:

- `brief_id`
- `name`
- `objective`
- `target_audience`
- `topic_angle`
- `desired_formats`
- `must_include`
- `must_avoid`
- `tone`
- `cta_goal`
- `brand_safety_notes`

### Account profile

Fields:

- `account_id`
- `name`
- `platform`
- `niche`
- `audience`
- `voice`
- `content_pillars`
- `format_preferences`
- `risk_tolerance`
- `cta_style`
- `brand_safety_rules`
- `historical_notes`

## Output formats

### Clip candidate

Each generated candidate must include:

- `candidate_id`
- `source_content_id`
- `start_time`
- `end_time`
- `duration_seconds`
- `transcript_excerpt`
- `reason_selected`
- `scores`
- `confidence`
- `generated_assets`
- `editing_notes`
- `status`

### Scores

Required scoring dimensions:

- Hook strength.
- Standalone clarity.
- Novelty.
- Emotional intensity.
- Shareability.
- Educational value.
- Brand safety.
- Editing complexity.
- Overall score.
- Confidence.

Score range: integer `1` to `5` for component dimensions; `0` to `100` for overall score; `0.0` to `1.0` for confidence.

The explanation must be concise and user-facing. Do not expose hidden chain-of-thought.

### Generated assets

For each candidate:

- 3 hooks.
- 2 titles.
- 2 captions.
- 1 CTA.
- Editing notes.
- Optional platform notes.

All generated assets are editable drafts.

## Main workflow

```text
Timestamped Transcript
        +
Content Brief
        +
Target Account Profile
        ↓
Transcript Validation
        ↓
Content Segmentation
        ↓
AI Moment Detection
        ↓
Clip Candidate Scoring
        ↓
Hook, Caption, Title, CTA, and Editing Notes
        ↓
Structured Output Validation
        ↓
Human Review
        ↓
Approval or Rejection
        ↓
Mock Publishing Queue
        ↓
Simulated Performance Data
        ↓
Fleet Dashboard
        ↓
Experiment Analysis
        ↓
Weekly Growth Recommendations
```

## Domain entities

| Entity | Purpose |
|---|---|
| `SourceContent` | Represents the original content item, such as a podcast episode, stream, webinar, or interview. |
| `Transcript` | Timestamped transcript attached to source content. |
| `TranscriptSegment` | Deterministic segment of a transcript, with start/end timestamps and text. |
| `ContentBrief` | User intent, audience, tone, goals, and constraints. |
| `AccountProfile` | Fictional account's platform, audience, voice, and safety constraints. |
| `ClipCandidate` | Proposed clip with timestamp range, excerpt, status, scores, and generated assets. |
| `ClipScore` | Score dimensions, overall score, confidence, and explanation. |
| `GeneratedAsset` | Hook, title, caption, CTA, or editing note draft. |
| `ReviewDecision` | Human approve/reject/edit decision with reason and reviewer notes. |
| `PublishingQueueItem` | Mock scheduled item for approved candidates. |
| `PerformanceRecord` | Simulated metrics for a queued or published candidate. |
| `ContentExperiment` | Experiment comparing content variables such as hook type or CTA style. |
| `WeeklyGrowthReport` | Summary of fleet performance, experiment findings, and next recommendations. |
| `WorkflowRun` | One end-to-end run with status, timings, errors, and linked model runs. |
| `ModelRun` | One model-provider call with prompt version, provider, model, token/cost estimate, raw output reference, validation status, and repair attempt count. |

## Status lifecycle

Clip candidate lifecycle:

```text
DETECTED
NEEDS_REVIEW
APPROVED
REJECTED
EDITING
READY_TO_PUBLISH
PUBLISHED
```

Rules:

- New model-generated candidates start as `DETECTED`.
- Candidates move to `NEEDS_REVIEW` only after schema and business validation pass.
- Only a human review decision can move a candidate to `APPROVED` or `REJECTED`.
- Editing an approved candidate moves it to `EDITING`.
- Queueing a candidate moves it to `READY_TO_PUBLISH`.
- Importing or assigning simulated published data may move it to `PUBLISHED`.

Invalid transitions must return a typed error.

## AI responsibilities

The AI may:

- Identify promising moments from validated transcript segments.
- Propose candidate timestamp ranges.
- Draft score explanations.
- Generate hooks, titles, captions, CTAs, and editing notes.
- Flag brand-safety concerns.
- Produce weekly recommendation drafts from structured metrics.

The AI must not:

- Publish automatically.
- Override human review.
- Invent performance data.
- Claim real-world growth from simulated records.
- Request or expose hidden chain-of-thought.
- Ignore account-profile safety rules.

## Human responsibilities

The human reviewer:

- Confirms candidates are contextually accurate.
- Edits generated assets.
- Approves or rejects candidates.
- Assigns rejection reasons.
- Confirms queue readiness.
- Interprets dashboard recommendations as simulated/demo guidance.

## Analytics metrics

### Content-performance metrics

- Views.
- Likes.
- Comments.
- Shares.
- Saves.
- Completion rate.
- Average watch percentage.
- Follower conversions.
- Engagement rate.
- View velocity in first 24 hours.

### Workflow metrics

- Transcript validation success rate.
- Candidates generated per run.
- Approval rate.
- Rejection reasons.
- Average review time.
- Model repair attempt rate.
- Processing success/failure rate.
- Estimated model cost per run.
- Cost per approved output.

### Fleet metrics

- Account health score.
- Approved clips by account.
- Published clips by account.
- Median engagement rate by account.
- Best-performing content pillar.
- Underperforming account flags.

Health scores must be transparent weighted rules, not opaque claims.

## Experiment model

Supported v1 experiment types:

- Hook type comparison.
- CTA style comparison.
- Content pillar comparison.
- Clip duration band comparison.

Experiment fields:

- `experiment_id`
- `name`
- `hypothesis`
- `variant_a`
- `variant_b`
- `metric_primary`
- `guardrail_metrics`
- `start_date`
- `end_date`
- `sample_size`
- `result_summary`
- `winner`
- `confidence_note`

Experiment language must avoid overclaiming. If sample size is small or simulated, say so plainly.

## Weekly report structure

Each `WeeklyGrowthReport` contains:

1. Week range.
2. Accounts covered.
3. Executive summary.
4. Fleet performance snapshot.
5. Top clips and why they worked.
6. Underperforming clips and likely issues.
7. Experiment readout.
8. Workflow operations metrics.
9. Recommended next experiment.
10. Content backlog suggestions.
11. Risks, caveats, and simulated-data disclosure.

## Error handling

Required typed error categories:

- `TRANSCRIPT_PARSE_ERROR`
- `TRANSCRIPT_VALIDATION_ERROR`
- `MODEL_PROVIDER_ERROR`
- `MODEL_OUTPUT_SCHEMA_ERROR`
- `MODEL_OUTPUT_REPAIR_FAILED`
- `BUSINESS_RULE_VALIDATION_ERROR`
- `INVALID_STATE_TRANSITION`
- `NOT_FOUND`
- `SIMULATED_DATA_IMPORT_ERROR`

Every API error response should include:

- Machine-readable code.
- Human-readable message.
- Relevant field or entity ID.
- Suggested next action where possible.

## Security and privacy considerations

V1 is local-first and demo-oriented. It should still:

- Avoid committing secrets.
- Provide `.env.example`.
- Treat transcripts and briefs as user-provided content.
- Never send private data to a model provider without explicit configuration.
- Log metadata instead of full sensitive prompts where practical.
- Keep simulated account data fictional.
- Avoid real client, employer, or confidential content in seed data.
- Disclose that performance data is simulated.

## Acceptance criteria

The POC is acceptable when:

- A user can create a workflow run from a valid timestamped transcript, brief, and account.
- The system generates at least six candidates.
- Each candidate has timestamps, excerpt, scores, confidence, explanation, and generated assets.
- Malformed model output triggers one repair attempt and then a clear failure if still invalid.
- A user can edit and approve or reject candidates.
- Approved candidates enter a mock publishing queue.
- Simulated performance data can be imported or seeded.
- Dashboard shows account and fleet metrics.
- An experiment compares at least two hook types.
- Weekly report proposes a next experiment with caveats.
- Tests cover parser, scoring, state transitions, model-output validation, API workflow, and one demo path.
- README and docs explain setup, demo, architecture, limitations, and simulated data.

## Definition of done

A feature is done only when:

- Scope matches the assigned ticket.
- Code is formatted and type/lint checks pass where configured.
- Relevant unit/integration/UI tests pass.
- At least one negative/error case is tested when applicable.
- Documentation is updated.
- Manual verification is recorded.
- Changed files and commands run are reported.
- Known limitations are stated.
- No prohibited scope was added.

## Final demo scenario

1. The user opens ClipOps.
2. The user uploads or pastes a timestamped transcript.
3. The user enters a content brief.
4. The user selects a fictional account.
5. ClipOps generates at least six clip candidates.
6. Each candidate has timestamps, scores, confidence, and a concise explanation.
7. ClipOps generates hooks, captions, titles, CTAs, and editing notes.
8. The user edits and approves three candidates.
9. The approved candidates enter a mock publishing queue.
10. Simulated performance data is imported.
11. The dashboard shows account health and fleet performance.
12. An experiment compares two hook types.
13. A weekly report identifies a winner and proposes the next experiment.
14. The repository clearly discloses simulated data and system limitations.

## Known limitations

- No real video processing.
- No automatic transcription.
- No real social publishing.
- No real account data.
- No authentication.
- No production deployment.
- No statistical proof of growth.
- No RAG or historical similarity search.
- AI output quality depends on provider, prompt, transcript quality, and human review.

## Roadmap

### v1 POC

- Transcript workflow.
- Human review.
- Mock publishing.
- Simulated analytics.
- Experiment tracker.
- Weekly report.

### v1.1 hardening

- Better validation fixtures.
- Prompt/version evaluation report.
- More realistic seed data.
- Accessibility pass.
- Docker Compose if setup friction is high.

### v2

- Video upload.
- Automatic transcription.
- FFmpeg clip preview/export.
- Historical clip retrieval.
- Platform-specific templates.

### Later

- Real scheduling integrations.
- Authentication.
- Team roles.
- Cloud deployment.
- External data connectors.
