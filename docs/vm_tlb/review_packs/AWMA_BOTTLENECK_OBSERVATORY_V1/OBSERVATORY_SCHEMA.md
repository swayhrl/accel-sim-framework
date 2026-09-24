# AWMA Bottleneck Observatory V1 schema

The observatory is a target-independent, opt-in, read-only telemetry module for
the frozen RTX4080/V1 simulator.  Its public controls are:

- `GPGPUSIM_AWMA_BOTTLENECK_OBSERVATORY=0|1|2|3`
- `GPGPUSIM_AWMA_BOTTLENECK_DOMAINS=progress,scheduler,execution,memory,translation,sync`

Level 0 is the default.  An absent domain mask means `all`.  Unknown levels or
domain names assert at configuration time rather than silently changing scope.

## Levels

- `0 OFF`: hooks return before state traversal or allocation; no observatory
  output is emitted.
- `1 TRIAGE`: aggregate counters, source-predicate scheduler classification,
  bounded instruction/CTA progress checkpoints, cache/LDST/queue aggregates.
- `2 WINDOWED`: Level 1 plus online fixed 32/128/512 simulator-cycle windows,
  bounded deterministic reservoir quantiles, and fixed Top-8 windows per metric.
- `3 DEEP`: Level 2 plus earliest READY-to-admission latency, exact cycle-indexed
  instruction/CTA progress, and first/last application-data DRAM completion.

The Level-2 reservoir holds at most 4096 completed windows per metric and width.
It is deterministic and bounded; `mean` and `peak` are exact, while p50/p95/p99
are reservoir estimates when the number of windows exceeds 4096.  The output
records the reservoir size.  Top-K windows are exact.

## Structured records

- `awma_observatory_metric`: domain, metric, kind, total, samples, mean,
  single-cycle peak.
- `awma_observatory_window`: domain, metric, width, window count, mean, p50,
  p95, p99, peak, reservoir count.
- `awma_observatory_top_window`: domain, metric, width, rank, start cycle, end
  cycle, value.
- `awma_observatory_progress`: object, total, p25/p50/p75/p90/p99 cycles, tail.
- `awma_observatory_ready_to_admission`: completed, missing, repeat READY
  observations, outstanding, mean/p50/p95/p99/max latency.
- `awma_observatory_dram_boundary`: data completion count, first cycle, last
  cycle.

Event metrics are summed inside a window.  Gauge metrics are averaged over their
source-supported samples inside a window.  All windows are aligned to simulator
cycle zero; trace-file position is never used as time.

## Interpretation contract

The analyzer reports locations and supported mediators.  It never emits an
automatic root-cause claim.  Scoreboard collision is not split into memory and
compute dependency because the source does not retain that producer provenance.
Likewise, `eligible_structural` is a scheduler-level structural location, not a
specific functional unit unless another source counter supplies that evidence.
