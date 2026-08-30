# CALIBRATION_ANALYSIS_INFRA_r1

Lane-D infrastructure pack, initially populated from the formal interim
22/26 scope (11 completed workload pairs). It is not a baseline decision and
does not contain any opportunity-mechanism result.

Analyzer source: Lane-D branch `hrl/ep-l2-cal-analysis-v0`, commit
`1b1f5f3e1faecaf8a5344eb7687d00a032a194e9`.

## Contents

- `TEMPORAL_CARDINALITY_AUDIT.csv`: verified 64-slice L2 and 32-channel DRAM
  topology and completed-5K-window cardinality.
- `TEMPORAL_DISTRIBUTIONS.csv`, `CHANNEL_IMBALANCE.csv`: distribution,
  burst, and imbalance summaries. `NOT_EMITTED` remains distinct from zero.
- `CALIBRATION_MATRIX.csv`, `CALIBRATION_DELTAS.csv`: incrementally ingestible
  absolute records and provenance-guarded deltas. The initial delta file is
  header-only because D512/L1 calibration cells are not yet accepted inputs.
- `ANALYSIS_MANIFEST.json`: input scope and cell declaration.
- `../calibration/DESCRIPTOR_METADATA_COST.md`,
  `../calibration/BASELINE_DECISION_TEMPLATE.md`, and
  `../calibration/TELEMETRY_SEMANTICS.md`: cost, decision, and semantic
  contracts (repository-relative paths from `docs/ep_l2/`).

## Reproduction

Run from the Framework Lane-D worktree:

```bash
python3 -m pytest -q tests/ep_l2_analysis/test_lane_d_analysis.py
python3 docs/ep_l2/analysis/lane_d_analysis.py \
  --cell D256_BASE:/workspace/worktrees/accel-sim-ep-l2-c7e/docs/ep_l2/target_baseline_results_final_850:256:BASE \
  --workload vectorAdd_4M --workload scan --workload spmv \
  --workload convolutionSeparable --workload cfd_097k --workload dwt2d \
  --workload sad --workload sgemm --workload btree \
  --workload FWT_7_21 --workload FWT_11_19 \
  --out docs/ep_l2/review_packs/CALIBRATION_ANALYSIS_INFRA_r1
sha256sum docs/ep_l2/review_packs/CALIBRATION_ANALYSIS_INFRA_r1/* > \
  docs/ep_l2/review_packs/CALIBRATION_ANALYSIS_INFRA_r1/SHA256SUMS
```

When a workboard calibration row becomes `DONE`, rerun with one additional
explicit cell declaration, for example
`D512_BASE:/absolute/result/root:512:BASE`. The analyzer rejects mismatched
Core/Framework SHAs, frequency, trace identity, duplicate records, missing
baselines, and undeclared config changes.
