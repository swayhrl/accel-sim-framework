# C16 scenario and token policy

`S0`–`S4` are frozen pre-execution identities, not measured runs.  Every
receipt starts from one versioned raw input in `inputs/`, tokenizes it with the
deployment's immutable tokenizer using `local_files_only=true`,
`trust_remote_code=false`, and `add_special_tokens=false`, then repeats the
real source IDs and trims exactly to the stated prefill length.  The receipt
stores both source and target IDs, hashes, tokenizer asset hashes, and the
Transformers version.

Decode is intended to be deterministic greedy decoding (`do_sample=false`)
when G's native runner becomes available.  The runner must emit its actual
generation, attention/KV, dtype, parallelism, and feature identity; the policy
does not assert that an unexecuted backend honored these settings.

S2 has all three frozen input classes for MoE deployments so routing can later
be audited across multiple exact inputs.  It does not assert expert routing,
MoE width, cache behavior, or performance.  S3/S4 must be reported as
`SKIPPED_RESOURCE` if resource admission fails; their dimensions may not be
silently reduced.
