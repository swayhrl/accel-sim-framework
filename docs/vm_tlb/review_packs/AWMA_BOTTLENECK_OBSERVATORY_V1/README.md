# AWMA Bottleneck Observatory V1

Status: `COMPLETE`

This pack validates a target-independent, opt-in, multi-domain bottleneck
observability infrastructure.  It is not a mechanism experiment and makes no
scientific-semantics change.

Frozen authorities:

- RTX4080/V1 baseline: `AWMA_RTX4080_SIM_BASELINE_V1`
- ideal-control V3: `5e59fbcf7e5217e91d40e5ff2e38dfd3f48a97f8`
- T1 attribution V1: `0349464aa3c43623553730b3c28b3f1f5bafd9a8`

Primary entry points are `OBSERVATORY_SCHEMA.md`, `COUNTER_SOURCE_MAP.tsv`, and
the final overhead/neutrality/retrospective reports.  Automatic diagnosis is
limited to observed location, supported mediator, not-supported, and unresolved
labels; cause requires an external controlled experiment or manual directional
attribution.

Final binary SHA-256:
`875e89e1a6d2a1dd350954f050b0cc5dd9d26fd847b372bab5308e79e5760b05`.

## Validation outcome

- 48/48 formal overhead runs pass cycles/instructions/CTA/UID/correctness and
  OFF/no-output gates.
- T1 10/80, 0/80, and ideal recover the accepted high-level location:
  `downstream temporal burst/backpressure`.
- The accepted splitkv-combine target validates
  `NOT_MEMORY_DOMINATED:SCHEDULER_DEPENDENCY_SCOREBOARD` without inventing a
  compute mechanism or root cause.
- Domain-mask directed validation emits only requested scheduler records.

## Reliable location domains

- progress: cycles, committed work, CTA completion, bounded Level-1 and exact
  Level-3 progress/tail;
- scheduler: exclusive source-predicate classification and active warp/CTA
  gauges;
- execution: completed ALU/SFU/Tensor/LDST/OTHER pipeline classes;
- memory: LDST stall enums, L1D/L2 status, successful admissions/bytes,
  partition/DRAM queue pressure, and selected data DRAM boundaries;
- translation: accepted VM counters plus READY/not-ready and Level-3
  READY-to-admission latency;
- sync: barrier and membar predicates.

These remain symptoms rather than causes when source provenance is absent:
scoreboard dependency cannot be split into memory-vs-compute producer latency;
eligible structural blockage cannot be assigned to one FU after mixed dual-issue
traversal; empty ibuffer does not identify the precise frontend cause; and
`COAL_STALL` retains its existing combined meaning.

Currently `NOT_AVAILABLE`: a non-double-counted whole-hierarchy outstanding
request counter and a backend-independent separate ICNT-injection FIFO occupancy
counter.  Exact limitations are enumerated in `COUNTER_SOURCE_MAP.tsv`.

## Host-cost recommendation

Measured wall overhead relative to same-binary OFF:

| target | Level1 | Level2 | Level3 |
|---|---:|---:|---:|
| T1 | +1.031% | +2.490% | +2.658% |
| T2 | +6.229% | +5.935% | +4.250% |
| splitkv-combine | +6.710% | +8.028% | +9.356% |

No arbitrary PASS threshold is applied.  T2 contains a host-time outlier and the
short combine target magnifies fixed/noise costs; all raw repetitions remain in
`OBSERVATORY_OVERHEAD_MATRIX.tsv`.

`RECOMMENDED_DAILY_LEVEL = 1 (TRIAGE)`

`DEEP_DIAGNOSTIC_LEVEL = 3 (DEEP)`

Use Level 2 when temporal correlation and Top-K windows are required without
Level-3 exact progress/READY state.

## Pack contents

- `OBSERVATORY_SCHEMA.md`
- `COUNTER_SOURCE_MAP.tsv`
- `LEVEL1_TRIAGE_SCHEMA.tsv`
- `WINDOW_SCHEMA.md`
- `T1_RETROSPECTIVE_VALIDATION.md`
- `NON_MEMORY_CANARY.md`
- `OBSERVATORY_OVERHEAD_MATRIX.tsv`
- `OVERHEAD_QUALIFICATION.md`
- `NEUTRALITY_GATES.tsv`
- `SOURCE_DIFF_SUMMARY.md`
- `BOTTLENECK_OBSERVATORY.patch`
- `RAW_DATA_INDEX.tsv`
- `SHA256SUMS`
