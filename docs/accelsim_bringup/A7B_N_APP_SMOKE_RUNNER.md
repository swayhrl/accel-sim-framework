# A7B controlled N-app smoke runner

## Goal

Upgrade from a single-app direct smoke to a controlled N-app smoke runner.

The goal is not to run a full benchmark suite. The goal is to prove that multiple trace apps can be run with bounded time and produce per-app stats.

## Required tracked script

Create:

    scripts/accelsim/a7b_n_app_smoke.sh

## Inputs

Support these environment variables:

    ACCELSIM_TRACE_ROOT
    ACCELSIM_A7B_RUN_NAME
    ACCELSIM_A7B_MAX_APPS
    ACCELSIM_A7B_TIMEOUT_SEC
    ACCELSIM_A7B_APP_FILTER
    ACCELSIM_A7B_DRY_RUN
    ACCELSIM_A7B_CONFIG_DIR

Defaults:

    ACCELSIM_A7B_RUN_NAME=A7B_n_app_smoke_TIMESTAMP
    ACCELSIM_A7B_MAX_APPS=3
    ACCELSIM_A7B_TIMEOUT_SEC=600
    ACCELSIM_A7B_DRY_RUN=0
    ACCELSIM_A7B_CONFIG_DIR=SM7_QV100

## Trace discovery

Trace root selection priority:

1. ACCELSIM_TRACE_ROOT if set.
2. Trace root recorded in newest A6 or A7A reports.
3. Discover by finding kernelslist.g under:
   - .local_traces
   - hw_run
   - current repo tree

Do not download large traces in A7B.

## Direct run mode

The preferred A7B mode is direct accel-sim.out execution for selected kernelslist.g files.

Use:

    $ACCELSIM_ROOT/bin/release/accel-sim.out
      -trace KERNELSLIST
      -config $GPGPUSIM_ROOT/configs/tested-cfgs/SM7_QV100/gpgpusim.config
      -config $ACCELSIM_ROOT/configs/tested-cfgs/SM7_QV100/trace.config

Use timeout:

    timeout "$ACCELSIM_A7B_TIMEOUT_SEC" COMMAND

If timeout is not available, record that and run only the smallest single app.

## App selection

Discover candidate kernelslist.g files.

Prefer apps whose path contains one of these names if available:

    backprop
    bfs
    gaussian
    hotspot
    lud
    nw
    srad
    streamcluster
    pathfinder

Select up to ACCELSIM_A7B_MAX_APPS.

Avoid selecting very large apps if names or paths imply scaled, large, full, or huge.

If fewer than ACCELSIM_A7B_MAX_APPS are available, run what is available and mark PARTIAL_PASS_FEWER_APPS.

## Output layout

For each app, create an isolated local run directory:

    .local_runs/A7B_RUN_NAME/app_index_appname/

Write per-app logs:

    .local_logs/A7B_RUN_NAME_app_index_appname.log

Write CSV:

    .local_reports/A7B_RUN_NAME_stats.csv

CSV columns should include at least:

    app_index
    app_name
    status
    exit_code
    timeout_sec
    kernelslist
    log_path
    gpgpu_simulation_time
    gpgpu_simulation_rate_inst_sec
    gpgpu_simulation_rate_cycle_sec
    gpgpu_n_tot_w_icount
    exit_detected

Parsing can be best effort. If a stat is missing, use NA.

Write markdown report:

    .local_reports/A7B_n_app_smoke_TIMESTAMP.md

## Dry run

If ACCELSIM_A7B_DRY_RUN=1, print selected apps and commands but do not run the simulator.

Dry run should pass even when no trace root is available, as long as it reports that real execution would be blocked by missing traces.

## Required tracked doc

Create or update:

    docs/accelsim_bringup/N_APP_SMOKE_RUNNER.md

It must explain:

- why A7B exists.
- direct accel-sim.out mode.
- environment variables.
- default app count and timeout.
- output files.
- limitations.

## A7B pass criteria

- script exists and is executable.
- dry run works.
- real run runs up to 3 apps when trace root exists.
- stats CSV exists.
- report exists.
- no full benchmark suite is launched.
