# Qwen2.5 S2 full kernel census reclassification V2

Stage: `AWMA_QWEN25_S2_KERNEL_CENSUS_RECLASSIFICATION_V2`
Status: COMPLETE — offline reclassification only; no new GPU capture.

## Authority and method

The frozen input is the accepted node164 authority
`qwen25_s2_kernel_census_20260917T101100Z`:

- SQLite: `17d9551472a4b8d090a6aa9437ff9a74d90f336ae1ab15189ed108da1041734d`
- V1 full inventory: `7825697aa23647daee6a38ac4436029c5746fe29a468d303520d3884f2b4abef`
- V1 historical branch/commit: `hrl/awma-qwen25-s2-census-109-v1 @ 678d7b491d4788369ca0c22717453b20846ab195`

V2 does not use GPU-kernel wall-time overlap with NVTX ranges for its decision.
For every kernel, it requires this source-supported chain:

`CUPTI_ACTIVITY_KIND_KERNEL.correlationId` → exactly one
`CUPTI_ACTIVITY_KIND_RUNTIME.correlationId` → the CPU runtime API start lies
inside a `C16_PHASE` NVTX range on the same `globalTid`.

Only that chain yields `PREFILL` or `DECODE_STEP_n`. A correlated CPU launch
whose start is outside every C16 phase range is explicitly classified
`AUXILIARY`; this is a context classification, not a claimed argmax/sampling
operator identity. Missing, ambiguous, or thread-mismatched correlation would
remain `UNKNOWN`. No Q/K/V, layer, or GEMM/GEMV operator role is inferred.

## Whole-run result

| V2 class | Launches | GPU duration (ns) | GPU-time share |
|---|---:|---:|---:|
| PREFILL | 980 | 32,229,639 | 20.809841% |
| DECODE (32 steps) | 33,664 | 122,454,407 | 79.065632% |
| AUXILIARY | 33 | 192,864 | 0.124527% |
| UNKNOWN | 0 | 0 | 0.000000% |
| **All launches** | **34,677** | **154,876,910** | **100.000000%** |

The inventory retains exact kernel function, normalized family, grid/block,
stream, phase, decode step, runtime API context, correlation ID, and V1 fields.
The complete family/function/shape/step aggregation remains on node164; compact
phase, top-200, and delta tables are in this review pack.

## V1 → V2 attribution delta

All 34,072 previously non-UNKNOWN V1 rows retain their phase and step. The 605
V1 UNKNOWN rows (21,763,663 ns; 14.052182% of full GPU time) are now resolved
by the CUPTI chain:

- 572 launches / 21,570,799 ns (13.927705%) → `PREFILL`.
- 33 launches / 192,864 ns (0.124527%) → `AUXILIARY`.
- 0 rows remain UNKNOWN in this particular authority; the V2 policy still
  preserves UNKNOWN whenever the stated chain is absent or ambiguous.

The V1 inventory is unmodified historical evidence. The complete delta and the
legal-UNKNOWN reclassification summary are included separately.

## Durable outputs and hash closure

Large V2 artifacts are intentionally retained only at:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/qwen25_s2_kernel_census_reclassification_v2_20260923/`

Notably:

- `ALL_KERNEL_LAUNCHES_V2.tsv` (34,677 rows), SHA-256
  `222d5dfeeb1e7aaae3423f13873053c37c27f5c6290d8a58bd3186a0803ca77a`.
- `V2_FULL_CLASSIFICATION_SUMMARY.tsv`, SHA-256
  `7afc9833f633561f7cbb4acb2cada018c8bf6ddc73c311a6597e438a717e99f9`.
- `RUN_RECEIPT_V2.json` and `SHA256SUMS` close all durable artifacts.

The Git review pack deliberately contains only compact derivatives, durable
artifact index, receipt, and checksums. No raw NSYS/SQLite or full inventory is
committed.

## Validation

- Input SQLite and V1 inventory hashes match accepted authority.
- V1 and V2 launch cardinality match exactly: 34,677.
- V2 class counts and durations each sum to the whole-run total.
- Every phase/step assignment is `CUPTI_CORRELATED_RUNTIME_START_IN_SAME_THREAD_NVTX`.
- 33 auxiliary rows are all explicitly `AUXILIARY_RUNTIME_START_OUTSIDE_ALL_C16_PHASE_RANGES`.
- No capture, simulator run, Lane B edit, or V1 edit was performed.

The implementation and independent-review details are in the accompanying
review pack.
