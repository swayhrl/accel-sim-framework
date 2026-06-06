# A10D bounded aligned smoke and normalized stats

## Goal

Run a bounded Accel-Sim smoke on workloads that are both:

1. present in real prior Mascar/MeDiC workload inventory, and
2. mapped to available Accel-Sim traces.

This is a small validation of the mapping, not a full reproduction.

## Required tracked script

Create:

    scripts/accelsim/a10d_run_aligned_smoke.sh

## Inputs

Support:

    ACCELSIM_A10C_MAPPING
    ACCELSIM_A10D_RUN_NAME
    ACCELSIM_A10D_MAX_RUNS
    ACCELSIM_A10D_TIMEOUT_SEC
    ACCELSIM_A10D_DRY_RUN
    ACCELSIM_A10D_REQUIRE_HIGH_EVIDENCE

Defaults:

    ACCELSIM_A10D_RUN_NAME=A10D_aligned_smoke_TIMESTAMP
    ACCELSIM_A10D_MAX_RUNS=3
    ACCELSIM_A10D_TIMEOUT_SEC=900
    ACCELSIM_A10D_DRY_RUN=0
    ACCELSIM_A10D_REQUIRE_HIGH_EVIDENCE=1

## Run selection

Select rows from A10C mapping where:

    runnable == yes
    mapping_status == TRACE_AVAILABLE
    match_type in exact, alias, suite_alias
    evidence_strength == high if ACCELSIM_A10D_REQUIRE_HIGH_EVIDENCE=1

Prefer a mix of Mascar and MeDiC if both exist.

Do not run more than ACCELSIM_A10D_MAX_RUNS.

If no rows qualify, mark:

    BLOCKED_NO_RUNNABLE_ALIGNED_WORKLOADS

but still write a report.

## Direct run command

Use direct accel-sim.out mode:

    $ACCELSIM_ROOT/bin/release/accel-sim.out
      -trace KERNELSLIST
      -config $GPGPUSIM_ROOT/configs/tested-cfgs/SM7_QV100/gpgpusim.config
      -config $ACCELSIM_ROOT/configs/tested-cfgs/SM7_QV100/trace.config

Run inside per-workload local dirs:

    .local_runs/A10D_RUN_NAME/index_workload/

Capture logs:

    .local_logs/A10D_RUN_NAME_index_workload.log

Use timeout per workload.

## Stats parsing

Create:

    .local_reports/A10D_aligned_smoke_TIMESTAMP.csv

Columns:

    run_id
    paper
    prior_workload_id
    prior_name
    normalized_name
    kernelslist_path
    status
    exit_code
    timed_out
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

Parsing is best effort. Missing fields should be NA, not failure.

## Report

Create:

    .local_reports/A10D_aligned_smoke_TIMESTAMP.md

Include:

- mapping CSV path
- selected rows
- commands
- pass/fail/timeout counts
- stats CSV path
- limitations
- note that this is bounded smoke, not paper reproduction

## Required tracked doc

Create:

    docs/accelsim_bringup/A10_ALIGNED_SMOKE.md

Explain:

- selection rules
- direct-run command
- stats schema
- how this relates to A8
- limitations

## Hygiene fixes allowed in A10D

If needed, make small tracked fixes to:

    scripts/accelsim/a7b_n_app_smoke.sh
    scripts/accelsim/a8_small_benchmark_baseline.sh

Allowed fixes:

- strip CR from kernelslist paths
- avoid writing a transient file named 0
- quote shell variables
- keep CSV stable

If such fixes are made, commit them before running A10D.

## A10D pass criteria

- Dry-run works.
- Real run is bounded.
- Stats CSV exists if runnable workloads exist.
- Report exists.
- No full benchmark campaign is launched.
