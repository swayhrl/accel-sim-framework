# CALIBRATION_ANALYSIS_INFRA_r1

Lane-D infrastructure pack, initially populated from the formal interim
22/26 scope (11 completed workload pairs). It is not a baseline decision and
does not contain any opportunity-mechanism result.

Analyzer source: Lane-D branch `hrl/ep-l2-cal-analysis-v0`; this pack records
the final-review V3 analyzer contract and validation evidence.

## Contents

- `TEMPORAL_CARDINALITY_AUDIT.csv`: verified 64-slice L2 and 32-channel DRAM
  topology, completed-5K-window cardinality, and exact per-time-group stream
  alignment.
- `TEMPORAL_DISTRIBUTIONS.csv`, `CHANNEL_IMBALANCE.csv`: distribution,
  cycle-fraction, high-average-run, and traffic-conditioned imbalance
  summaries. `NOT_EMITTED` remains distinct from zero.
- `NATIVE_DRAM_BANDWIDTH.csv`: final complete 32-channel native snapshot
  parsed from retained raw logs, with `n_cmd`-weighted physical data-bus mean,
  p50/p95/max, and `n_cmd` sum. An incomplete snapshot fails closed; no native
  physical 5K-window metric was retained.
- `CALIBRATION_MATRIX.csv`, `CALIBRATION_DELTAS.csv`: incrementally ingestible
  absolute records and provenance-guarded deltas. The initial delta file is
  header-only because D512/L1 calibration cells are not yet accepted inputs.
- `ANALYSIS_MANIFEST.json`: input scope and cell declaration.
- `validation/`: compact test, diff, and status evidence.
- `../calibration/DESCRIPTOR_METADATA_COST.md`,
  `../calibration/BASELINE_DECISION_TEMPLATE.md`, and
  `../calibration/TELEMETRY_SEMANTICS.md`: cost, decision, and semantic
  contracts (repository-relative paths from `docs/ep_l2/`).

## Reproduction

Run from the Framework Lane-D worktree:

```bash
python3 -m pytest -q tests/ep_l2_analysis/test_lane_d_analysis.py
python3 docs/ep_l2/analysis/lane_d_analysis.py \
  --cell D256_BASE:/workspace/worktrees/accel-sim-ep-l2-c7e/docs/ep_l2/target_baseline_results_final_850:256:BASE:docs/ep_l2/calibration/contracts/D256_BASE.json \
  --workload vectorAdd_4M --workload scan --workload spmv \
  --workload convolutionSeparable --workload cfd_097k --workload dwt2d \
  --workload sad --workload sgemm --workload btree \
  --workload FWT_7_21 --workload FWT_11_19 \
  --out docs/ep_l2/review_packs/CALIBRATION_ANALYSIS_INFRA_r1
find docs/ep_l2/review_packs/CALIBRATION_ANALYSIS_INFRA_r1 -type f ! -name SHA256SUMS -print0 | \
  sort -z | xargs -0 sha256sum > docs/ep_l2/review_packs/CALIBRATION_ANALYSIS_INFRA_r1/SHA256SUMS
```

When a workboard calibration row becomes `DONE`, add a corresponding contract
for the new cell. The analyzer rejects duplicate/missing stream keys, missing
baselines, wrong lineage, changed SHA without PASS equivalence evidence, and
any effective-config difference outside the declared cell contract. It also
rejects an actual runtime configuration digest that differs from the contract
and any incomplete config-delta PASS gate.
