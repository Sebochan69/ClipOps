# Moment detection

Prompt `backend/prompts/moment-detection-v1.md` requires at least six structured candidate moments. The mock provider returns deterministic output; Pydantic validates timestamps, excerpts, and concise reasons before six `DETECTED` candidates are persisted. Real-provider integration and one-attempt repair are deferred.
