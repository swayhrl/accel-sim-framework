# Target Baseline final 26/26 C7e — independent-review-ready supplement

**Status:** `TARGET_BASELINE_26RUN_REVIEW_READY` (self-gated; ChatGPT independent acceptance pending).

This is a documentation/analysis-only supplement. The original final pack remains immutable at `../TARGET_BASELINE_FINAL_26OF26_C7E_r1/`; no simulator jobs were rerun and no formal Lane-A binary/config/trace was changed.

| Identity | Value |
|---|---|
| Runtime Core | `ece1a3a77c5628763e0a4605bfd1c639ee6a1495` |
| Runtime Framework | `f08d2ce857972fad73c4e1ab7162ba94c6336507` |
| Analysis Framework (Lane-D V3) | `cb83606eb8640382b7c1932d8981b70608d9d130` |
| Formal configuration hash | `85562fce759876616806d32791ea3b7d1b13ee68cf20a84e48c63c96f67b8c0d` |
| Accepted rows | 26 / 26 |
| Excluded diagnostics | 2 / 2 quarantined 3mm paths |

Recommended review order:

1. `FINAL_ACCEPTANCE_MATRIX.md` and `ACCEPTED_FORMAL_RUNS.csv`.
2. `3MM_REPLACEMENT_AUDIT.md` and `EXCLUDED_DIAGNOSTIC_RUNS.csv`.
3. `SOURCE_AND_ANALYSIS_ANCHORS.md`, `FORMAL_PROVENANCE_AUDIT.csv`, and `VALIDATION_SUMMARY.md`.
4. `TELEMETRY_COMPLETENESS.md` and `analysis/lane_d_v3/`.
5. Final workload tables: `target_baseline_comparison.csv`, `target_resource_pressure.csv`, `target_blocking_matrix.csv`, `target_bank_pressure.csv`, `target_l1_pressure.csv`, `target_lower_path.csv`, `target_temporal_summary.csv`, and `target_kernel_summary.csv`.
6. `INTERIM_TO_FINAL_RECONCILIATION.md` and `TARGET_BASELINE_BOTTLENECK_ANALYSIS.md`.

Raw logs are deliberately not copied into Git. `RAW_LOG_INDEX.tsv` gives their immutable runtime paths and hashes.
