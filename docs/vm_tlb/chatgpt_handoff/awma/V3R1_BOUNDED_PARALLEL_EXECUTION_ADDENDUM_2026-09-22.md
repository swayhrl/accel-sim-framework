# AWMA 174 V3R1 Resource-Aware Parallel Execution Addendum

Date: 2026-09-22

Applies to:

`AWMA_174_EXACT_F0_SEGMENT_STATE_CLOSURE_V3R1`

Coordination branch:

`hrl/awma-mainline-reset-crossview-v2`

## Decision

Dependency-first, resource-aware speculative parallelism is authorized.

Do not serialize runs merely because their scientific admission is ordered.

Current T1 `0/80` must continue uninterrupted.

Before launching more work, inspect:

- physical/logical CPU topology;
- current load and per-simulator CPU utilization;
- available memory and swap pressure;
- measured RSS of an existing simulator;
- I/O wait and shared trace-read pressure;
- free storage and node164 health;
- existing simulator/process count.

Concurrency is resource-derived, not fixed at 1 or 2.

If resources safely support all remaining executable simulations, launch all of
them.

For the current state, once frozen T2 input/config assets already exist:

- T1 `0/80`;
- T2 `10/80`;
- T2 `0/80`;

have no input-data dependency on one another.

Therefore T2 `10/80` and T2 `0/80` may both start while T1 `0/80`
continues, if the resource audit passes.

## Scientific admission rule

Any downstream point started before its upstream scientific gates close is
labelled:

`SPECULATIVE_PRE_GATE`

Execution is allowed, but admission is delayed.

The T1 pair is admitted only after T1 `0/80` passes its own hard gate.

The T2 pair is admitted only after both T2 `10/80` and T2 `0/80` pass their
own hard gates.

If an upstream or target-local gate fails, already-computed speculative results
are quarantined and not admitted until ChatGPT review.

## Isolation requirements

Concurrent runs must use separate:

- output directories;
- effective-config copies;
- stdout/stderr logs;
- receipt files;
- temporary directories;
- mutable checkpoint/state files.

Shared producer traces and compatibility assets remain immutable/read-only.

Do not mutate shared config/map files.

When useful, pin CPU-bound simulator processes to disjoint physical cores or
CPU sets.

Host wall time and CPU affinity are engineering controls, not scientific
metrics.

## Hard gate remains unchanged

Every admitted run requires:

- natural terminal completion;
- full per-access coverage;
- translated == downstream admissions;
- untranslated = 0;
- unobserved = 0;
- vm_weight_segmentation_enabled = 0;
- Segment lookup attempts/launches/completions = 0;
- Segment hits/misses = 0;
- all Segment suppression counters = 0.

Any nonzero Segment functional activity invalidates that run.

## Continuous-refill schedule

```text
NOW:
  T1 0/80        continue
  T2 10/80       start if resources permit
  T2 0/80        also start if resources permit; SPECULATIVE_PRE_GATE

AS EACH RUN FINISHES:
  hard-gate it immediately
  checkpoint/hash it immediately
  preserve node164 copy
  refill any free slot with remaining ready work

WHILE LONG RUNS CONTINUE:
  generate already-available receipts/tables/checkpoints in parallel
  do not wait idly for all simulation processes to finish

AFTER ALL REQUIRED RUNS PASS:
  derive cross-target metrics
  final report / review pack
  node164 closure
  commit / push / remote verify
```

No additional science is authorized.
