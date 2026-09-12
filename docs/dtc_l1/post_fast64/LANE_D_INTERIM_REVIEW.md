# Lane D interim review: terminal observer evidence

Status: `INTERIM_CHECKPOINT_NOT_D6_D7_CLOSEOUT`.

This checkpoint has 26 naturally terminal launched rows, 3 live GESUMMV rows,
and one exact Btree OO D3B reuse.  The 29-row launched coverage is
`generated/LANE_D_INTERIM_LAUNCHED_COVERAGE.tsv`; its 26/3 split is intentional.
The reuse is not a launched row and is separately and explicitly recorded in
`generated/LANE_D_INTERIM_D3B_REUSE.tsv`.  Thus the terminal numeric tables use
16 D4 rows and 11 D5 IO-versus-OO comparisons (10 fresh rows plus Btree reuse),
without silently treating a reuse as a 30th launched run.

Every terminal row was accepted only after the fail-closed collector verified
natural exit 0, immutable attempt/runner/Core/runtime/config/trace identity,
exact equality of all pre-existing accepted FAST64 metrics, lower/dependency
conservation, terminal drain, and zero observer live records.  All rows retain
classification `POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT`.
`generated/LANE_D_INTERIM_TERMINAL_COLLECTION.tsv` is the 26-row compact
correctness-evidence record for those checks; it is not raw simulator output.

## A. Already source-proven

- The Lane-B source audit, recorded as a dependency in
  `LANE_D_OBSERVER_EXECUTION_HANDOFF.md`, rules out a direct physical-ID or
  free-list effect on lower address, L2 set/partition mapping, and request
  ordering.  Hypothesis 1 (physical-ID mapping) therefore cannot explain a
  downstream mapping change.
- `LANE_D_OBSERVER_COUNTER_SEMANTICS.md` proves the exposure measurements are
  active-SM-cycle time integrals.  The sampler is observer-only and is not
  consulted by admission, allocation, scheduling, victim selection, retire, or
  reclaim.
- The pending-Tag-eviction-to-duplicate lower-request transition is exact
  source semantics, not a proxy: the IO proof is retained by Lane C and the OO
  analogue is documented in `OO_DUPLICATE_COUNTER_SEMANTICS.md`.  A duplicate
  is a successful reallocation of a still-pending, Tag-evicted logical line
  that reaches new-miss request creation; it is not a post-response re-access.
- For this whole-line request path a newly created lower request has a 128-B
  logical-line payload.  The reported payload inflation is request payload
  only, not total interconnect/DRAM traffic or recoverable performance.
- OO deferred-eviction-to-final-reclaim and allocation-to-ready intervals are
  generation-keyed observer records with terminal drain.  Their definitions are
  source-proven; a relationship from these intervals to concurrency is not.

## B. Supported by terminal interim data

- Btree is a stable D4 control: at 24/32/48 KiB, cycles, lower requests,
  in-flight exposure, allocation-to-ready lifetime, and duplicate count are
  identical within each mode; pool-full fraction is zero.  Its occupancy
  *fraction* falls only because the configured denominator grows.  This does
  not support a universal simple capacity-starvation explanation (hypothesis 2).
- BICG exposes strong capacity-associated changes.  IO average allocated lines
  increase 186.94 -> 248.46 -> 355.06 and average inflight requests 59.85 ->
  79.77 -> 148.05 from 24 -> 32 -> 48 KiB; OO shows 186.37 -> 247.83 ->
  303.77 and 72.55 -> 98.73 -> 133.97.  This supports a measured association
  of pool size with observed occupancy/inflight (hypothesis 4), not a causal
  arrow.
- In BICG, allocation-to-ready lifetime and L2 misses per lower covary across
  the three points (IO: 2018 -> 2802 -> 9400 cycles and 1.43 -> 1.61 -> 2.82;
  OO: 2331 -> 3341 -> 5574 and 1.25 -> 1.44 -> 1.64).  This supports measured
  covariation relevant to hypothesis 5; it does not identify `L2 pressure ->
  lifetime`.
- GESUMMV has only the 24/32-KiB D4 pair so far.  At 32 KiB, both modes have
  higher allocated/inflight exposure, allocation-to-ready lifetime, L2 pressure
  per lower, duplicate count, and cycles than at 24 KiB.  This is a local,
  terminal descriptive pattern relevant to hypothesis 3, not a completed
  three-point result.
- Of the 11 terminal D5 comparisons, OO duplicate/lower is lower for six
  workloads (2DConvolution, ATAX, BICG, GEMM, Hotspot1, LUD), higher for three
  (Btree, DWT2D, Gaussian), and equal at zero for two (MRI-Q, NN).  The exact
  values, accepted IO speedups, and accepted OO speedups are in
  `generated/D5_INTERIM_IO_OO_DUPLICATE.tsv`.

## C. Tentative / waiting for the three GESUMMV rows

- D4 GESUMMV 48-KiB IO and OO remain live.  They are needed before assessing a
  full GESUMMV 24/32/48 capacity pattern, including the proposed local
  pressure-transfer/reclaim-lifetime contrast.
- D5 GESUMMV primary OO remains live.  It is needed before the D5 comparison
  covers all twelve FAST12 workloads; no GESUMMV OO duplicate value is inferred
  from an IO value or another proxy.
- No 40-KiB point is justified by this interim snapshot.  A fourth capacity
  point cannot itself identify a causal direction; the final decision waits for
  the completed three-point GESUMMV evidence.

## D. Not supported

- A universal simple capacity-starvation story is not supported: Btree is
  invariant and never full, while BICG does not improve monotonically with a
  larger pool (e.g., IO cycles rise to 77.9M at 48 KiB).
- A direct physical-ID/free-list downstream-mapping explanation is ruled out by
  source audit (hypothesis 1).
- Duplicate traffic causing performance is not supported.  Capacity changes
  also change occupancy, in-flight work, allocation lifetimes, L2 pressure and
  reservation failures, so this observational wave cannot isolate duplicates.
- OO does not universally reduce duplicates: Btree, DWT2D, and Gaussian are
  preserved counterexamples among the 11 completed comparisons.

## E. Still insufficient

- Hypothesis 3 as a causal `capacity pressure -> transfer` claim is
  insufficient: the telemetry reports exposure, but neither randomizes pool
  capacity nor separately intervenes on the alleged throttle.
- Hypothesis 6 (`lifetime -> pending Tag eviction`) is insufficient and not
  uniformly monotonic.  BICG OO deferred/reclaim lifetimes rise across points,
  whereas pending-Tag-evictions per lower do not form the same unambiguous
  trend.  Counts alone do not establish direction.
- Hypotheses 5 and 10 retain only descriptive covariation, not causal proof.
  In particular, OO reclaim lifetime versus exposed concurrency is measured but
  not identified as either cause or consequence.
- Performance speedups are accepted FAST64 Base/IO and Base/OO ratios.  They
  are retained for comparison, not attributed to a duplicate mechanism.

The interim D4 raw compact rows and derived normalizations are respectively
`generated/D4_INTERIM_TERMINAL_ROWS.tsv` and
`generated/D4_INTERIM_ANALYSIS.tsv`.  Ratios have explicit zero-denominator
forms and are descriptive rates, not probabilities.
