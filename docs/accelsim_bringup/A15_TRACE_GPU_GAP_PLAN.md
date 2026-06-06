# A15 trace acquisition and GPU gap plan

## Goal

Document and, if possible, partially close the remaining trace and GPU gap.

A15 should not block the A11-A14 infrastructure readiness if no GPU is visible.

## Required tracked script

Create:

    scripts/accelsim/a15_trace_gpu_gap_plan.sh

## Inputs

Default newest inputs:

    .local_reports/A12_workload_config_lock_*.csv
    .local_reports/A10C_trace_mapping_*.csv

Allow overrides:

    ACCELSIM_A15_LOCKFILE
    ACCELSIM_A15_TRACE_MAPPING
    ACCELSIM_A15_ALLOW_TRACE_GENERATION
    ACCELSIM_A15_GPU_DEVICE
    ACCELSIM_A15_RUN_NAME

Defaults:

    ACCELSIM_A15_ALLOW_TRACE_GENERATION=0
    ACCELSIM_A15_GPU_DEVICE=0
    ACCELSIM_A15_RUN_NAME=A15_trace_gpu_gap_TIMESTAMP

## GPU checks

Run and record:

    nvidia-smi
    ls -l /dev/nvidia*
    nvcc --version
    echo CUDA_HOME
    echo CUDA_PATH
    echo CUDA_INSTALL_PATH

If no GPU is visible, mark:

    BLOCKED_NO_GPU_FOR_TRACER

but still produce trace gap plan.

## Trace gap matrix

Create:

    .local_reports/A15_trace_gap_matrix_TIMESTAMP.csv

Columns:

    gap_id
    paper
    workload
    normalized_workload
    current_trace_status
    kernelslist_path
    needed_for_set
    can_use_pretrace
    needs_new_trace
    gpu_required
    suggested_source
    suggested_command
    notes

needed_for_set values:

    smoke
    pilot
    paper_candidate
    future

## Trace acquisition plan

Create:

    .local_reports/A15_trace_gap_plan_TIMESTAMP.md

Include:

- GPU availability
- tracer status
- missing traces from lockfile
- which missing traces matter
- pre-trace-only path
- GPU tracer path
- exact future commands for NVBit tracer if GPU becomes available
- risks and limitations

## Optional trace generation

Only if all are true:

- GPU is visible
- ACCELSIM_A15_ALLOW_TRACE_GENERATION=1
- gpu-app-collection exists or can be safely cloned under .local_runs
- user intent is clear from environment variable

Then A15 may attempt one tiny trace generation for a missing smoke/pilot workload.

If attempted:

- limit to one workload
- record commands
- do not run a large suite
- do not commit generated traces
- validate kernelslist.g exists
- optionally run one direct accel-sim smoke

If not attempted, this is not a failure.

## Hygiene checks

A15 should also check and report:

- no untracked file named 0 remains
- CSV files generated in A11-A15 have stable headers
- known CRLF path issue is fixed or not observed
- review pack does not include large artifacts

## Final review pack

Create final review pack:

    review_packs/A11_A15_PAPER_REPRO_PIPELINE_review_pack_TIMESTAMP.tar.gz

Include:

- docs/accelsim_bringup/A11*.md
- docs/accelsim_bringup/A12*.md
- docs/accelsim_bringup/A13*.md
- docs/accelsim_bringup/A14*.md
- docs/accelsim_bringup/A15*.md
- docs/accelsim_bringup/STATS_EQUIVALENCE_SCHEMA.md
- docs/accelsim_bringup/WORKLOAD_CONFIG_LOCKDOWN.md
- docs/accelsim_bringup/EXPERIMENT_MATRIX_SCHEMA.md
- docs/accelsim_bringup/PAPER_REPRODUCTION_READY.md
- docs/accelsim_bringup/TRACE_ACQUISITION_PLAN.md
- docs/accelsim_bringup/RUNBOOK.md
- docs/accelsim_bringup/KNOWN_ISSUES.md
- scripts/accelsim/a11*.py
- scripts/accelsim/a12*.py
- scripts/accelsim/a13*.py
- scripts/accelsim/a14*.sh
- scripts/accelsim/a15*.sh
- scripts/accelsim/a11_a15_run_all.sh
- scripts/accelsim/accelsim_stats_parser.py if present
- scripts/accelsim/accelsim_csv_utils.py if present
- scripts/accelsim/README.md
- .local_reports/A11*.md
- .local_reports/A11*.csv
- .local_reports/A12*.md
- .local_reports/A12*.csv
- .local_reports/A13*.md
- .local_reports/A13*.csv
- .local_reports/A14*.md
- .local_reports/A14*.csv
- .local_reports/A15*.md
- .local_reports/A15*.csv
- .local_reports/A11_A15_final_summary_*.md
- selected small .local_logs/A11*.log
- selected small .local_logs/A12*.log
- selected small .local_logs/A13*.log
- selected small .local_logs/A14*.log
- selected small .local_logs/A15*.log

Do not include:

- traces
- hw_run directories
- build directories
- downloaded apps
- prior repos
- nested review packs
- huge logs
- binary files

## Final summary

Create:

    .local_reports/A11_A15_final_summary_TIMESTAMP.md

Include:

- A11 status
- A12 status
- A13 status
- A14 status
- A15 status
- baseline commit
- stats equivalence matrix path
- lockfile path
- experiment matrix path
- experiment results path
- readiness checklist path
- trace gap matrix path
- review pack path
- final git status
- conclusion:
    paper reproduction infrastructure ready, partially ready, or blocked

## Required tracked doc

Create or update:

    docs/accelsim_bringup/TRACE_ACQUISITION_PLAN.md

Also update:

    docs/accelsim_bringup/A15_TRACE_GPU_GAP_PLAN.md
    docs/accelsim_bringup/RUNBOOK.md
    docs/accelsim_bringup/KNOWN_ISSUES.md

## Pass criteria

A15 PASS requires:

- GPU/tracer gap plan exists
- trace gap matrix exists
- final summary exists
- final review pack exists
- no transient file 0 remains
- final git status is clean

A15 can be PASS_WITH_NO_GPU if no GPU is visible but the gap plan is complete.
