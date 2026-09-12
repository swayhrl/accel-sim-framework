# Llama S2 direct-semantic evidence

Status: `DIRECT_SEMANTIC_QUALIFICATION_PASS` for instrumentation and join
qualification only.  Classification is `SEMANTIC_DIAGNOSTIC_ONLY` and
`NOT_FOR_NATIVE_TIMING`: the pass has `scientific_eligible=false` and
`scientific_eligible_for_timing=false`.  It neither overwrites nor reinterprets
the closed standalone baseline or G1 census.

The pass used the fixed Llama S2 identity and runtime source
`b241fecfe5cd78bc2cdbb733e3a437d68b741c89`.  It loaded the bound model once,
performed one uninstrumented warmup and one cache-correct instrumented decode,
and retained no timing samples.  Direct PyTorch module hooks emitted NVTX ranges
for direct module paths/classes only.  No kernel-name heuristic, duration-based
guess, or historical Llama map was used.

The full 45,280-row `DIRECT_SEMANTIC_MAP.tsv` is published outside Git with its
deterministic gzip companion and SHA256 in
[DIRECT_SEMANTIC_ARTIFACT_INDEX.tsv](DIRECT_SEMANTIC_ARTIFACT_INDEX.tsv).  Every
row binds deployment/scenario/run identity, kernel SQLite row identity, CUDA
correlation, stream, start/end interval, layer, operator, evidence type/source,
and source receipt/profile/package hashes.  The stable join key is
`run_id + kernel_rowid + correlation_id + stream + start_ns + end_ns`; all
45,280 keys are unique.  The map preserves all unmatched kernels as `UNKNOWN`.

Direct module categories include `ATTENTION` (Q/K/V/O projection and core),
`FFN` (gate/up/down/core), `NORM`, and `EMBEDDING_OUTPUT`.  Its map fields
distinguish `DIRECT_RUNTIME_NVTX`, `DIRECT_MODULE_ID`, and `UNKNOWN`.  Of 45,280
kernel rows, 20,669 are directly and unambiguously mapped, 24,611 remain
conservatively unknown, and 0 have an equal-width direct-range conflict.

Coverage is reported in [SEMANTIC_COVERAGE.tsv](SEMANTIC_COVERAGE.tsv): direct
GPU-time coverage is 17.2832% for Prefill and 37.1406% for Decode; the 455
kernel rows outside phase ranges remain `UNKNOWN`.  These are evidence coverage
statistics, not performance measurements and not evidence that an
operator/layer feature is valuable or unimportant.

Local Nsight Systems 2022.4.2 rejected the remote 2024.1 report format, so the
already hash-closed raw report received a one-time remote SQLite export fallback
and then local SHA closure.  No remote launch TSV/catalog was generated.  The
exact raw/SQLite paths, sizes, and hashes are in the artifact index.

The first direct-semantic attempt
`7c9d0ba8-2376-46f9-9791-2c3b8c8fb260` failed because an NVTX hook returned a
value that PyTorch interpreted as a replacement module input.  It remains a
`NON_SCIENTIFIC_DIAGNOSTIC` ledger row (12.5169 seconds) with a retained raw
hash/index row.  The corrected hook explicitly returns `None`; the successful
run uses a new ID and source anchor.
