# Qwen2.5-7B AWQ S2 direct-semantic evidence

`DIRECT_SEMANTIC_QUALIFICATION_PASS` is a direct-runtime instrumentation and
within-run join qualification only.  It is `SEMANTIC_DIAGNOSTIC_ONLY` and
`NOT_FOR_NATIVE_TIMING`: the standalone baseline and clean G1 census remain
separate immutable performance evidence.

The run used frozen P3 AWQ S2/TEXT inputs and runtime source `ae560163…`.
Direct module hooks emitted observable NVTX identities for ATTENTION (including
Q/K/V/O and core), FFN (gate/up/down and core), NORM, and EMBEDDING_OUTPUT.
Uncertain kernels remain `UNKNOWN`; kernel names, duration, and historical
model maps were never used for semantic assignment.

The full 96,152-row external `DIRECT_SEMANTIC_MAP.tsv` and deterministic gzip
are hash-locked by [DIRECT_SEMANTIC_ARTIFACT_INDEX.tsv](DIRECT_SEMANTIC_ARTIFACT_INDEX.tsv).
There are 46,079 direct/unambiguous rows, 50,073 conservative `UNKNOWN` rows,
and zero ambiguous direct-range ties.  The within-run identity is `run_id +
kernel_rowid + correlation_id + stream + start_ns + end_ns`.

No clean-census row is joined by a different run's absolute timestamp.  Any
clean-to-diagnostic reconciliation belongs solely to Lane P through its
`EVENT_INPUT_CONTRACT`.  Direct coverage is diagnostic only: 47.490994% of
Prefill GPU time and 46.814151% of Decode GPU time.  It is not a performance
result, selector input, or evidence that missing operator/layer features lack
value.
