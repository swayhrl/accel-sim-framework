# C16-P — Llama S2 P2 local direct-semantic postprocess

Status: `REAL_NATIVE_SCHEMA_SANITY / PROVISIONAL / COVERAGE_LIMITED`.

P consumed only the hash-closed G event at producer commit
`64f9ea0f00c2a97eedb4cc21d3d38e2b294be736` on
`hrl/vm-c16-g-autodl-wave1-v0`.  Its committed publish manifest SHA-256 is
`90fba52218fb97fdeeeea7d0abb3196762ecd3ef85687f2fcc4ae1f2c049e5fb`.
The successful diagnostic identity is deployment
`c16_llama32_1b_frozen_compatible`, scenario `S2`, diagnostic run
`cd3e40be-a7d5-43e5-9030-d84dc158f406`, and raw report SHA-256
`c96dacbeff499a59cb81a8ccf2f7344ee6701453069275c6b3b19b4861025eb3`.

P verified every committed Git payload and every declared external payload,
including the raw report, producer SQLite, producer direct map, semantic
receipt, and Nsight receipt.  The direct runtime receipt proves module-hook
identity only, forbids kernel-name/duration/historical backfill, and marks the
capture `SEMANTIC_DIAGNOSTIC_ONLY`, never timing evidence.

Local Nsight Systems 2024.2.3 re-exported the frozen raw `.nsys-rep` to a
22,274,048-byte SQLite (SHA-256
`52205c414eaa6c322e0d8048c86f6da1e7f3097b37dae035e721e81c92106053`).
The remote/local qualification passed: consumed schemas match; both have
45,280 kernel rows, 45,280 CUDA-correlated rows, stream `{7}`, two Prefill and
two Decode NVTX ranges, and 6,240 direct-runtime NVTX ranges. SQLite byte
identity was intentionally not required.

Within the diagnostic report only, NVTX temporal containment yields 20,669
direct-unambiguous kernels and 24,611 conservative UNKNOWNs, with zero
equal-width direct-range conflicts. P independently reproduced the G map on
all 45,280 report-local stable keys (`run_id`, SQLite rowid, correlation,
stream, start, end), with zero field mismatches.

For the clean S2 census report
`5a602bf2aec7700c5f3efb742ccd86fdc59bb37f17cdb228dae01ab0d6042bf0`,
P retained all 113,200 launches. Cross-report matching excludes absolute
timestamps, duration, correlation, stream, and launch ordinal. It permits only
the frozen structural tuple: deployment, scenario/input, implementation,
dtype, phase, device/context, verbatim kernel text, grid, and block. No clean
row has exactly one eligible diagnostic candidate: 111,223 have multiple
candidates and 1,977 have none. All remain explicit `UNKNOWN`; no kernel name
was interpreted as operator/layer semantics. The clean map's direct mapped GPU
time is therefore `0.0` for Prefill, Decode, and unattributed rows, and each
coverage row is `COVERAGE_LIMITED`.

Large outputs are raw-outside-Git under
`artifacts/c16_p_native_postprocess/event_driven/llama_s2_direct_semantic_cd3e40be-a7d5-43e5-9030-d84dc158f406/`.
They include the 108,502,189-byte full clean `DIRECT_SEMANTIC_MAP.tsv`
(SHA-256 `6c82edcb48b29b2cc4c8979091fb4009ff5bcf98d9c07594f6dbbfac20d9b38b`),
its deterministic gzip, coverage TSV, raw index, and merge audit. Exact
artifact hashes are in the committed receipt below.

This is an instrumentation/schema result, not a cross-lane scientific claim or
a Lane-C selector input. P remains active and will continue event-driven local
processing for hash-closed P1/P2/P3 events.
