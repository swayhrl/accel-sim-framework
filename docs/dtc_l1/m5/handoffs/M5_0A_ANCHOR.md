# M5.0A anchor handoff

## Status

**PASS — continue to M5.0B.**

## Input anchors

- Core parent `cdeec769fd0c1be12b45d58536ecb81074d4b415`; M5 Core `ddb9aac59cd1f6c80d7990b8bb9ec173d4819680`.
- Framework parent `56369da33dc5f48fc9ac071fd122fde4b35bd8c9`; M5 Framework `deca81b47623854d849520015b2ac20864080eb7`.
- Formal execution anchor: `m5/FORMAL_ANCHOR.md`.

## Completed experiment IDs

`M5.0A-ANCESTRY`, `M5.0A-BUILD`, `M5.0A-CTEST`, `M5.0A-VECADD-{LEGACY,BASE,IO,OO}`, and `M5.0A-REGISTRY`.

## Acceptance checklist

- CORRECTNESS_HARD: all DTC CTests PASS.
- CORRECTNESS_HARD: VecAdd output/accounting sentinels PASS in four modes.
- FIDELITY_HARD: LEGACY/IO/OO cycles exactly match M4 closeout.
- FIDELITY_HARD: runtime/toolchain/config/workload identities and raw logs are indexed.
- FIDELITY_HARD: registry check/register resume behavior is demonstrated.
- DIAGNOSTIC: safe initial batch concurrency is one simulator process.

## Results, issues, and invalidation

Artifacts: `FORMAL_ANCHOR.md`, `generated/result_registry.json`, four strict sentinel summaries, and `generated/m5_0a_raw_log_index.tsv`. No formal result is invalidated. The initial CMake configuration had DTC tests disabled by default; reconfiguring with `GPGPUSIM_BUILD_DTC_L1_TESTS=ON` resolved it before acceptance and generated no behavioral result.

## Mechanism finding and next scope

M5 runtime is neutral relative to M4 sentinels. M5.0B now resolves all ten workloads, first auditing `gemv/gemver`, `gesu/gesummv`, and `conv2d/2DConvolution`; inputs are selected only from canonical/standard source and Base-only full-load evidence.

## Do-not-redo

Reuse this build/runtime and registered sentinels unless a later behavior/timing Core change invalidates them.
