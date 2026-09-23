# AWMA representative suite refinement V3

Stage: `AWMA_AI_TRANSLATION_REPRESENTATIVE_SUITE_REFINEMENT_V3`
Status: **RECOMMENDED_CORE_SUITE_FOR_REVIEW**

The recommended core is **BALANCED: 25 actual simulator targets representing
139,333,064 / 154,876,910 ns (89.9637%) of the frozen full S2 Native GPU
duration**. It includes all five required Decode GEMV shapes, both Decode Flash
implementations, three major Prefill GEMM shapes, Prefill Flash, and three
measurement points for the one observed changing-grid Decode trajectory.

The selector uses frozen Native structure and duration plus accepted trace
availability. No translation response, simulator result, or mechanism outcome
is an input. These targets are a suite recommendation; this stage authorizes
no new trace capture or simulation.

## Read order

1. [Methodology](METHODOLOGY.md): cluster, holdout, identity, and frontier rules.
2. [Pareto frontier](PARETO_FRONTIER.tsv): denominators, coverage, structure,
   trace status, and measurement burden for all three options.
3. [Target manifest](SUITE_TARGETS.tsv): actual launch or accepted trace
   identity for each measurement point.
4. [Cluster catalog](CLUSTER_CATALOG.tsv) and
   [trajectory steps](DECODE_SHAPE_TRAJECTORY_STEPS.tsv): represented mass and
   all 32 source observed grids, durations, and recurrence counts.
5. [Identity reconciliation](IDENTITY_RECONCILIATION.tsv): five exact safe
   Lane A ↔ Lane C matches, including payload launch index and both hashes.
6. [Scientific holdout](SCIENTIFIC_HOLDOUT.tsv) and
   [step evidence](SCIENTIFIC_HOLDOUT_STEP_EVIDENCE.tsv): reserved identity.
7. [Validation](VALIDATION_SUMMARY.md), [source anchors](SOURCE_ANCHORS.md),
   and [open issues](OPEN_ISSUES.md).

## Three non dominated choices

| Suite | Targets | Represented full S2 | Full S2 | Prefill | Decode | Reuse / requal / missing |
|---|---:|---:|---:|---:|---:|---:|
| CORE_MINIMAL | 14 | 107,980,380 ns | 69.72% | 75.40% | 68.33% | 3 / 2 / 9 |
| **BALANCED (recommended)** | **25** | **139,333,064 ns** | **89.96%** | **75.40%** | **93.94%** | **3 / 2 / 20** |
| BROAD | 38 | 151,314,122 ns | 97.70% | 90.91% | 99.64% | 3 / 2 / 33 |

The training objective sorts optional clusters by non holdout Native duration.
Each optional cluster costs exactly one simulator target and one missing trace
in this authority. Consequently each prefix maximizes training represented
mass at its incremental target and missing trace count. The tiers are chosen
at source time mass breakpoints (1% and 0.25% of the non holdout pool), rather
than preset suite sizes. Full S2 coverage is reported separately after
selection. The larger tiers add coverage and also add measurement and asset
work, so none dominates another on those axes.

The prior Phase 2 22 target figure is superseded: it mixed full stratum mass
with three trajectory launch durations. The Phase 3 target manifest contains
an additive `represented_mass_accounted_ns` field that charges the whole
trajectory exactly once.

## Boundaries

- `STATISTICAL_HOLDOUT`: 6,897 V2 launch records from the prior fixed
  identity split. Optional selection and representative launch choice exclude
  them. Its role is selector stability and weight validation.
- `SCIENTIFIC_HOLDOUT_REQUIREMENT`: a separately reserved source observed
  stable Decode shape path, excluded from all three candidate suites. Future
  scientific validation must also reserve a cross context or different model
  family target that shares no discovery target identity.
- `REUSABLE_NOW` and `REQUIRES_REQUALIFICATION` are excluded from missing
  capture demand. `MISSING_SIM_TRACE` is an asset classification, not capture
  authorization. Lane C Native only bundles are never treated as simulator
  traceg assets.

The full report is
`docs/vm_tlb/codex_handoff/awma/AI_TRANSLATION_REPRESENTATIVE_SUITE_REFINEMENT_V3_REPORT.md`.
