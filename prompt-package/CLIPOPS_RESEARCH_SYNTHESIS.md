# ClipOps Research Synthesis

Generated: 2026-07-26  
Purpose: convert relevant AI Brain knowledge into implementation decisions and prompt constraints for a ClipOps proof of concept.

This document distinguishes:

- Retrieved knowledge: principles found in the AI Brain pages listed below.
- Synthesis: project-specific interpretation of those principles for ClipOps.
- Recommendation: the concrete decision pi.dev should follow unless the owner approves a change.

## A. Executive Summary

The AI Brain strongly supports building ClipOps as a small, evidence-producing product system rather than as a broad agent demo. The important retrieved patterns are:

- Use a ticket/stage-contract workflow. The coding agent should read a bounded context package, implement one approved ticket, run explicit checks, report evidence, and stop. This comes from the harness, stage-contract, handoff, and AI-assisted coding notes.
- Treat AI output as a proposal, not truth. Pydantic schemas and JSON validation can enforce structure, but they cannot prove that a clip is actually good, safe, or supported by the transcript.
- Keep deterministic work in code. Transcript parsing, timestamp validation, lifecycle transitions, scoring aggregation, dashboard math, and simulated-data labeling should be ordinary tested software. Use the LLM only for moment judgment and content asset drafting.
- Add RAG later, not in Version 1. ClipOps v1 has one active transcript, content brief, account profile, and generated outputs. Retrieval becomes useful only after historical clips, hooks, playbooks, or account performance records exist and have enough metadata to retrieve against.
- Prefer a modular monolith. FastAPI, Pydantic, SQLAlchemy, SQLite, a replaceable model-provider interface, and a React/TypeScript frontend are enough. Microservices, cloud infrastructure, full video processing, Graphify, MLflow, n8n, and custom training should be deferred.
- Make analytics honest. Use transparent definitions for view velocity, completion rate, engagement rate, approval rate, cost per approved output, and experiment readouts. Simulated performance data must be labeled as simulated, and ClipOps must avoid unsupported growth or causal claims.
- Design the demo for review speed. The repo should show the workflow in five minutes: transcript in, six candidates out, three approvals, mock queue, simulated metrics, experiment winner, weekly recommendation, limitations disclosed.

## B. Retrieved Knowledge by Area

### Agentic development

| Source file or knowledge location | Relevant principle | How it applies to ClipOps | Priority |
|---|---|---|---|
| `wiki/harness-loop/concepts/Stage Contract.md` | One bounded workflow transformation should define goal, inputs, process, outputs, authority, and review. | Every pi.dev task should be a single ticket with explicit non-scope, inputs, outputs, tests, and acceptance criteria. | Required |
| `wiki/harness-loop/concepts/Reference and Working Context Separation.md` | Separate stable rules from per-run task material. | Keep `CLIPOPS_MASTER_SPEC.md`, `AGENTS.md`, and ADRs as stable reference; feature prompts supply only ticket-specific working context. | Required |
| `wiki/harness-loop/concepts/Agent Session Continuity and Handoff.md` | A fresh agent session should resume from durable project state, decisions, evidence, blockers, and next action instead of chat history. | pi.dev must update backlog status or a completion report with changed files, tests, decisions, known limits, and next suggested ticket. | Required |
| `wiki/harness-loop/concepts/Agent Observability.md` | A completion message is a claim; acceptance needs tests, external signals, or human judgment. | pi.dev must include test outputs and manual verification notes before claiming a feature is done. | Required |
| `wiki/harness-loop/patterns/Agent Orchestration Patterns.md` | Use parallel or multi-agent work only when boundaries, handoffs, and ownership are explicit. | Default to one builder. Add reviewer/critic roles only after the builder finishes a ticket. Avoid many parallel agents early. | Required |
| `wiki/harness-loop/patterns/Minimum Viable Agent Loop.md` | Automate one recurring, machine-checkable task with a hard gate, state, and stop rule. | ClipOps should implement one workflow path first and require deterministic gates before adding richer automation. | Recommended |
| `wiki/ai-ml-library/sources/Source - Beyond Vibe Coding.md` | AI-assisted engineering starts with intent, constraints, acceptance criteria, review, tests, and human ownership. | The pi.dev bootstrap prompt must prohibit one-shot full builds and require ticket-based delivery. | Required |

### Architecture

| Source file or knowledge location | Relevant principle | How it applies to ClipOps | Priority |
|---|---|---|---|
| `wiki/system-design/concepts/Backend Engineering.md` | Backend service anatomy: routes, typed validation, DI, DB sessions, background work boundaries, deployment concerns. | Use FastAPI routers by domain, Pydantic schemas at the boundary, SQLAlchemy repositories/services, and clear in-process task limits. | Required |
| `wiki/system-design/concepts/FastAPI.md` | Type hints and dependencies define and document the HTTP API. | Use typed request/response models and generated OpenAPI docs as part of the portfolio value. | Required |
| `wiki/system-design/concepts/API Design Contract.md` | API contracts include resources, schemas, errors, idempotency, pagination/filtering, compatibility, and operations. | Define stable endpoints for transcripts, workflow runs, candidates, review decisions, queue items, metrics, experiments, and reports. | Required |
| `wiki/ai-ml-library/sources/Source - Building Generative AI Services with FastAPI.md` | Keep web orchestration separable from heavy inference; add persistence only when state must survive restarts; test deterministic seams and probabilistic behavior separately. | ClipOps uses hosted/mock provider calls behind an interface, stores workflow state, and does not load local LLMs in FastAPI. | Recommended |
| `wiki/cloud-devops/concepts/CI-CD for Cloud Infrastructure.md` | GitHub Actions should run build/test gates and handle secrets carefully; artifacts are not releases. | Add a simple CI workflow for backend tests, frontend build/tests, and lint/type checks. No deployment secrets in v1. | Recommended |

### AI workflow

| Source file or knowledge location | Relevant principle | How it applies to ClipOps | Priority |
|---|---|---|---|
| `wiki/llm-engineering/sources/Source - Learning LangChain.md` | Increase agency only with stronger state, bounded tools, human control, structured output, and trajectory tests. | Use LangGraph for explicit workflow state and nodes, not as an excuse for an autonomous free-form agent. | Required |
| `wiki/llm-engineering/sources/Source - LangGraph Repository.md` | LangGraph is a low-level framework for stateful, long-running workflows; builder retains control. | Use a small graph for validation → segmentation → moment detection → asset generation → validation/repair. | Recommended |
| `wiki/harness-loop/concepts/Tool Contract.md` | Tool contracts require typed inputs, outputs, errors, authority, side effects, and evidence. | Model-provider calls, transcript parser, scorer, repair step, and queue transition functions need explicit contracts. | Required |
| `wiki/llm-engineering/concepts/LLM-as-a-Judge Evaluation.md` | Model judges are fallible measurement instruments, not ground truth. | If a reviewer prompt scores candidates later, calibrate it against fixtures and do not treat it as final proof. | Optional |
| `wiki/ai-security/concepts/AI Trustworthiness Testing.md` | Trustworthiness tests should record failure property, component, expected safe behavior, result, severity, and retest date. | Add prompt-injection-like transcript fixtures, malformed output fixtures, unsafe claim tests, and brand-safety checks. | Recommended |

### Analytics

| Source file or knowledge location | Relevant principle | How it applies to ClipOps | Priority |
|---|---|---|---|
| `wiki/ai-ml-library/sources/Source - Lean Analytics.md` | Choose one metric for the current risk, define thresholds before collecting results, and distinguish actionable from vanity metrics. | Use weekly report recommendations tied to explicit metrics, thresholds, and next experiments; avoid generic "grow faster" advice. | Required |
| `wiki/ai-ml-library/sources/Source - AI-Powered Business Intelligence.md` | Dashboards can surface associations but do not establish causes; prototypes need realistic data and acceptance criteria. | Dashboard should label simulated data and explain that experiment winners are directional unless sample size and design support stronger claims. | Required |
| `wiki/ai-ml-library/sources/Source - Building AI-Powered Products.md` | Product, system, and AI-proxy metrics answer different questions. | Track content/account outcomes, workflow reliability, and model-output quality separately. | Required |
| `wiki/harness-loop/concepts/Agent Observability.md` | Operational metrics include cost, latency, retries, failures, and human acceptance. | Track processing success rate, approval rate, review latency, repair attempts, and model-run cost estimates. | Recommended |

### Content systems

| Source file or knowledge location | Relevant principle | How it applies to ClipOps | Priority |
|---|---|---|---|
| `wiki/ai-ml-library/sources/Source - Using Generative AI for SEO.md` | Use models for brainstorming, summarizing, drafting, and classification, but accountable experts must own publishable content. | Generated hooks, captions, titles, CTAs, and editing notes must enter human review before queueing. | Required |
| `wiki/ai-ml-library/sources/Source - Using Generative AI for SEO.md` | Content should add organization-specific evidence, experience, perspective, or utility instead of generic restatement. | Clip candidates should be scored for standalone clarity, novelty, educational value, and brand fit, not just "viral" language. | Recommended |
| `wiki/ai-ml-library/sources/Source - Designing AI Interfaces.md` | Outputs should be clear, verifiable, grounded, actionable, and adjustable. | Clip candidate cards must show timestamps, transcript excerpt, scores, rationale, editable assets, and review controls. | Required |

### Testing

| Source file or knowledge location | Relevant principle | How it applies to ClipOps | Priority |
|---|---|---|---|
| `wiki/ai-ml-library/sources/Source - Building Generative AI Services with FastAPI.md` | Use unit, integration, behavioral, and end-to-end evidence; mocks reduce cost but do not prove real providers. | Add pytest unit tests for parsers/scoring/state transitions, API tests, mock-model workflow tests, and one demo E2E. | Required |
| `wiki/ai-ml-library/sources/Source - Beyond Vibe Coding.md` | Generated code and generated tests can share the same misunderstanding. | Tests should be derived from `CLIPOPS_MASTER_SPEC.md` and fixtures, not only from pi.dev's implementation. | Required |
| `wiki/harness-loop/patterns/Prompt Optimization Loop.md` | Prompt changes need frozen versions, evaluation splits, cost/latency records, and rollback targets. | Version the moment-detection and asset-generation prompts; defer automated prompt optimization until enough examples exist. | Recommended |
| `wiki/ai-security/concepts/AI Trustworthiness Testing.md` | Passing one test is evidence for one version under stated conditions, not permanent safety. | Model prompts, provider versions, and scoring rubrics should be stored with `ModelRun` records. | Recommended |

### Frontend

| Source file or knowledge location | Relevant principle | How it applies to ClipOps | Priority |
|---|---|---|---|
| `wiki/ai-ml-library/sources/Source - Designing AI Interfaces.md` | AI interfaces need visible plans, layered progress, reviewable outputs, permission gates, checkpoints, and editing. | Build a review queue and dashboard that make the workflow understandable, not just a text dump of model outputs. | Required |
| `wiki/ai-ml-library/sources/Source - Applied Natural Language Processing in the Enterprise.md` | Streamlit is useful for exposing models to nontechnical reviewers early, but the source treats it as prototype, not production frontend. | Streamlit is viable for speed but less aligned with the polished portfolio app goal. | Optional |
| `wiki/ai-ml-library/sources/Source - RAG with Python Cookbook.md` | Streamlit, Chroma, local files, and manual deployment are prototype accelerators, not proof of durable product readiness. | If React can be kept small, prefer React/TypeScript for demo polish and product credibility. | Recommended |

### Documentation

| Source file or knowledge location | Relevant principle | How it applies to ClipOps | Priority |
|---|---|---|---|
| `wiki/ai-ml-library/sources/Source - Building AI-Powered Products.md` | AI products need use-case, user value, tradeoffs, metrics, responsible-AI questions, and rollout/maintenance ownership. | README and docs should describe problem, workflow, architecture, tradeoffs, metrics, limits, and demo script. | Required |
| `wiki/cloud-devops/sources/Source - GitHub for Data Engineering.md` | GitHub portfolio projects benefit from branches, PRs, CI checks, and clear documentation, but beginner guides are incomplete. | Use as portfolio workflow support only; rely on stronger CI/CD and testing gates for actual quality. | Recommended |
| `wiki/harness-loop/concepts/Agent Session Continuity and Handoff.md` | Handoffs require decisions, verification evidence, blockers, and next safe action. | Every pi.dev completion report must document changed files, checks run, known limitations, and next ticket. | Required |

## C. Conflicts and Gaps

### Conflicting or bounded guidance

- Streamlit versus React: the vault supports Streamlit as a fast prototype surface, but the interface/product notes favor reviewable, adjustable, polished product experiences. Recommendation is React/TypeScript for ClipOps, with strict scope control.
- LangChain versus direct SDK: LangChain is useful for integrations, but the harness notes favor explicit inspectable control. Recommendation is direct provider SDK behind a local interface plus LangGraph for stateful workflow only.
- Structured output: several sources recommend Pydantic/JSON schemas, but the RAG and FastAPI sources warn that schema validity is not semantic truth. Recommendation is schema validation plus transcript reference checks and human review.
- RAG: RAG sources provide strong lifecycle guidance, but the content and SEO source contains RAG simplifications and even a logged conflict about RAG being conflated with training. Recommendation is no RAG in v1.
- Analytics: Lean Analytics and BI sources are useful but include historical benchmarks and causal caveats. Recommendation is explicit metric definitions and no causal/growth guarantees.

### Missing knowledge

- The vault lacks a dedicated, validated short-form content operations source for TikTok/Reels/Shorts moment detection, hook taxonomies, platform-specific editorial patterns, or account-fleet management.
- No meaningful Graphify source was found. Treat Graphify as a later architecture-audit option only if the future repo needs graph-based architecture inspection.
- No direct `uv` packaging note was found. `uv` remains a user-provided architectural default, not an AI Brain-derived recommendation.
- No direct, current React-versus-Streamlit comparison source was found. The React recommendation is synthesis from portfolio/product-interface goals.
- No current pi.dev-specific operating guide was available in the AI Brain. The pi.dev prompts are built from general coding-agent, harness, and handoff principles.

### Outdated or currentness-sensitive material

- LangGraph/LangChain, model-provider APIs, Streamlit, FastAPI/SQLAlchemy details, and GitHub Actions behavior are fast-moving. pi.dev should verify current official docs during implementation.
- Several source pages are text-only reviews and explicitly warn that code listings were not executed.
- Analytics benchmark values from Lean Analytics are not suitable as 2026 social-platform thresholds.

## D. Final Recommendations

### What ClipOps should use

- Backend: Python 3.11+, FastAPI, Pydantic, SQLAlchemy, SQLite, repository/service layering, typed API contracts, `.env.example`.
- AI workflow: LangGraph for a small explicit state graph; direct hosted-model SDK behind a replaceable `ModelProvider`; `MockModelProvider` for tests.
- Frontend: React with TypeScript, kept small and focused on review queue, candidate detail, publishing queue, dashboard, experiment report, and weekly recommendation.
- Testing: pytest, deterministic transcript fixtures, mock provider, API tests, workflow/state-transition tests, malformed-output repair tests, frontend component/flow tests, and one scripted E2E demo.
- Documentation: README, master spec, ADRs, demo script, simulated-data disclosure, limitations, and evaluation report.

### What ClipOps should avoid

- One-shot implementation by pi.dev.
- Full video processing, FFmpeg, transcription, automatic social posting, authentication, cloud deployment, microservices, custom model training, autonomous publishing, and major dependency additions without approval.
- Treating scores, model confidence, LLM judges, or dashboards as proof of real growth.
- Hidden chain-of-thought requests. Use concise user-facing rationales and evidence links instead.

### What should be deferred

- RAG/embeddings for historical clips and playbooks.
- MLflow or formal experiment tracking beyond simple database records.
- n8n automation.
- Graphify architecture audit.
- Docker Compose, unless setup friction becomes a blocker.
- Full video upload/transcription/clipping.

### Essential practices for pi.dev

1. Read `AGENTS.md`, `CLIPOPS_MASTER_SPEC.md`, `CLIPOPS_ARCHITECTURE_DECISIONS.md`, and `CLIPOPS_TICKET_BACKLOG.md`.
2. Implement one ticket at a time.
3. Preserve existing architecture unless the ticket requires a change.
4. Add or update tests with every feature.
5. Report changed files, commands run, test output, manual verification, and limitations.
6. Stop after the assigned ticket and wait for approval before expanding scope.
