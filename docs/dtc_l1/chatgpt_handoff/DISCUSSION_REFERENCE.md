# DTC-L1 / ISCAS 2027 Discussion Reference

Last update: 2026-09-24

## 1. Research question for the current stage

DTC removes L1-side miss-concurrency constraints and exposes substantially more memory-level parallelism. Most workloads benefit, but BICG and GESUMMV improve dramatically when the DTC GPU-wide lower-outstanding cap is reduced.

The current question is:

> Is this simply a need to throttle DTC, or can a source-defined downstream resource be enlarged so the system can retain high DTC concurrency and recover performance?

This distinction matters to the paper.

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

## 3. Why a bounded downstream-headroom experiment is scientifically valuable

A strong positive headroom result would improve the paper story:

> DTC exposes useful concurrency that the fixed downstream hierarchy cannot always absorb; enlarging the implicated resource can convert that concurrency into performance without throttling DTC.

This is stronger than saying only:

> DTC must be throttled.

A null result is also informative:

> The pressure is downstream, but no single tested L2 queue/port resource explains it, so the paper should keep the broader downstream-oversubscription interpretation.

Both outcomes are acceptable.

## 4. Why not say “the bottleneck is L2” today

Current evidence supports:

- pressure moves beyond L1 for difficult workloads;
- DTC injection is a strong intervention axis;
- L2 capacity can matter;
- L2 MSHR count is not sufficient to explain BICG.

Current evidence does **not** isolate a unique physical root cause such as:

- miss queue,
- data/fill port,
- NoC,
- ROP service,
- DRAM service.

Therefore paper wording must stay at:

> downstream oversubscription / shared memory-hierarchy pressure

unless the new headroom experiment isolates one resource.

## 5. Source-supported candidate resources

Default modeled L2:

- 40 banks.
- 10 MiB aggregate data capacity.
- 192 MSHR entries/bank.
- 4-way MSHR merge limit.
- 32-entry miss queue/bank.
- 32-B/cache-cycle data/fill port/bank.
- 200-cycle ROP delay.

The most plausible remaining first-line candidates are:

1. **miss queue**, if queue occupancy and `MISS_QUEUE_FULL` track cap sensitivity;
2. **data/fill port service width**, if utilization is near saturation and tracks request lifetime/cycles.

The point of the telemetry gate is to avoid guessing.

## 6. Required telemetry logic

Use accepted BICG IO/OO rows only:

- default;
- capacity=2x;
- MSHR=4x;
- cap=2048;
- cap=512.

For each row compare:

- cycles;
- DTC outstanding average/peak;
- lower-request average/max lifetime;
- L2 MSHR average occupancy;
- L2 miss-queue average occupancy;
- L2 misses;
- source-defined resource-failure reasons;
- data/fill port utilization.

The strongest evidence is a coherent chain:

> targeted pressure high at default → pressure falls under cap reduction → lifetime falls → cycles improve.

Do not convert correlation into causality unless the subsequent resource intervention supports it.

## 7. Guard-retry boundary

The known merge-tag identity-guard retry is non-resource diagnostic telemetry.

It must not be included in:

- L2 resource-pressure totals;
- failure-reason rankings;
- queue/MSHR attribution;
- paper causal claims.

Preserve original validator failures and reconciliations.

## 8. Allowed next-step logic

### Queue path

If miss-queue pressure coherently tracks throttling, test 32 -> 128 entries/bank at default DTC cap.

### Port path

If queue is not the dominant pattern but data/fill port utilization coherently tracks throttling, test 32 -> 64 B/cache-cycle at default cap.

### Both

If both independently satisfy the predeclared trigger, run both one-dimensional tests. Only if both materially help but remain incomplete may a queue+port combined upper-bound be tested.

### Neither

Stop. Do not cascade into NoC/DRAM/ROP sweeps.

## 9. Rejected alternatives for this window

Do not spend the unattended window on:

- more L2 capacity points;
- more L2 MSHR points;
- cap 1024/4096;
- queue=64 midpoint;
- 128-B port;
- ROP/DRAM/NoC sweeps;
- “infinite L2”;
- new adaptive admission hardware;
- full FAST12 sensitivity;
- more logical-Tag experiments.

These would either repeat already answered questions or expand the paper scope without a source-directed reason.

## 10. Expected paper outcome

Preferred strong outcome:

> DTC removes L1-side concurrency constraints; BICG/GESUMMV oversubscribe a fixed downstream resource; increasing that resource at cap=8192 recovers meaningful performance, showing that DTC shifts the resource balance downstream.

Conservative valid outcome:

> DTC removes L1-side concurrency constraints; BICG/GESUMMV exhibit workload-specific downstream oversubscription, but no single tested L2 queue/port resource is sufficient to isolate the root cause.

Do not broaden either conclusion beyond the tested workload scope.
