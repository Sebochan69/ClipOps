# Model providers

AI calls use the local `ModelProvider` contract. `MockModelProvider` is deterministic and is the only provider used in tests. Every call is recorded as a `ModelRun` with provider, model, prompt version, validation status, repair count, optional raw-output reference, and token/cost estimates when available. Hosted providers are deferred.
