# pi.dev Technical Review Prompt

You are reviewing a ClipOps implementation. Do not rewrite the project automatically. First produce a review report, then a focused remediation plan.

## Required context

Read:

1. `AGENTS.md`
2. `CLIPOPS_MASTER_SPEC.md`
3. `CLIPOPS_ARCHITECTURE_DECISIONS.md`
4. The implemented ticket prompt or backlog ticket
5. The changed files and relevant tests

## Review goals

Evaluate:

- Correctness.
- Architecture fit.
- Scope compliance.
- Test coverage.
- Error handling.
- LLM reliability.
- UX clarity.
- Analytics honesty.
- Documentation.
- Hiring-manager value.

## Issue severity

Classify each issue:

- Critical: breaks core workflow, data integrity, safety boundary, or explicit acceptance criteria.
- High: likely user-visible failure, major test gap, architecture drift, or unsupported claim.
- Medium: maintainability, incomplete edge case, unclear UX, or moderate documentation gap.
- Low: minor cleanup, naming, small docs improvement, or local polish.
- Optional: nice-to-have improvement outside the ticket's required scope.

## Review report format

Produce:

1. Overall verdict: Pass / Pass with fixes / Needs remediation / Blocked.
2. Scope compliance summary.
3. Architecture fit summary.
4. Test evidence summary.
5. Issues table:
   - Severity.
   - File/path.
   - Finding.
   - Why it matters.
   - Suggested fix.
6. Missing evidence.
7. Unsupported or overstated claims.
8. Positive notes worth preserving.

## Remediation plan format

After the report, provide a focused plan:

1. Critical fixes first.
2. High fixes next.
3. Medium/Low fixes only if they are in-scope.
4. Tests to add or rerun.
5. Documentation updates.

Do not propose a broad rewrite unless the current implementation cannot meet the ticket acceptance criteria without it.

Limit review loops to three focused iterations unless a critical issue remains.
