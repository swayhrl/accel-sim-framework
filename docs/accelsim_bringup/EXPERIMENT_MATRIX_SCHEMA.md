# Experiment Matrix Schema

A13 consumes the A12 lockfile and emits:

- `A13_experiment_matrix_*.csv`: planned runs.
- `A13_experiment_results_*.csv`: run outcomes and parsed key stats.

The matrix supports baseline and variant labels. Baseline can execute immediately. Non-baseline variants require an explicit paper-specific config; otherwise they are marked `SKIPPED_NO_VARIANT_CONFIG`.

Resume is controlled by per-run `metadata.json` in `.local_runs/`. Failed rows are preserved unless `ACCELSIM_A13_RERUN_FAILED=1`.

A13 is infrastructure only. It does not implement paper mechanisms.
