# ClipOps Context Manifest

Generated: 2026-07-26  
Purpose: compact audit trail of AI Brain material used to build the ClipOps prompt package.

## Retrieval summary

- AI Brain pages/files opened or inspected: 40.
- Sources materially used in generated decisions/prompts: 25.
- Non-AI-Brain input used: the user-supplied ClipOps task brief.
- Web browsing: none. This package intentionally relies on the AI Brain plus the user's architectural defaults.

## Sources used

| File path or note title | Topic | Why it was relevant | Generated files using it | Relevance confidence | Currentness |
|---|---|---|---|---|---|
| `wiki/Wiki Index.md` | Vault routing | Starting point for relevant neighborhoods. | Research synthesis, manifest | High | Current index dated 2026-07-26 |
| `wiki/harness-loop/Harness & Loop Engineering Index.md` | Agent harness routing | Identified core agent workflow, guardrail, handoff, and orchestration pages. | Research synthesis, AGENTS, prompt templates | High | Current enough |
| `wiki/harness-loop/concepts/Stage Contract.md` | Bounded agent tasks | Supported one-ticket-at-a-time prompt design. | AGENTS, bootstrap prompt, feature template | High | Current enough |
| `wiki/harness-loop/concepts/Reference and Working Context Separation.md` | Context engineering | Supported stable project docs versus ticket-specific prompts. | Research synthesis, AGENTS, feature template | High | Current enough |
| `wiki/harness-loop/concepts/Agent Session Continuity and Handoff.md` | Handoff pattern | Supported completion-report and evidence requirements. | AGENTS, bootstrap prompt, review prompt | High | Current enough |
| `wiki/harness-loop/concepts/Agent Context Management.md` | Context selection | Supported minimal context and just-in-time file loading. | AGENTS, bootstrap prompt | High | Current enough |
| `wiki/harness-loop/concepts/Agent Observability.md` | Evidence before completion | Supported test-output and operational-metric requirements. | Research synthesis, AGENTS, backlog | High | Current enough |
| `wiki/harness-loop/concepts/Agent Guardrails.md` | Safety controls | Supported approval gates, untrusted-content handling, and prohibited scope. | AGENTS, master spec | High | Current enough |
| `wiki/harness-loop/concepts/Tool Contract.md` | Typed tool contracts | Supported model-provider and workflow function contracts. | Master spec, ADRs, feature template | High | Current enough |
| `wiki/harness-loop/patterns/Agent Orchestration Patterns.md` | Sub-agent/parallel work | Supported restrained sub-agent strategy and parallel-work rules. | AGENTS, research synthesis, review prompt | High | Current enough |
| `wiki/harness-loop/patterns/Minimum Viable Agent Loop.md` | Small reliable automation | Supported small coherent v1 scope. | Research synthesis, backlog | High | Current enough |
| `wiki/harness-loop/patterns/Prompt Optimization Loop.md` | Prompt evaluation | Supported prompt versioning and deferring optimization until examples exist. | Research synthesis, backlog | Medium | Current enough |
| `wiki/harness-loop/sources/Source - Learn Harness Engineering.md` | Harness course source | Supported externalized state, verification, and session lifecycle. | Research synthesis, AGENTS | High | Educational, not production proof |
| `wiki/ai-ml-library/sources/Source - Beyond Vibe Coding.md` | AI-assisted coding | Supported anti-one-shot, testing, review, and human ownership rules. | AGENTS, bootstrap prompt, review prompt | High | Fast-moving 2025 tool snapshot |
| `wiki/system-design/System Design Index.md` | System architecture routing | Identified backend/API/FastAPI concepts. | Research synthesis, ADRs | High | Current enough |
| `wiki/system-design/concepts/Backend Engineering.md` | Backend service anatomy | Supported FastAPI routers, validation, DI, DB session, background-task boundaries. | Master spec, ADRs, backlog | High | Current enough |
| `wiki/system-design/concepts/FastAPI.md` | FastAPI concepts | Supported typed endpoint and OpenAPI approach. | Master spec, ADRs | High | Captured 2026-07-10 |
| `wiki/system-design/concepts/API Design Contract.md` | API contracts | Supported endpoint/resource/error/idempotency requirements. | Master spec, feature template | High | Current enough |
| `wiki/ai-ml-library/sources/Source - Building Generative AI Services with FastAPI.md` | GenAI FastAPI architecture | Supported Pydantic contracts, SQLAlchemy/repository pattern, mock/provider testing, Docker deferral. | Research synthesis, master spec, ADRs, backlog | High | 2025 source; current docs should be rechecked |
| `wiki/cloud-devops/concepts/CI-CD for Cloud Infrastructure.md` | GitHub Actions and CI/CD | Supported local evidence gates and simple GitHub Actions recommendation. | AGENTS, backlog, ADRs | High | Captured 2026-07-06/10 |
| `wiki/cloud-devops/sources/Source - GitHub for Data Engineering.md` | Git/GitHub portfolio workflow | Supported branch/PR/check/documentation portfolio pattern with caveats. | Research synthesis | Medium | Undated beginner guide |
| `wiki/llm-engineering/LLM Engineering Index.md` | LLM engineering routing | Identified LangGraph, RAG, evaluation sources. | Research synthesis, ADRs | High | Current index |
| `wiki/llm-engineering/architectures/Production LLM Lifecycle.md` | LLM lifecycle | Supported versioned data/prompt/model/evaluation artifacts. | Research synthesis, master spec | High | Current enough |
| `wiki/llm-engineering/sources/Source - Learning LangChain.md` | LangGraph, structured output, human control | Supported narrow LangGraph use, structured output, and testing trajectory. | ADRs, master spec, backlog | High | 2025; fast-moving framework |
| `wiki/llm-engineering/sources/Source - LangGraph Repository.md` | LangGraph repository snapshot | Supported LangGraph as low-level stateful workflow framework. | ADRs, research synthesis | Medium | README-only snapshot from 2026-07-09 |
| `wiki/llm-engineering/sources/Source - LangChain Repository.md` | LangChain repository snapshot | Supported direct-SDK-over-default-LangChain decision. | ADRs, research synthesis | Medium | README-only snapshot from 2026-07-09 |
| `wiki/concepts/Retrieval-Augmented Generation.md` | RAG definition | Supported deferring RAG until retrieval need exists. | Research synthesis, ADRs | High | Current enough |
| `wiki/llm-engineering/concepts/RAG Operations.md` | RAG lifecycle | Supported no-RAG-v1 and future historical-clip retrieval criteria. | ADRs, master spec | High | Current enough |
| `wiki/llm-engineering/concepts/Vector Database Selection.md` | Vector-store criteria | Supported deferring vector database until workload exists. | ADRs | Medium | README-depth repo sources |
| `wiki/llm-engineering/concepts/LLM-as-a-Judge Evaluation.md` | Judge limitations | Supported reviewer prompt and avoiding model-judge truth claims. | Research synthesis, review prompt | High | Current enough |
| `wiki/ai-security/concepts/AI Trustworthiness Testing.md` | AI test contracts | Supported malformed-output, prompt-injection, and safety fixture recommendations. | Research synthesis, backlog | High | Current enough |
| `wiki/llm-engineering/concepts/n8n.md` | Workflow automation | Supported deferring n8n from v1 core app. | ADRs | Medium | Usable, but integration pages incomplete |
| `wiki/ai-ml-library/sources/Source - Lean Analytics.md` | Analytics and experiments | Supported OMTM, thresholds, and avoiding vanity metrics. | Master spec, research synthesis, backlog | High | Historical examples; framework still useful |
| `wiki/ai-ml-library/sources/Source - AI-Powered Business Intelligence.md` | Dashboard/prototype analytics | Supported dashboard caveats, association-not-causation, and simulated-data honesty. | Master spec, research synthesis, product critic prompt | High | 2022 Microsoft stack is dated |
| `wiki/ai-ml-library/sources/Source - Building AI-Powered Products.md` | AI product management | Supported user-outcome-first design, metric blend, responsible AI, and portfolio scope. | Master spec, research synthesis, product critic prompt | High | 2025 practitioner source |
| `wiki/ai-ml-library/sources/Source - Designing AI Interfaces.md` | AI UX and shared control | Supported React UI requirements, editable outputs, progress/error states, and human review. | Master spec, ADRs, backlog, product critic prompt | High | Product snapshots may decay |
| `wiki/ai-ml-library/sources/Source - Using Generative AI for SEO.md` | AI-assisted content workflow | Closest content-system source; supported human ownership, expert review, and avoiding generic AI content. | Master spec, research synthesis | Medium | SEO-specific and currentness-sensitive |
| `wiki/ai-ml-library/sources/Source - Applied Natural Language Processing in the Enterprise.md` | NLP prototyping and Streamlit boundary | Supported Streamlit-as-prototype caveat and pretrained/simple-baseline mindset. | ADR-001, research synthesis | Medium | 2021 stack is dated |

## Important gaps

- No dedicated short-form content operations source was found for TikTok/Reels/Shorts workflows, hook taxonomies, or creator account fleet operations.
- No meaningful Graphify source was found.
- No direct `uv` source was found.
- No direct current React-versus-Streamlit comparison source was found.
- No pi.dev-specific source was found; prompts are based on general coding-agent and harness patterns.

## Manifest note

This manifest is for auditability. pi.dev should not need access to the AI Brain. The relevant decisions and constraints have been copied into the generated project documents.
