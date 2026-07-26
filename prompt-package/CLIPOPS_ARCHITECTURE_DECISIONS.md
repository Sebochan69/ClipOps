# ClipOps Architecture Decisions

These are initial decisions for the ClipOps POC. Revisit only when the listed trigger occurs or the owner approves a change.

## ADR-001 — Frontend: React with TypeScript over Streamlit

- Context: ClipOps needs a review queue, editable content assets, dashboard, experiment readout, and a polished five-minute portfolio demo.
- Options: Streamlit; React with TypeScript.
- Decision: use React with TypeScript.
- Rationale: Streamlit is faster for prototypes, but the AI Brain treats it as a prototype surface. ClipOps benefits from product polish, custom review states, and a SaaS-like dashboard.
- Consequences: more setup and frontend testing than Streamlit; better portfolio signal and UI control.
- Revisit trigger: if frontend work blocks core workflow delivery, consider a smaller React scope rather than switching frameworks.

## ADR-002 — Database: SQLite for v1, PostgreSQL-ready schema

- Context: v1 is local-first and demo-oriented but should not paint itself into a corner.
- Options: SQLite; PostgreSQL.
- Decision: use SQLite in v1 with SQLAlchemy models that can migrate to PostgreSQL later.
- Rationale: SQLite reduces setup friction and supports local demos; SQLAlchemy keeps persistence patterns portable.
- Consequences: avoid database-specific features; tests should not assume PostgreSQL-only behavior.
- Revisit trigger: concurrent users, hosted deployment, advanced analytics queries, or queue durability requirements.

## ADR-003 — LLM provider: direct SDK behind local interface over LangChain default

- Context: ClipOps needs replaceable provider calls, structured output, and mock testing.
- Options: direct provider SDK; LangChain as primary abstraction.
- Decision: use a local `ModelProvider` interface with direct SDK implementations and a `MockModelProvider`.
- Rationale: explicit contracts are easier to test and inspect. LangChain can be added later for a specific integration, not as default ceremony.
- Consequences: more local interface code; less framework coupling.
- Revisit trigger: multiple providers or tools create enough repeated integration work to justify LangChain.

## ADR-004 — Workflow: LangGraph over a simple service pipeline, but narrowly

- Context: The requested default is LangGraph, and ClipOps has a natural stateful workflow.
- Options: plain service pipeline; LangGraph graph.
- Decision: use LangGraph for a small explicit workflow graph.
- Rationale: validation, segmentation, moment detection, asset generation, repair, and persistence form a useful graph/state machine. Keep deterministic rules in services.
- Consequences: adds framework dependency and learning curve; graph should stay small.
- Revisit trigger: if graph complexity exceeds value or tests become harder than an explicit service pipeline.

## ADR-005 — Model hosting: hosted model over local model

- Context: ClipOps is a portfolio POC, not an inference-systems project.
- Options: local model; hosted model; mock only.
- Decision: implement mock provider for tests and a hosted provider path for optional real runs.
- Rationale: local models add hardware, packaging, latency, and quality variability. Hosted models keep focus on workflow design.
- Consequences: real runs require API key and cost disclosure; CI uses mock provider.
- Revisit trigger: offline demo requirement, privacy constraint, or cost issue.

## ADR-006 — Embeddings/RAG: not needed in v1

- Context: ClipOps v1 operates on one active transcript, brief, and account profile.
- Options: no RAG; embeddings over current transcript; historical retrieval.
- Decision: no embeddings or RAG in v1.
- Rationale: segmentation and active-context prompting cover the current transcript. RAG becomes valuable when historical clips, hooks, playbooks, and account results exist.
- Consequences: simpler architecture; no similar-clip retrieval initially.
- Revisit trigger: at least 50 historical clip records or playbooks with metadata and a user story requiring similarity retrieval.

## ADR-007 — MLflow: defer

- Context: v1 needs prompt/model-run traceability, not full experiment-management infrastructure.
- Options: no MLflow; MLflow for prompt/model tracking.
- Decision: defer MLflow.
- Rationale: database `ModelRun` records and docs are enough for v1. MLflow would add setup weight before there are real model experiments.
- Consequences: simpler local setup; less formal model registry.
- Revisit trigger: repeated prompt/model comparisons, real provider benchmarks, or multiple model artifacts.

## ADR-008 — n8n: defer from core app

- Context: ClipOps is itself demonstrating content operations workflow. n8n could automate external handoffs later.
- Options: include n8n; defer n8n.
- Decision: defer n8n.
- Rationale: v1 has no external posting or client automation. n8n would add credential, hosting, and workflow-operation surface without improving the core demo.
- Consequences: mock publishing queue only.
- Revisit trigger: real platform integrations, scheduled handoffs, or client automation workflows.

## ADR-009 — Graphify: later architecture-audit tool only

- Context: The AI Brain search found no meaningful Graphify source.
- Options: include Graphify; defer.
- Decision: defer and treat as later architecture audit if useful.
- Rationale: no current project requirement or validated source justifies it.
- Consequences: architecture will be documented through ADRs and diagrams instead.
- Revisit trigger: repository grows enough that automated architecture graphing would reveal dependency or ownership drift.

## ADR-010 — Docker: optional after native local setup

- Context: Local-first development should be easy.
- Options: native setup only; Docker Compose immediately; Docker later.
- Decision: start native local setup; add Docker Compose only if setup friction appears.
- Rationale: v1 uses SQLite, FastAPI, React, and mock provider. Docker is useful but not essential.
- Consequences: README must make native setup reliable.
- Revisit trigger: onboarding friction, CI mismatch, or need for a reproducible demo environment.

## ADR-011 — Architecture shape: modular monolith over microservices

- Context: ClipOps has several domains but one small team, one local database, and no scale requirement.
- Options: modular monolith; microservices.
- Decision: modular monolith.
- Rationale: service boundaries can be represented by modules, routers, schemas, and services without distributed-system costs.
- Consequences: simpler testing and local demo; modules must stay clean.
- Revisit trigger: independently deployable workloads, real queue workers, external integrations, or team boundaries.
