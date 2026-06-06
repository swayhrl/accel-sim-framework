# A9 Mascar and MeDiC workflow alignment

## Goal

Align the Accel-Sim bringup pipeline with the existing GPGPU-Sim paper reproduction workflow style used for Mascar and MeDiC.

This phase should not reproduce Mascar or MeDiC again inside Accel-Sim. It should create a mapping and a reusable alignment layer:

- benchmark naming
- trace availability
- run command style
- stats CSV style
- review pack style
- known gaps

## Required tracked script

Create:

    scripts/accelsim/a9_mascar_medic_alignment.sh

## Inputs

Support:

    ACCELSIM_TRACE_ROOT
    ACCELSIM_A9_RUN_NAME
    ACCELSIM_A9_PRIOR_REPO_ROOT
    ACCELSIM_A9_MAX_ALIGNED_RUNS
    ACCELSIM_A9_DRY_RUN

Defaults:

    ACCELSIM_A9_RUN_NAME=A9_mascar_medic_alignment_TIMESTAMP
    ACCELSIM_A9_MAX_ALIGNED_RUNS=3
    ACCELSIM_A9_DRY_RUN=0

## Prior workflow discovery

Do not assume exact previous repo path.

Search cautiously under /workspace/repos for likely prior artifacts:

- repo or directory names containing:
    gpgpu
    mascar
    medic
- docs or review packs containing:
    Mascar
    MeDiC
    MASCAR
    MEDIC
    medic
    mascar
    rodinia
    parboil
    polybench
    cutlass

Use bounded search. Avoid scanning huge build directories.

Suggested approach:

    find /workspace/repos -maxdepth 3 -type d | grep -Ei 'gpgpu|mascar|medic'
    find /workspace/repos -maxdepth 4 -type f | grep -Ei 'mascar|medic|review_pack|stats|benchmark|workload'

If a relevant prior repo root is given by ACCELSIM_A9_PRIOR_REPO_ROOT, use it first.

## Mapping CSV

Create:

    .local_reports/A9_mascar_medic_alignment_TIMESTAMP_mapping.csv

Columns:

    source
    paper
    prior_benchmark_name
    prior_app_or_workload
    accel_trace_candidate
    trace_available
    runner
    config
    status
    notes

Possible status values:

    TRACE_AVAILABLE
    TRACE_MISSING
    NAME_UNMAPPED
    RUNNABLE_SMOKE
    RAN_PASS
    RAN_FAIL
    BLOCKED_NO_PRIOR_ARTIFACTS

## Optional aligned smoke

If the mapping finds available traces that match prior Mascar or MeDiC benchmark names, run up to ACCELSIM_A9_MAX_ALIGNED_RUNS using A7B direct runner.

Do not run a large suite.

If no prior artifacts are found, do not fail the whole infrastructure round. Mark A9:

    PARTIAL_PASS_ALIGNMENT_TEMPLATE

or:

    BLOCKED_NO_PRIOR_ARTIFACTS

depending on whether a useful template mapping was produced.

## Review pack style

Create final review pack:

    review_packs/A6B_A9_ACCELSIM_PIPELINE_review_pack_TIMESTAMP.tar.gz

Include:

- tracked docs under docs/accelsim_bringup relevant to A6B-A9
- tracked scripts under scripts/accelsim
- .local_reports/A6B*.md
- .local_reports/A7A*.md
- .local_reports/A7B*.md
- .local_reports/A8*.md
- .local_reports/A9*.md
- .local_reports/A7B*_stats.csv
- .local_reports/A8*_stats.csv
- .local_reports/A9*_mapping.csv
- .local_reports/A9*_stats.csv if present
- small selected logs only

Do not include:

- traces
- hw_run directories
- build directories
- gpu-app-collection
- nested review packs
- huge logs

## Required tracked doc

Create or update:

    docs/accelsim_bringup/MASCAR_MEDIC_ALIGNMENT.md

It must explain:

- what was searched.
- what prior workflow artifacts were found or not found.
- how benchmark names map to Accel-Sim traces.
- which aligned smoke runs were attempted.
- what remains for future real reproduction.
- how this differs from A8 small baseline.

## A9 pass criteria

- A9 script exists and is executable.
- mapping CSV exists.
- alignment report exists.
- review pack exists.
- any runnable aligned smoke is bounded and logged.
- final git status is clean.
