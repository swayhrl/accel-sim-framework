# AWMA AI translation representative suite refinement V3 report

Status: **RECOMMENDED_CORE_SUITE_FOR_REVIEW**
Stage: `AWMA_AI_TRANSLATION_REPRESENTATIVE_SUITE_REFINEMENT_V3`

The recommended `BALANCED` suite has 25 actual simulator targets and
represents 139,333,064 ns (89.9637%) of the 154,876,910 ns full S2 Native
GPU duration. Prefill coverage is 75.4013%; Decode coverage is 93.9382%.
The same selected clusters represent 113,956,715 / 126,440,396 ns
(90.1268%) of the non holdout selection pool. These are distinct
denominators with matching numerators.

The core keeps five Decode GEMV implementation/shape strata and both
splitkv/combine Flash implementations. It includes a 32-step changing-grid
trajectory as one represented cluster with three measurement targets. This
trajectory represents 10,661,015 ns once. Each of its 32 source grids,
durations, and recurrence values is retained in the review pack.

Three anchor-constrained, non dominated choices are published:
`CORE_MINIMAL` (14 targets; 69.72% full S2; 9 missing traces),
`BALANCED` (25; 89.96%; 20 missing), and
`BROAD` (38; 97.70%; 33 missing). All three reuse T0/T1/T2 and require
requalification of the existing splitkv and combine traces. The 20 missing
BALANCED traces are asset gaps, not capture requests.

The accepted Lane A structural catalog and Lane C asset inventory yield five
closed simulator asset strata. The Phase 3 code independently checks each
candidate payload's kernel index against the V2 exact function, phase, step,
grid, and block. Native only bundles remain outside simulator asset coverage.

The 6,897 record statistical holdout is used only for selector stability and
weight validation. A separate identity-hash selected Decode stable shape path
is reserved for future scientific validation and excluded from all suites.
Future cross context and different model family samples must likewise remain
disjoint from discovery targets.

The methods, per-target identities, coverage definitions, Pareto evidence,
validation, and source hashes are in
`docs/vm_tlb/review_packs/AWMA_AI_TRANSLATION_REPRESENTATIVE_SUITE_REFINEMENT_V3/README.md`.
No Node109, capture, Accel-Sim, or mechanism execution occurred.
