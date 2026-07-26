# Structured-output repair

Parsed model output is validated once, repaired once on validation failure, then validated again. A second failure raises `MODEL_OUTPUT_REPAIR_FAILED`; no unlimited retry occurs. `ModelRun.repair_count` records whether repair was used.
