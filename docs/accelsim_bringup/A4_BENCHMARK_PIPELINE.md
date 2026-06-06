# A4 benchmark pipeline scripts

## Purpose

Turn the ad hoc A2/A3 commands into reusable scripts for future paper reproduction work.

A4 should not attempt a large benchmark campaign. It should provide a reliable smoke suite with clear knobs.

## Required tracked files

Create or finalize:

    scripts/accelsim/README.md
    scripts/accelsim/accelsim_env.sh
    scripts/accelsim/a4_run_smoke_suite.sh

Optional helper if useful:

    scripts/accelsim/common.sh

## Required behavior of a4_run_smoke_suite.sh

Inputs via environment variables:

    ACCELSIM_BENCH_LIST
    ACCELSIM_CONFIG_LIST
    ACCELSIM_TRACE_ROOT
    ACCELSIM_RUN_NAME
    ACCELSIM_MAX_JOBS
    ACCELSIM_DRY_RUN

Defaults:

    ACCELSIM_BENCH_LIST=rodinia_2.0-ft
    ACCELSIM_CONFIG_LIST=QV100-SASS
    ACCELSIM_RUN_NAME=A4_smoke_suite_TIMESTAMP
    ACCELSIM_MAX_JOBS=1
    ACCELSIM_DRY_RUN=0

Behavior:

- cd to repo root.
- Source accelsim_env.sh.
- Validate simulator binary exists.
- Validate trace root if using SASS config.
- Print resolved benchmark/config/run settings.
- For each benchmark/config pair:
  - Run run_simulations.py with -B, -C, -N.
  - Add -T only when trace root is needed and available.
- Run monitor_func_test.py.
- Run get_stats.py.
- Save:
    .local_logs/A4_smoke_suite_TIMESTAMP.log
    .local_reports/A4_smoke_suite_TIMESTAMP.md
    .local_reports/A4_smoke_suite_TIMESTAMP_stats.csv
- Include dry-run mode that prints commands without running them.

## README content

scripts/accelsim/README.md should explain:

- Source env:
    source scripts/accelsim/accelsim_env.sh
- Run A0:
    bash scripts/accelsim/a0_env_check.sh
- Run A1:
    bash scripts/accelsim/a1_build_smoke.sh
- Run A2 with explicit trace root:
    ACCELSIM_TRACE_ROOT=/path/to/traces bash scripts/accelsim/a2_pretrace_smoke.sh
- Run A3 if GPU exists:
    bash scripts/accelsim/a3_trace_rodinia_smoke.sh
- Run A4 suite:
    ACCELSIM_TRACE_ROOT=/path/to/traces bash scripts/accelsim/a4_run_smoke_suite.sh
- Collect final:
    bash scripts/accelsim/a5_collect_results.sh

## A4 pass criteria

- Scripts are executable.
- Dry-run works without requiring traces.
- If a valid trace root exists from A2 or A3, smoke suite runs and stats CSV is produced.
- If no trace exists, A4 still passes dry-run and records that full smoke execution is blocked by missing trace.
