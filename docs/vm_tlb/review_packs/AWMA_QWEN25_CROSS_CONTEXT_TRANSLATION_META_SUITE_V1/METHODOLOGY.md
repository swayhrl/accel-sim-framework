# Meta-suite methodology

## Three nested identity levels

Level 1 is (phase, source normalized family archetype). CUBLAS_GEMV is GEMV,
CUBLAS_GEMM is GEMM, Flash is FLASH, native elementwise variants are
ELEMENTWISE, and reduce/copy retain their own archetypes. These are kernel
implementation categories, not inferred Q/K/V or model-operator roles.

Level 2 is (phase, normalized family, implementation-family key, recurrence
signature). GEMV exact template specializations retain distinct hashes at
this level; splitkv and combine are distinct implementation families.
Flash template specializations that retain the same splitkv/combine kind may
share Level 2. Recurrence records present-step launch count; the accepted S2
catalog uses a zero-inclusive minimum for grids occurring at one Decode step,
while the cross-context tables use present-step min/max. The selector
normalizes both to ONE_STEP_SHAPE_N before comparison. A Level 2 match does
not imply the same grid or batch context.

Level 3 is (phase, full exact implementation SHA, grid, block). A Level 3
match is strict. A Level 2 implementation/recurrence match with different
Level 3 becomes PORTABLE_IMPLEMENTATION_SHAPE_VARIANT. Source-driven B4
family/implementation dispatch shifts are SCENARIO_SPECIFIC_DISPATCH.
The D128 continuation is HORIZON_EXTENSION_VARIANT only after the 96 new
grids are verified at steps 33–128 with unchanged exact implementation,
block, and 48 launches per step. ABSENT_IN_SCENARIO remains a valid class
even though no selected S2 cluster requires it in these four observations.

All coverage is a union of scenario rows, counted once per scenario.
Exact, implementation/recurrence, and archetype masses use each scenario's
own full Native GPU duration denominator, including auxiliary launches.
Implementation coverage includes Level 3 exact matches, and archetype
coverage includes all deeper matches. A cluster-map row's Level 2 and Level 1
matching masses are explicitly nonadditive because multiple S2 clusters can
map to the same broader scenario stratum.

## Core and extensions

The accepted 25 S2 BALANCED measurement targets constitute
CORE_CROSS_CONTEXT: each selected cluster is Level 2 or Level 3 portable in
at least two other scenarios, or is an accepted reusable anchor. This
preserves the accepted S2 suite once; it is not copied per scenario.

Scenario extension candidates partition nonauxiliary Level 3 gaps.
Identical exact function/grid/block shapes across scenarios form one
candidate group. A changing-grid Decode path is grouped only if recurrence
tables establish one grid per step, contiguous steps, constant per-step
launch count, and monotonic grid evolution. Its first, grid-medoid, and last
steps supply three planning targets, while the candidate's Native duration
is counted once. D128's new step 33–128 segment is a continuation group;
its first/medoid/last points supplement the S2 trajectory measurements.

A candidate enters SCENARIO_EXTENSIONS if it contributes at least 3% of a
scenario's total Native GPU time; or if the same exact shape contributes
at least 10 ms summed over two or more contexts; or if it is needed for a
source-observed short-context Prefill GEMM/Flash, short Decode Flash or
shape path, long Prefill GEMM/Flash, batch Decode GEMM/Flash, or D128 horizon
axis. A second batch Decode GEMM implementation with at least 2% B4 share
is retained. These are structural/time rules and do not use translation
results. The rule selects 20 extension groups and 28 actual targets.
EXTENSION_CANDIDATES.tsv keeps the unselected alternatives visible.

The proposed meta-suite includes 53 actual target identities: 25 accepted
S2 core and 28 extension points. Level 3 coverage credits a candidate's
entire source-observed shape trajectory only when the trajectory passes the
stated recurrence/monotonic checks and its three measurement points are
included. This is design coverage, not evidence that the three points have
the same translation response as every intermediate shape.

## Capture priority

CAPTURE_PRIORITY ranks 38 missing planning groups (18 S2 BALANCED missing
clusters plus 20 scenario extension groups), not individual trajectory
points. The deterministic score is:

  cross_context_reuse_value * Native_time_mass_across_scenarios
  * scenario_diversity / estimated_capture_sim_burden

Here cross_context_reuse_value =
1 + 0.5*(number of scenarios sharing Level 2 implementation - 1)
+ (number sharing the exact candidate shape - 1).
scenario_diversity is the number of scenarios with that exact candidate
shape. Estimated burden = 4 * actual target count *
(1 + log2(1 + sum of representative grid CTAs)/16).
The factor 4 is a transparent missing-asset planning weight, not a measured
capture or simulator time. The score uses no C1, mechanism, or translation
sensitivity result. Existing REUSABLE_NOW and REQUIRES_REQUALIFICATION
payloads are excluded from missing-capture ranking, and every row states
capture_authorized=NO.
