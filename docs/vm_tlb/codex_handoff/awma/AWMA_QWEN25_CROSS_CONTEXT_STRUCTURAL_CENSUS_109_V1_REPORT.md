# AWMA Qwen2.5 cross-context structural census V1

Stage: `AWMA_QWEN25_CROSS_CONTEXT_STRUCTURAL_CENSUS_V1`  
Node: 109 / RTX 4080  
Status: COMPLETE — lightweight native NSYS/CUPTI census only; STOP.

## Authorities and boundary

- Lane A structural signature: `2e8680dc4cc25e2409c2ef37a15ae8c2fc29ae9f`.
- Lane D V3 representative suite: `ba1b4bdbca47e24a56909eec2764e738c509d2f1`.
- Classification is exactly CUPTI kernel correlation ID to one CPU CUDA-runtime launch, then the runtime-start timestamp in a same-thread C16 NVTX phase. GPU/NVTX wall-time overlap is not an attribution method.
- No NCU, NVBit, simulator-native capture, Accel-Sim, or mechanism run was performed.

## Inputs

`T256` is explicitly `DERIVED_CONTROL`: the first 256 IDs of the accepted S2 token stream, materialized deterministically (output SHA-256 `60a5e2239924fde29e6a872a55f953adb4052e5e5e152fe47a112d18ea773e15`). `T8192` uses the existing hash-closed S3_TEXT frozen input (SHA-256 `9e127ae9363358c3b2ed3b09608d9268fd3fc799070d58688aa540be019a3bb4`). B4 replicates the accepted S2 sequence four times and is a controlled shape experiment. D128 continues greedy decode deterministically from accepted S2 prefill and records all generated tokens in the raw driver receipt.

There is no second accepted, independently frozen T2048 TEXT payload in the consulted authority. The same-length different-content point is therefore `STOP_NO_SECOND_ACCEPTED_OR_EXPLICITLY_FROZEN_T2048_TEXT_PAYLOAD`; no substitute payload was used.

## Observations

| Scenario | Prefill launches/pass | Decode launches/step | Full GPU time | Decision |
|---|---:|---:|---:|---|
| T256 / B1 / D32 | 1,004 | 1,052 | 113,218,961 ns | RESTRATIFY_REQUIRED |
| T8192 / B1 / D32 | 980 | 1,052 | 317,794,729 ns | RESTRATIFY_REQUIRED |
| T2048 / B4 / D32 | 980 | 1,076 | 308,549,681 ns | RESTRATIFY_REQUIRED |
| T2048 / B1 / D128 | 980 | 1,052 | 497,208,082 ns | RESTRATIFY_REQUIRED |

The compact per-scenario strata and step tables contain every exact `phase/family/implementation/grid/block` record, its GPU-time weight, catalog join outcome, and recurrence. The D128 result retains the 32-step prefix but adds later-horizon exact strata; it is therefore not a reweight-only extension. T256 changes Prefill launch count; B4 changes the per-decode-step count. These are structural gate failures regardless of any time-weight change.

The five Decode GEMV shapes, 48/24 observations, splitkv/combine observations, and changing-grid paths are deliberately retained as exact separate rows in the recurrence tables. They are not merged by family name. Any mismatch or post-step-32 extension is represented as `RESTRATIFY_REQUIRED`, rather than assumed stable from S2.

`BALANCED` S2 coverage is not projected as portable workload coverage: its 89.9637% is an S2-only denominator. The scenario tables provide the exact safe S2-catalog join needed to recalculate coverage after a new scenario-specific target selection; existing S2 mass must not be reused as a claimed cross-context Native-time coverage value.

## Raw custody and review contents

All `.nsys-rep` and `.sqlite` raw files, extraction inventories, generated-token receipts, and checksums were copied to node164:

`/home/huangrulin/awma_raw/awma_qwen25_cross_context_census_20260924/`

Git contains only the compact scenario comparison, exact strata/recurrence derivatives, receipt, scripts, report, and hashes.
