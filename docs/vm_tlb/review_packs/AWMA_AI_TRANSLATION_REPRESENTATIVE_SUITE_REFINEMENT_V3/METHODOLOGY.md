# Phase 3 selection methodology

## Two different quantities

`REPRESENTED_WORKLOAD_MASS` is the full S2 sum of GPU durations for all V2
launches in a selected structural cluster. A selected cluster contributes its
mass **once**, regardless of how many points are measured.

`MEASUREMENT_BURDEN` counts actual simulator targets. It also reports the
sum of selected launches' Native durations and grid CTA counts as source
scale proxies. The planning index (reusable=1, requalification=2,
missing=4) is a transparent relative effort score, not predicted simulator
seconds. A changing shape trajectory requires three targets; its entire
32-step mass is counted once.

The four coverage denominators are:

1. represented full S2 mass / 154,876,910 ns;
2. represented **non holdout** mass / 126,440,396 ns;
3. represented Prefill mass / 32,229,639 ns;
4. represented Decode mass / 122,454,407 ns.

Full S2 includes the 192,864 ns auxiliary class. The numerator for the
selection pool metric removes the same statistical holdout launch IDs as its
denominator. Thus no full work mass is divided by a smaller pool denominator.

## Structural clusters

The accepted structural catalog has 100 phase/family/exact function/grid/block
strata. They partition all 34,677 V2 launches and 154,876,910 ns exactly.
The Phase 3 script groups strata only when it observes a systematic stepwise
grid evolution with the same family, exact implementation, block, and per step
path. Concurrent different grids in a step remain separate strata. The script
splits an evolving path on a grid direction reversal, recurrence switch, or a
sustained median Native duration shift of at least 25%. It never merges an
implementation switch.

Exactly one path qualifies in S2: Decode `AT_NATIVE_ELEMENTWISE`, block
`128,1,1`, with 32 increasing grids, 48 launches per step and
10,661,015 ns accumulated duration. Its selected points are steps 1, 16,
and 32. The step table preserves all 32 grids, recurrence, accumulated
duration, and median duration. The endpoint/shape medoid/endpoint rule uses no
translation or mechanism result.

After this grouping there are 69 disjoint structural clusters. Selecting the
trajectory covers its 32 member strata and records three actual measurement
targets. All other selected clusters have one target. The frontier reports
both represented implementation/shape strata and the smaller count of
distinct shapes actually measured.

## Required major variants and frontier

`CORE_MINIMAL` includes five independent Decode GEMV shapes:
`1216/16×4`, `18992/8×8`, `224/16×4`, `224/32×4`, and `32/32×4`.
Their respective full S2 masses are 24,759,017; 13,107,325; 11,757,630;
6,837,034; and 4,468,140 ns. Shared `CUBLAS_GEMV` family does not justify
merging them. It also includes both Decode Flash implementations:
`FLASH_FWD_SPLITKV` (9,924,399 ns) and
`FLASH_FWD_SPLITKV_COMBINE` (2,164,261 ns). Prefill Flash, the three
largest non holdout Prefill GEMM clusters, and the observed shape trajectory
complete the required core anchors.

All eligible optional clusters cost one missing trace and one target. They
are ordered by decreasing **non holdout** accumulated Native duration. At
each optional target count, this prefix maximizes represented training mass
under the accepted asset and anchor constraints. `BALANCED` includes
optional clusters with at least 1% of the non holdout time; `BROAD` extends
to at least 0.25%. These are mass breakpoints, giving 11 and 24 optional
targets in this evidence. The full S2 mass of each candidate is evaluated
only after selection. Very small strata, including the prior approximately
17, 41, and 60 microsecond items, remain outside the recommended core.

The BALANCED tier covers four additional material Decode families (copy,
reduce, unrolled elementwise, vectorized elementwise). BROAD adds 13 targets
and 11,981,058 ns over BALANCED, at 13 more missing trace assets. BALANCED
therefore serves as `RECOMMENDED_CORE_SUITE`; CORE_MINIMAL is the lower
burden fallback, and BROAD is the expansion plan.

## Exact safe asset identity

The accepted Lane A catalog defines a narrow canonical implementation kind.
Phase + normalized family + canonical function kind + exact grid + block form
the structural join key. When the kind is unrecognized, the exact source
function SHA is retained so two distinct functions cannot collide.

For each of the five catalog strata with simulator assets, the Phase 3 script
also resolves the Lane C candidate payload name's `kernel-N` to V2 global
launch `N` and checks phase, full exact V2 function, shape, and Decode step.
The canonical key agrees on both sides. T0/T1/T2 are `REUSABLE_NOW`;
splitkv and combine are `REQUIRES_REQUALIFICATION`. All remaining selected
targets have no accepted exact safe simulator trace match and are classified
`MISSING_SIM_TRACE`. The nine `NATIVE_ONLY` bundles do not satisfy the
simulator trace requirement.

## Holdout contract

The 20% launch record `STATISTICAL_HOLDOUT` only validates selector
stability and weights. Candidate ranking, tier thresholds, duration regime
decisions, and actual representative launches use its complement.

The separate `SCIENTIFIC_HOLDOUT_REQUIREMENT` is selected by a fixed hash
of structural identity among non anchor, stable, 32-step Decode paths,
before optional mass ranking. The reserved cluster
`STR_c906c2d98595` is absent from CORE_MINIMAL, BALANCED, and BROAD.
Its 32-step source evidence and exact reserved launch identity are published.
It must not be used for mechanism discovery. Cross context and a distinct
model family remain future scientific holdout requirements; no result for
those contexts is claimed here.
