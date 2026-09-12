# Qwen2.5-0.5B S2 direct-semantic evidence

`DIRECT_SEMANTIC_QUALIFICATION_PASS` applies only to diagnostic instrumentation
and within-run join qualification.  This is `SEMANTIC_DIAGNOSTIC_ONLY` and
`NOT_FOR_NATIVE_TIMING`; the closed standalone baseline and clean G1 census were
not rerun or modified.

The immutable runtime source is `b241fecfe5cd78bc2cdbb733e3a437d68b741c89`.
The fixed P1 model/revision/input/back-end made one warmup plus one instrumented
cache-correct decode without retained timing samples.  Direct module hooks emit
NVTX identities for `ATTENTION`, `FFN`, `NORM`, and `EMBEDDING_OUTPUT`.

The full 70,224-row external `DIRECT_SEMANTIC_MAP.tsv` and deterministic gzip
are hash-locked by [DIRECT_SEMANTIC_ARTIFACT_INDEX.tsv](DIRECT_SEMANTIC_ARTIFACT_INDEX.tsv).
There are 33,184 direct/unambiguous rows, 37,040 conservative `UNKNOWN` rows,
and zero equal-width direct-range conflicts.  The stable diagnostic join key is
`run_id + kernel_rowid + correlation_id + stream + start_ns + end_ns`.

No different-run absolute timestamp is joined to clean census data.  Any
clean-to-diagnostic reconciliation is solely Lane P's `EVENT_INPUT_CONTRACT`
work.  Kernel names, durations, and historical model mappings are forbidden
from semantic assignment.  [SEMANTIC_COVERAGE.tsv](SEMANTIC_COVERAGE.tsv) is
diagnostic coverage only: 36.0195% Prefill and 45.7097% Decode direct GPU-time
coverage.  It is not a performance result or selector input.
