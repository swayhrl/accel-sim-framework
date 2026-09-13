# Lane D analysis revision: controlled capacity effects and pressure measures

Status: `LANE_D_ANALYSIS_REVISION_COMPLETE`.

This is an analysis-only refinement of `D_OBSERVER_EVIDENCE_READY`. It launches
no simulator, changes no Core/config/raw-run directory, and changes no accepted
FAST64 artifact or scientific raw counter. The only new D4 fields are derived
from existing compact evidence: `no_free_events_per_active_sm_cycle` and
`no_free_events_per_1k_active_sm_cycles`, for IO only.

## 1. What is source-proven

- The occupancy observer samples once per active SM cycle and is observer-only;
  `physical_full_sample_fraction` is physical-pool-full **time exposure**.
- IO `no_free_events_per_active_sm_cycle` is an exact rate over those same
  active-SM-cycle samples. Whole-line OO has no compact no-free counter and is
  explicitly not imputed.
- A pending, Tag-evicted logical line that is successfully reallocated while
  still pending enters the exact duplicate lower-request path. Post-response
  re-accesses are excluded. A lower request payload is source-proven 128 B in
  this path.
- The physical-ID/free-list identity is source-proven downstream-inert for
  lower address, L2 mapping, and request order.

## 2. What the controlled capacity sweep establishes

D4 deliberately changes physical capacity (24/32/48 KiB) under frozen
workload, trace, and unrelated configuration. It establishes that capacity
changes end-to-end behavior and resource exposure in a workload-dependent,
non-monotonic way: Btree is invariant, while BICG/GESUMMV are sensitive.

At 48 KiB, physical-full time exposure falls substantially. For BICG it is IO
`0.927254 -> 0.930394 -> 0.595079` and OO
`0.923532 -> 0.927231 -> 0.00896656`; for GESUMMV it is IO
`0.967385 -> 0.973196 -> 0.599628` and OO
`0.962273 -> 0.966046 -> 0.00796831`. IO no-free events per active SM cycle
also fall at 48 KiB: BICG `0.925948 -> 0.929407 -> 0.594385`, GESUMMV
`0.965778 -> 0.972275 -> 0.595874`.

This is distinct from program-work burden. IO no-free events per instruction do
not fall: BICG `3.781 -> 3.977 -> 4.617`; GESUMMV
`5.475 -> 7.059 -> 6.677`. Runtime changes, so a reduced fraction of active
SM time at a full pool can coexist with more accumulated retries per completed
instruction.

## 3. Observed internal mediator relationships

At 48 KiB BICG/GESUMMV also expose higher average allocated lines/inflight
work, higher L2 miss/reservation pressure, longer alloc-to-ready lifetimes, and
worse cycles at several local points. For example, BICG IO misses/lower and
mean allocation-to-ready lifetime are `1.43/2018 -> 1.61/2802 -> 2.82/9400`;
GESUMMV IO is `1.48/1123 -> 1.94/2276 -> 2.65/5431`.

Those are measured mediator correlations in a controlled capacity sweep. The
capacity effect itself is established by the sweep; directions among occupancy,
inflight work, L2 pressure, lifetime, pending Tag eviction, and performance are
not independently isolated.

## 4. What is explicitly not established

The data do not prove that L2 pressure causes the slowdown, that duplicate
lower requests are the primary limiter, or that OO reclaim lifetime causes
performance. They cannot rank L2 contention, queueing, miss lifetime, and
duplicate feedback as independent causal contributors. The exact boundary is
machine-readable in `generated/D6_INTEGRATED_ARROW_CLASSIFICATION.tsv`.

## 5. What the duplicate-request study establishes

No-MSHR duplicate lower traffic is a real source-proven efficiency cost and is
workload-dependent; accepted PAPER_IO evidence includes very large shares.
`duplicate_traffic_inflation = duplicate / (lower_created - duplicate)` is
**lower-request payload inflation** only—not DRAM, bandwidth, or total-link
traffic inflation.

OO duplicate share is lower for seven workloads, higher for three, and zero in
both modes for MRI-Q and NN. OO therefore does not universally eliminate
duplicates. Btree, Gaussian, and 2DConvolution remain essential counterexamples
to the simple claim that OO performance wins are explained solely by duplicate
removal.

## 6. Recommended paper wording

> In a controlled physical-pool sensitivity sweep, more physical capacity is
> not monotonically beneficial. At 48 KiB, BICG and GESUMMV spend markedly less
> active-SM time with the physical pool full, while exposing greater inflight
> concurrency, longer miss lifetime, heavier L2 pressure, and worse execution
> time. This supports evidence consistent with bottleneck migration after a
> front-end capacity constraint is relieved; it does not independently identify
> the dominant downstream mediator.

> No-MSHR duplicate lower requests are a workload-dependent lower-request
> payload cost. OO does not universally reduce them, and its performance gains
> cannot be attributed solely to duplicate reduction.

## 7. Remaining limitations and frozen-input record

No 40-KiB point is added: it would not isolate internal mediators. No OO
no-free proxy exists. The revision used existing compact evidence only and
recorded these pre-revision SHA-256 values. As an additional read-only check,
`generated/D7_ORDERED_PREEXISTING_STAT_AUDIT.tsv` binds the accepted source-log
hash and proves the ordered sequence of every selected pre-existing statistic
is exact for all 30 final D4/D5 compact rows; it contains no raw output.

| Input | SHA-256 |
|---|---|
| Prior D4 telemetry | `44784f6fc47d3c4de22b82b509bfeeb5d5c285ba8fc358248c09926acef69901` |
| Prior D5 OO telemetry | `4ed62ec6b3d298bb057836b0b6356994faaa34c0d7e5bf44637cc6072a7ba687` |
| Prior D5 IO/OO comparison | `3d45e87f4c14e2593917234850958b25a30b19f2605ffe202d1ee94ccd225578` |
| Prior D5 traffic-inflation table | `36830e7a61b24ad7de123bf565cbd1b2b22d73aa83d1c8b51cf3eb562ad715ae` |
| Prior D6 classification | `653bd878f75293a4c16194132d5356064baf94f3216ce2a827cf8977a4947824` |
| Prior Lane-D final report | `9b445a5634078a9727ab5e4fbea81eb42dbd3ffc4c1bce544693cb27c8232c9c` |
| Accepted Lane-C IO table | `9537f6a55994e674b659be425cfc0e81144b5d3846a8c7282e56b193fc2655bd` |
| Accepted FAST64 speedup table | `9c8909d5b870d8cc9638d20e4723579e41cc3f7b9e85bb5701107b7d4f3038c2` |
| Accepted FAST64 primary registry | `f2f2ef207aed571b4323abcf39466a5a4c795fd87f8de359f3907af9cacf4a2b` |
| Accepted FAST64 primary matrix | `54f39f07ea80efbd359ec59e4dbc3a8380c6257fa866a42d30ad060b7ff4cebf` |
