# DTC-L1 / ISCAS 2027 Discussion Reference

Last update: 2026-09-24

## 1. Research question for the current stage

DTC removes L1-side miss-concurrency constraints and exposes substantially more memory-level parallelism. Most workloads benefit, but BICG and GESUMMV improve dramatically when the DTC GPU-wide lower-outstanding cap is reduced.

The earlier question was whether a larger L2 miss queue could absorb that concurrency.

The first queue intervention now gives a sharper question:

> Is the difficult-workload slowdown caused by limited buffering, limited deeper memory service, or an interaction in which both must be relieved before DTC's exposed MLP becomes useful?

This distinction directly affects the paper story.

## 2. What current evidence already rules out

### Extra L2 MSHR entries are not the main BICG explanation

BICG receives little/no meaningful performance benefit from increasing L2 MSHR entries by 4x.

Therefore do not reopen MSHR sweeps.

### L2 data capacity is only a partial explanation

Increasing L2 capacity helps BICG, especially OO, but the improvement is smaller than the effect of reducing DTC injection.

Therefore do not claim that the slowdown is simply “L2 is too small.”

### Total lower work is not enough

Comparable 128-B variants can create nearly equal lower-request counts/payload while having very different cycle counts.

Therefore do not use total bytes/transactions as the root-cause explanation.

### Low DTC cap is not a universal optimum

cap=512 strongly helps BICG/GESUMMV but hurts Btree/2DConvolution.

Therefore the correct insight is a workload-dependent concurrency balance, not “512 is the right cap.”

## 3. New intervention evidence: queue capacity alone is insufficient

Accepted BICG/OO queue intervention:

- queue=32 default:
  - `MISS_QUEUE_FULL` = 43,594,150
  - cycles = 47,231,655
  - average lower lifetime = 5,612.70
- queue=128:
  - `MISS_QUEUE_FULL` = 0
  - cycles = 47,588,121 (+0.75%)
  - average lower lifetime = 5,692.26

This supports:

> **INTERVENTION_SUPPORTED:** eliminating L2 miss-queue-full events is not sufficient to recover BICG/OO performance.

It does **not** support:

> “the L2 miss queue is irrelevant.”

Why? A queue can absorb bursts but cannot raise the sustained service rate of the resources behind it. If the downstream service path is slower than the DTC injection rate, a larger queue can remove queue-full events while leaving end-to-end latency and total runtime unchanged.

Therefore `MISS_QUEUE_FULL` can be a **backpressure symptom** rather than the unique throughput-limiting resource.

## 4. Why a buffering × service 2×2 is the right next experiment

The clean conceptual design is:

| | Default memory service | Increased memory-service headroom |
|---|---|---|
| queue=32 | existing default | new M-only cell |
| queue=128 | current queue intervention | new Q+M cell |

This directly separates:

1. queue buffering effect;
2. memory-service effect;
3. queue × memory-service interaction.

For BICG IO and OO, the queue=32/default cell already exists and queue=128/default is already running/accepted. Only the two memory-headroom cells per mode are new.

This is a stronger experiment than trying unrelated memory parameters one by one.

## 5. What “memory-service headroom” means

The next knob must increase a **deeper service capability**, not merely add another buffer.

The source audit must inspect the path after the L2 miss queue, including as available:

- memory-partition queues;
- interconnect / memory-partition admission;
- DRAM scheduler;
- DRAM request/return queues;
- DRAM command/data service;
- HBM timing / bandwidth;
- memory-fetch latency and queueing latency.

Use only source-defined counters and semantics that are actually available in the current simulator/logs.

### Important distinction

A larger downstream queue is another buffering experiment.

The desired M dimension is a **service-rate or service-latency headroom intervention** whose source semantics are clean enough to interpret.

Examples of possible classes after source audit:

- a clean bandwidth/service-width knob;
- a clean source-defined memory-service-latency knob.

Do not assume a specific knob from its configuration name alone.

## 6. Selection criteria for the one allowed memory-service knob

The chosen knob must satisfy all of:

1. source semantics are explicitly audited;
2. it is config-only or otherwise isolated without changing DTC semantics;
3. it does not change SM count, memory-channel count, L2-bank count, address mapping, trace identity, or L2 capacity/MSHR/queue definition;
4. it changes one interpretable memory-service dimension;
5. existing telemetry provides at least some evidence that the dimension is relevant under default vs cap throttling;
6. its change is an **upper-bound headroom probe**, not claimed as a production design point.

If no candidate meets these requirements, stop before launching a memory experiment.

## 7. Existing-telemetry audit before new memory simulation

While the remaining queue=128 rows run, audit accepted BICG default / cap2048 / cap512 outputs and source for any available:

- memory-partition queue occupancy/full/stall counters;
- DRAM scheduler queue occupancy/full/stall counters;
- memory-fetch latency;
- DRAM queueing/service latency;
- memory-system bandwidth or command/data utilization;
- read/write command counts;
- interconnect-to-memory or partition stall indicators;
- bank-level activity/efficiency.

Do not invent unavailable metrics. Record `NOT_AVAILABLE` where appropriate.

The audit should answer:

> Which one memory-side service dimension has the cleanest source semantics and strongest evidence of being stressed when cap=8192?

## 8. Predeclared BICG 2×2 interpretation

For each BICG mode:

- Q0M0 = queue32 + default memory (existing)
- Q1M0 = queue128 + default memory (current)
- Q0M1 = queue32 + selected memory headroom (new)
- Q1M1 = queue128 + selected memory headroom (new)

Possible conclusions:

### Memory service alone is sufficient

If Q0M1 materially improves cycles/lifetime and Q1M1 adds little:

> deeper memory service, not queue capacity, is the dominant missing headroom.

### Interaction is important

If Q0M1 helps partially but Q1M1 adds substantial additional recovery:

> buffering and deeper service jointly limit how much DTC-exposed MLP becomes useful.

### Neither is sufficient

If memory headroom and Q+M do not materially recover performance:

> the tested memory-service dimension is insufficient; do not cascade automatically to another memory knob.

## 9. GESUMMV is independent validation, not another matrix

Only after the BICG 2×2 is complete should GESUMMV receive memory-headroom validation.

Use the same selected memory knob and no new parameter values.

The exact GESUMMV cells are controlled by `CODEX_NEXT_STAGE.md`:

- if memory service alone is supported, validate M-only;
- if queue × memory interaction is supported, validate both M-only and Q+M.

Do not build a full new memory-system matrix.

## 10. Paper-facing interpretation

Strong interaction outcome:

> DTC exposes additional MLP, but difficult workloads require both transient buffering and downstream service headroom before that parallelism translates into performance.

Strong memory-only outcome:

> L2 queue-full events are symptoms of a deeper service bottleneck; increasing downstream service capability recovers performance without throttling DTC.

Null outcome:

> DTC creates workload-specific downstream pressure, but neither queue capacity nor the selected memory-service headroom is sufficient to isolate a unique root cause.

All three outcomes are publishable if the evidence boundary is explicit.

## 11. Rejected alternatives for this window

Do not run:

- more L2 capacity points;
- more L2 MSHR points;
- cap=1024/4096;
- queue=64 midpoint;
- L2 port experiments merely because queue alone was insufficient;
- multiple DRAM/memory knobs;
- memory-channel-count changes;
- L2-bank-count changes;
- NoC / ROP / DRAM parameter sweeps;
- perfect/infinite memory;
- new adaptive admission hardware;
- full FAST12 sensitivity;
- more logical-Tag experiments.

The current stage allows **one source-justified memory-service headroom dimension only**.
