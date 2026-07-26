# Business validation

Before a candidate can enter `NEEDS_REVIEW`, ClipOps verifies timestamp/duration consistency (1–90 seconds), a brand-safety score of at least 3, account safety rules, and the complete generated-asset set. Failures raise `BUSINESS_RULE_VALIDATION_ERROR` with field-specific violations.
