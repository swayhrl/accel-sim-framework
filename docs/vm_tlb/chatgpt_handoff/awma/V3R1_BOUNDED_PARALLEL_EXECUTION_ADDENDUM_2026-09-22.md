# AWMA 174 V3R1 Bounded Parallel Execution Addendum

Date: 2026-09-22

Applies to:

`AWMA_174_EXACT_F0_SEGMENT_STATE_CLOSURE_V3R1`

Coordination branch:

`hrl/awma-mainline-reset-crossview-v2`

## Decision

Bounded speculative parallelism is authorized.

Current T1 `0/80` must continue uninterrupted.

While T1 `0/80` is running, T2 `10/80` may start immediately in a separate process/run directory.

Maximum concurrent simulator processes for this stage:

`2`

Do not start T2 `0/80` until T2 `10/80` has passed its own terminal/coverage/Segment-dormancy gate.

## Scientific admission rule

T2 `10/80` started before T1 `0/80` closes is labelled:

`SPECULATIVE_PRE_T1_GATE`

Its execution is allowed, but it is not admitted into the scientific matrix until:

1. T1 `0/80` passes terminal/full-coverage/Segment-dormancy gates; and
2. T2 `10/80` itself passes the same gates.

If T1 `0/80` fails a scientific hard gate, any concurrently produced T2 result is quarantined and not admitted until ChatGPT review.

## Isolation requirements

Parallel runs must use separate:

- output directories;
- effective-config copies;
- stdout/stderr logs;
- receipt files;
- temporary directories where applicable.

Shared producer traces and compatibility assets remain immutable/read-only.

Do not mutate shared config/map files.

If practical, inspect host CPU topology and pin the two simulator processes to disjoint CPU sets. CPU pinning is an engineering optimization only and must not alter simulator configuration.

Host wall time is not a scientific metric.

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

## Recommended schedule

```text
NOW:
  T1 0/80        running
  T2 10/80       start in parallel

WHEN T1 0/80 PASS:
  admit T1 pair
  continue waiting for T2 10/80 if still running

WHEN T2 10/80 PASS:
  start T2 0/80

AFTER T2 0/80 PASS:
  derive cross-target metrics
  report / review pack / node164 closure / remote publication
```

No additional science is authorized.
