# A13 experiment matrix runner

## Goal

Create a bounded experiment matrix runner that can execute locked workloads with baseline and future variant labels.

A13 is still infrastructure. It should not implement a paper mechanism.

## Required tracked script

Create:

    scripts/accelsim/a13_experiment_matrix_runner.py

Optional helpers:

    scripts/accelsim/accelsim_stats_parser.py
    scripts/accelsim/accelsim_csv_utils.py

## Inputs

Default newest input:

    .local_reports/A12_workload_config_lock_*.csv

Allow overrides:

    ACCELSIM_A13_LOCKFILE
    ACCELSIM_A13_RUN_NAME
    ACCELSIM_A13_VARIANTS
    ACCELSIM_A13_MAX_RUNS
    ACCELSIM_A13_TIMEOUT_SEC
    ACCELSIM_A13_DRY_RUN
    ACCELSIM_A13_RESUME
    ACCELSIM_A13_RERUN_FAILED
    ACCELSIM_A13_STATS_MODE
    ACCELSIM_A13_INCLUDE_SET

Defaults:

    ACCELSIM_A13_RUN_NAME=A13_matrix_TIMESTAMP
    ACCELSIM_A13_VARIANTS=baseline
    ACCELSIM_A13_MAX_RUNS=4
    ACCELSIM_A13_TIMEOUT_SEC=900
    ACCELSIM_A13_DRY_RUN=0
    ACCELSIM_A13_RESUME=1
    ACCELSIM_A13_RERUN_FAILED=0
    ACCELSIM_A13_STATS_MODE=last
    ACCELSIM_A13_INCLUDE_SET=smoke

include set values:

    smoke
    pilot
    paper_candidate

## Matrix generation

Read lockfile rows.

Select rows where:

- runnable == yes
- include_smoke == yes when include set is smoke
- include_pilot == yes when include set is pilot
- include_paper_candidate == yes when include set is paper_candidate

For each selected row and each variant, create one run.

In A13, only baseline variant needs to actually run. If non-baseline variants are requested but no variant config is provided, mark them as SKIPPED_NO_VARIANT_CONFIG.

## Experiment matrix CSV

Create:

    .local_reports/A13_experiment_matrix_TIMESTAMP.csv

Columns:

    run_id
    run_name
    variant
    paper
    workload
    normalized_workload
    lock_id
    kernelslist_path
    trace_root
    gpgpusim_config_path
    accelsim_trace_config_path
    timeout_sec
    stats_mode
    run_dir
    log_path
    planned_status
    notes

## Run command

Use direct accel-sim.out:

    $ACCELSIM_ROOT/bin/release/accel-sim.out
      -trace KERNELSLIST
      -config GPGPUSIM_CONFIG
      -config ACCELSIM_TRACE_CONFIG

Run in:

    .local_runs/A13_RUN_NAME/RUN_ID/

Log:

    .local_logs/A13_RUN_NAME_RUN_ID.log

Use timeout per run.

## Resume behavior

If ACCELSIM_A13_RESUME=1:

- If a run metadata file says PASS and log exists, skip it.
- If a run failed and ACCELSIM_A13_RERUN_FAILED=0, skip it and preserve failed status.
- If ACCELSIM_A13_RERUN_FAILED=1, rerun failed rows.

Write per-run metadata JSON:

    .local_runs/A13_RUN_NAME/RUN_ID/metadata.json

## Results CSV

Create:

    .local_reports/A13_experiment_results_TIMESTAMP.csv

Columns:

    run_id
    run_name
    variant
    paper
    workload
    status
    exit_code
    timed_out
    stats_mode
    log_path
    gpgpu_simulation_time
    gpgpu_simulation_rate_inst_sec
    gpgpu_simulation_rate_cycle_sec
    gpgpu_n_tot_w_icount
    gpu_tot_sim_cycle
    gpu_tot_ipc
    l2_total_cache_accesses
    l2_total_cache_misses
    exit_detected
    notes

Missing stats should be NA.

## Summary report

Create:

    .local_reports/A13_experiment_matrix_summary_TIMESTAMP.md

Include:

- lockfile path
- run name
- variants
- selected rows
- matrix CSV path
- results CSV path
- pass/fail/timeout counts
- skipped runs
- limitations

## Required tracked doc

Create:

    docs/accelsim_bringup/EXPERIMENT_MATRIX_SCHEMA.md

It must explain:

- lockfile consumption
- matrix schema
- result schema
- direct-run mode
- resume and rerun-failed rules
- baseline vs variant semantics
- why A13 does not implement paper mechanisms

Also update:

    docs/accelsim_bringup/A13_EXPERIMENT_MATRIX_RUNNER.md
    docs/accelsim_bringup/RUNBOOK.md
    docs/accelsim_bringup/KNOWN_ISSUES.md

## Pass criteria

A13 PASS requires:

- dry-run works
- real baseline smoke matrix runs within max_runs
- matrix CSV exists
- results CSV exists
- summary exists
- no full benchmark campaign is launched

## Implemented Local Workflow

Dry-run first:

```bash
ACCELSIM_A13_DRY_RUN=1 python3 scripts/accelsim/a13_experiment_matrix_runner.py
```

Then bounded baseline:

```bash
python3 scripts/accelsim/a13_experiment_matrix_runner.py
```
