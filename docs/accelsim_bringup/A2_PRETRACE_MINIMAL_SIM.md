# A2 pre-trace minimal simulation

## Purpose

Run the smallest possible trace-driven SASS simulation without requiring tracer generation first.

The preferred path is to use existing traces if present. If no traces exist, try the official pre-trace downloader with the smallest available option.

## Required tracked script

Create:

    scripts/accelsim/a2_pretrace_smoke.sh

Required behavior:

- cd to repo root.
- Source scripts/accelsim/accelsim_env.sh.
- Accept optional environment variables:
    ACCELSIM_TRACE_ROOT
    ACCELSIM_BENCH
    ACCELSIM_CONFIG
    ACCELSIM_RUN_NAME
- Defaults:
    ACCELSIM_BENCH=rodinia_2.0-ft
    ACCELSIM_CONFIG=QV100-SASS
    ACCELSIM_RUN_NAME=A2_pretrace_smoke_TIMESTAMP
- First discover traces locally:
    find . .local_traces hw_run -type f -name kernelslist.g
    find . .local_traces hw_run -type d -name traces
- If ACCELSIM_TRACE_ROOT is set, use it.
- If not set, infer a trace root from discovered kernelslist.g paths.
- The expected run_simulations trace root should be the root containing app argument trace dirs, not necessarily the exact traces directory. If inference is uncertain, try a small ordered list and record each attempt.
- If no trace exists:
  - Run:
        python3 ./get-accel-sim-traces.py --help
    and save help output.
  - If the script supports a clearly small subset or destination option, use it.
  - If the script is purely interactive or likely to download huge data, do not start a huge download blindly. Mark A2 as BLOCKED_NEED_TRACE and record exact help output.
- Run:
    ./util/job_launching/run_simulations.py -B "$ACCELSIM_BENCH" -C "$ACCELSIM_CONFIG" -T "$TRACE_ROOT" -N "$ACCELSIM_RUN_NAME"
- Then:
    ./util/job_launching/monitor_func_test.py -v -N "$ACCELSIM_RUN_NAME"
    ./util/job_launching/get_stats.py -N "$ACCELSIM_RUN_NAME"
- Save:
    .local_logs/A2_pretrace_smoke_TIMESTAMP.log
    .local_reports/A2_pretrace_smoke_TIMESTAMP.md
    .local_reports/A2_pretrace_smoke_TIMESTAMP_stats.csv
- Search for output directories associated with run name and record them.

## Important details

- run_simulations.py can run trace-driven SASS mode with -T trace_root.
- monitor_func_test.py and get_stats.py use -N run_name.
- Do not use huge benchmark sets in A2.
- If a workload takes too long, stop after a reasonable smoke-test timeout and record partial status.

## A2 pass criteria

- At least one simulation finishes and get_stats.py emits nonempty CSV.
- Or A2 is BLOCKED_NEED_TRACE with exact missing trace reason and no uncontrolled download was performed.
