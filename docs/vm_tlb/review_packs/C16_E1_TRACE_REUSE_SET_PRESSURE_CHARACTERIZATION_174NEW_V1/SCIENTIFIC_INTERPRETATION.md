# Scientific Interpretation

Final label: `C16_E1_TRACE_REUSE_SET_PRESSURE_CHARACTERIZED_V1`

This interpretation is limited to `TRACE_ADDRESS_REFERENCE`,
`128B_LINE_REFERENCE_PROXY`, static accepted-Core mapping, and
`SET_CONFLICT_REFERENCE_PRESSURE_PROXY`. It makes no timing, actual L2
traffic, hit/miss, eviction, residency, or budget-performance claim.

## Evidence binding

The formal summary closed 4,515 kernels, IDs 2926–7440, against the qualified
trace index: 16,313,481,995 dynamic instructions and 3,653,040 CTAs. The
aggregator recorded `raw_trace_opened=false`. The runtime mapper was built
source-direct from Core `a2322069b9701597db7019080b5b54d29518e3a2` and config
SHA-256 `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`.

Durable result root:

`/root/share/mnt164/huangrulin/c16_ai_workload/analysis/C16_E1_TRACE_REUSE_SET_PRESSURE_CHARACTERIZATION_174NEW_V1`

Key durable SHA-256 values are:

- `QWEIGHT_L2_SET_MAPPING.json`:
  `732996f535876c90167352ba3eaaa9bebe53c694ebea139e815bc14322a2214a`
- `QUOTA_STATIC_MAPPING.json`:
  `1081c8c26cd568e9f25f461a861a7d86e772524fdc5c0a592d7be523c3f4b48f`
- `SET_CONFLICT_PRESSURE_ANALYSIS.json`:
  `228c6500350a82943e9f25ea8d8096a56634134b1d6af5761c3080e2519e1d84`
- `D1_D2_D2_D3_STABILITY.json`:
  `1b583affc08183413f9a8eaed1781acc7ce382af0607a20282b388cdaf65abea`
- `AGGREGATION_PROVENANCE.json`:
  `eea3c6fcd08d83e120613c6e2322a510d7c885e02f8d899f58e2726b0584b283`

The review-pack entry points are `VALIDATION_SUMMARY.json` and
`RESULT_SHA256SUMS` for mirrored results,
`TRACE_REFERENCE_SUMMARY_MANIFEST.json` for the durable compact-summary tree,
and `QWEIGHT_L2_SET_MAPPING_MANIFEST.json` for the durable full static mapping.
There is no copied `TRACE_REFERENCE_SUMMARY.json` or full
`QWEIGHT_L2_SET_MAPPING.json` in the review pack.

## Core mechanism semantics that constrain interpretation

At the exact Core SHA, `oracle_config::configure` converts the selected global
budget to lines and distributes quotient plus remainder over the 16 L2
instances (`src/gpgpu-sim/oracle_elastic_residency.cc:250-289`). This is a
per-subpartition quota, not a per-set reservation.

Victim selection is local to the addressed set's 16 ways. Below quota, an
eligible target fill can become protected. At quota full:

- an invalid local victim produces
  `QUOTA_FULL_BASELINE_INVALID_PRIORITY`, so the fill is not protected;
- an existing protected victim in the same set can be replaced while retaining
  protection occupancy;
- if the set has normal victims but no local protected victim, protection is
  denied as `QUOTA_FULL_NO_LOCAL_PROTECTED_VICTIM`.

See `oracle_elastic_residency.cc:345-431` and
`src/gpgpu-sim/gpu-cache.cc:464-524,573-642`. Ordinary traffic prefers normal
victims but may fall back to a protected victim when no normal victim is
eligible. Only non-write global reads are oracle-target eligible
(`oracle_elastic_residency.cc:434-437`). Thus global byte capacity never, by
itself, proves realized protection or survival until reuse.

## Static footprint and set placement

Each layer's qweight is exactly 33,947,648 bytes = 265,216 lines = 32.375 MiB.
Every layer contributes exactly 16,576 lines to each subpartition. Every one of
the 32,768 `(subpartition,set)` coordinates is used: 29,696 coordinates contain
8 target lines and 3,072 contain 9. Per-layer mean is 8.09375 lines/set,
coefficient of variation is 0.0360130, and zero-set fraction is zero.

All 378 layer pairs have a 32,768-coordinate set intersection and Jaccard 1.
Across all 28 regions, aggregate population remains even: mean 226.625,
median 226.5, p90 229, p99/max 230, coefficient of variation 0.0082367, and no
zero sets.

Therefore static placement is broad and balanced, not concentrated into a
small hot subset, and no layer has a static placement advantage. Conversely,
all layers share the entire set support, so there are no disjoint set islands
that could isolate one layer from other-layer traffic.

## Capacity meaning of B8, B16, B24, and BFULL

| Budget | Global lines | Lines/subpartition | L2 fraction | One-qweight fraction | Even per-set reference | Static result |
|---|---:|---:|---:|---:|---:|---|
| B8 | 65,536 | 4,096 | 12.5% | 24.7104% | 2 | Capacity-short in all 16 subpartitions |
| B16 | 131,072 | 8,192 | 25% | 49.4208% | 4 | Capacity-short in all 16 subpartitions |
| B24 | 196,608 | 12,288 | 37.5% | 74.1313% | 6 | Capacity-short in all 16 subpartitions |
| BFULL | 265,216 | 16,576 | 50.5859% | 100% | 8.09375 | Exactly one layer statically fits in every subpartition |

All quotient/remainder divisions have remainder zero. The per-set values are
an even-distribution interpretation reference, not hardware set quotas. For
B8/B16/B24, all 32,768 target sets carry 8 or 9 target lines versus references
of 2/4/6; those budgets cannot protect a complete layer even before dynamic
placement is considered. They are capacity-limited first, so the compound
“global sufficient but local unfavorable” flag is correctly false.

BFULL is the only budget globally and per-subpartition sufficient for one
complete qweight. Its 8/9 target lines per set also fit within 16-way physical
associativity. This establishes static fit only. It does not establish that the
right protected victim exists in each set when the quota is full, that ordinary
traffic never falls back to protected victims, or that one layer survives
while the other 27 target regions are accessed.

## Dynamic set-pressure proxy

Every layer/transition has `hot_set_fraction=1` at the 16-unique-line threshold
and `target_plus_non_target_over_associativity_fraction=1`. Median unique
layer-relative non-target pressure is 1,119–1,125 distinct lines per target set;
p90 is 1,131–1,139, p99 is 1,133–1,141, and maximum is 1,134–1,141. These are
distinct lines accumulated over the complete reuse gap, not simultaneously
resident lines or actual cache transactions.

The BFULL output marks all layers
`global_quota_sufficient_but_set_local_unfavorable_proxy=true`. This is driven
by the all-set dynamic pressure criteria, not static mapping skew. It means the
exact Core's same-set replacement/admission condition remains potentially
binding even when one layer's global quota fits. It does not report an observed
denial or eviction.

### Multidimensional extremes

No single layer is “hardest” under every pressure statistic:

- Unique median minimum 1,119: layers 14, 15, 16, 17, 18, and 21, D1→D2.
- Unique median maximum 1,125: layer 3, D1→D2.
- Unique p90/p99/maximum maxima 1,139/1,141/1,141: layer 27, D2→D3.
- Unique p90/p99 minima 1,131/1,133: layers 13, 14, and 18, D1→D2.
- Unique maximum minimum 1,134: layers 13 and 14, D1→D2.
- Reference median minimum 131,768: layer 7, D1→D2.
- Reference median maximum 144,672: layers 19 and 20, D2→D3.
- Reference p90 maximum 221,924: layer 19, D1→D2.
- Reference p99 maximum 283,824: layer 0, D1→D2.
- Single-set reference maximum 9,955,848: layer 1, D2→D3.

The unique-pressure range is narrow, while reference-frequency tails select
different layers. A future timing result should therefore be compared with the
matching statistic and transition, not with one universal layer ranking.

## D1→D2 versus D2→D3 stability

Intervening dynamic instructions and global address references are nearly
identical between the two transitions: Pearson 0.999963 and 1.0, with median
symmetric relative differences `5.843e-5` and `8.945e-5`.

Unique pressure is also stable in magnitude: median symmetric relative
difference is 0.000890 for per-set medians and 0.000707 for total conflicting
unique lines; maximum observed relative differences are 0.003562 and 0.003347.
Layers 14 and 21 show the largest absolute median shift, only 4 lines/set
(1,119→1,123). However, cross-layer Pearson values are moderate rather than
near one—0.535 for median pressure and 0.241–0.361 for upper-tail statistics—
because the between-layer range is extremely narrow. The magnitude is stable;
the fine-grained layer ordering is not sufficiently stable to elevate into a
mechanism ranking.

## Capacity versus mapping versus admission

The results separate three explanations:

1. **Capacity:** B8/B16/B24 are unambiguously smaller than one qweight in every
   subpartition. Any complete-layer-retention interpretation is invalid for
   those budgets.
2. **Static mapping:** placement is even and uses all sets for every layer.
   There is no evidence that a small subset of sets or one anomalous layer
   causes the primary limitation.
3. **Admission and dynamic competition:** BFULL removes the one-layer static
   capacity shortfall, yet all sets see large reuse-gap pressure and exact Core
   admission at full quota requires a protected victim in the same set. This
   is the strongest remaining mechanism-level explanation for why global fit
   may fail to become durable protection. Only future mechanism counters can
   establish whether that limitation actually occurred.

## Future B16 interpretation branches

The current B16 run is not interpreted here. When its independently bound
timing and mechanism counters are available, use the frozen template:

- **Local timing positive + pressure low:** check realized protection, denial,
  saturation, and whole-decode coverage before attributing benefit to reuse.
- **Local timing positive + collateral high:** separate local gain from
  non-target cost and test whether same-set pressure/admission offsets it.
- **Target protection low + denial high:** treat timing as a test of admission
  realization, not a clean test of qweight reuse value; distinguish global
  capacity shortage from no-local-protected-victim denial.
- **Target protection high + timing no benefit:** investigate reuse distance,
  next-reuse footprint, critical-path coverage, and other bottlenecks rather
  than rejecting the mapper or proxy.

None of these branches authorizes a B8/B16/B24/BFULL performance ordering from
the offline characterization alone.
