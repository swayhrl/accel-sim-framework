# AWMA Qwen2.5 cross-context translation meta-suite V1

Status: META_SUITE_DESIGN_FOR_REVIEW
Stage: AWMA_QWEN25_CROSS_CONTEXT_TRANSLATION_META_SUITE_V1

This review pack upgrades the accepted S2 BALANCED suite into one structural
meta-suite across five observed scenarios. It has 25 shared S2 core targets
and 28 new scenario extension targets in 20 source-supported extension groups,
for 53 actual planned measurement targets. Separate 25-target suites for all
five scenes would require 125 target identities. This is a structural design,
not a translation-sensitivity or performance claim.

## Read order

1. METHODOLOGY.md: identity levels, coverage denominators, extension selection,
   recurrence normalization, and capture-priority formula.
2. CROSS_CONTEXT_COVERAGE.tsv: S2 BALANCED-only and proposed meta-suite coverage
   for all five scenario-specific Native time denominators.
3. CROSS_CONTEXT_CLUSTER_MAP.tsv: five-way disposition of each of the 23
   accepted S2 BALANCED structural clusters.
4. META_SUITE_TARGETS.tsv and SCENARIO_EXTENSION_TARGETS.tsv: proposed target
   identities, source scenario, roles, and represented scene relationships.
5. SCENARIO_STRATA_CLASSIFICATION.tsv and SCENARIO_HIGH_MASS_GAPS.tsv:
   per-stratum evidence and remaining high-mass exact gaps.
6. CAPTURE_PRIORITY.tsv: planning ranking with all capture_authorized=NO.
7. SOURCE_ANCHORS.md, VALIDATION_SUMMARY.md, OPEN_ISSUES.md, and RUN_RECEIPT.json.

## Scenario coverage

The first percentage is the S2 BALANCED-only Level 3 exact shape coverage.
The second is the proposed meta-suite Level 3 exact shape coverage. Level 2
and Level 1 are nested structural relationships, reported separately in the
machine-readable table.

| Scenario | Evidence class | S2 BALANCED exact | Proposed meta exact |
|---|---|---:|---:|
| S2 B1/T2048/D32 | accepted S2 | 89.96% | 90.96% |
| T256 B1/T256/D32 | derived control | 79.21% | 89.87% |
| T8192 B1/T8192/D32 | accepted S3 TEXT | 39.04% | 90.86% |
| B4 B4/T2048/D32 | replicated control | 7.13% | 80.03% |
| D128 B1/T2048/D128 | accepted S2 TEXT continuation | 87.05% | 93.95% |

The S2 meta exact increase is a structural match supplied by a cross-context
extension; it is not a claim that an S2 simulator trace for that extension
already exists.

## Main structural findings

- T256 retains all five S2 Decode GEMV exact shapes and the GEMV recurrence
  skeleton. Its Decode Flash splitkv and combine paths remain Level 2
  implementation/recurrence relatives even where exact specialization or grid
  changes. A short-context Prefill GEMM, Prefill Flash, splitkv variant, and
  changing-grid path are explicit extensions.
- T8192 retains the five Decode GEMV exact shapes and Decode splitkv/combine
  exact shapes. Long Prefill Flash (37,437,222 ns) and three major Prefill
  GEMM shapes (36,834,608; 24,471,716; 18,263,298 ns) drive extensions;
  several Prefill GEMM shapes are also present in B4.
- B4 has no Decode GEMV launches. Its Decode GEMM family contributes
  68,254,217 ns and Decode Flash 29,655,318 ns. This is a source-observed
  dispatch shift; no one-to-one operator equivalence is inferred.
- D128 retains the first 32 Decode shape-trajectory grids and continues the
  same exact implementation, block, and 48-per-step recurrence through 96
  new grids at steps 33–128 (28,654,328 ns). Its remaining exact gaps are
  separately visible rather than silently assigned to that trajectory.

## Boundary

T256 is a derived token-prefix control, B4 a replicated-input shape control,
and T8192 uses the accepted S3 TEXT input. The accepted census did not include
a second independently frozen T2048 content point. No GPU run, trace capture,
Accel-Sim run, C1 result, or translation sensitivity was used for selection.
All MISSING_SIM_TRACE entries and CAPTURE_PRIORITY ranks are planning only;
nothing here authorizes Node109 capture.
