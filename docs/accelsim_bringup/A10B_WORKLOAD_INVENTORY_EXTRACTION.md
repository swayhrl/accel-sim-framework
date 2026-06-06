# A10B prior workload and stats inventory extraction

## Goal

Parse real artifacts found by A10A and extract the actual prior GPGPU-Sim workload/config/stats information for Mascar and MeDiC.

This phase should create structured inventories. It should not run Accel-Sim yet.

## Required tracked script

Create:

    scripts/accelsim/a10b_extract_prior_inventory.py

Use python3 for robust parsing.

## Inputs

Default input:

    newest .local_reports/A10A_prior_artifact_inventory_*.csv

Allow override:

    ACCELSIM_A10A_INVENTORY

Also inspect extracted review pack text files under:

    .local_runs/a10_prior_reviewpacks/

## Workload extraction sources

Look for workload names in:

- shell scripts
- Python scripts
- markdown guidance docs
- benchmark list files
- CSV stats files
- config files
- run logs
- review pack manifests
- README or closeout reports

Do not infer benchmark names solely from generic docs if there is no actual run/config evidence.

## Benchmark name normalization

Create normalized workload names.

Examples:

    backprop-rodinia-2.0-ft -> backprop
    backprop_rodinia -> backprop
    bfs-rodinia -> bfs
    hotspot-rodinia -> hotspot
    lud-rodinia -> lud
    nw-rodinia -> nw
    streamcluster -> streamcluster
    pathfinder -> pathfinder
    gaussian -> gaussian
    srad -> srad

Normalization rules:

- lowercase
- strip CR and LF
- replace repeated separators with one underscore
- remove common suite suffixes only when safe:
    rodinia
    rodinia_2.0
    rodinia_3.1
    ft
    trace
    traces
- preserve enough original text in original_name column

## Prior workload inventory CSV

Create:

    .local_reports/A10B_prior_workload_inventory_TIMESTAMP.csv

Columns:

    workload_id
    paper
    source_path
    source_line
    source_type
    original_name
    normalized_name
    suite_hint
    config_hint
    run_mode_hint
    args_hint
    evidence_strength
    notes

paper values:

    Mascar
    MeDiC
    both
    unknown

evidence_strength:

    high
    medium
    low

High evidence examples:
- name appears in a run script command
- name appears in prior stats CSV
- name appears in a benchmark list used by a script

Low evidence examples:
- name appears only in prose or README examples

## Prior stats field inventory CSV

Create:

    .local_reports/A10B_prior_stats_field_inventory_TIMESTAMP.csv

Columns:

    field_id
    paper
    source_path
    field_name
    normalized_field_name
    field_type
    likely_meaning
    used_by_script
    notes

field_type examples:

    gpgpusim_stat
    derived_metric
    timing
    speedup
    cache
    memory
    scheduler
    unknown

## Markdown report

Create:

    .local_reports/A10B_prior_inventory_summary_TIMESTAMP.md

Include:

- input A10A inventory path
- number of workload rows
- number of high evidence workloads
- Mascar workload candidates
- MeDiC workload candidates
- stats fields found
- unknowns and gaps

## Required tracked doc

Create:

    docs/accelsim_bringup/A10_WORKLOAD_INVENTORY_SCHEMA.md

Explain the CSV schema and evidence-strength rules.

## A10B pass criteria

- Prior workload inventory CSV exists.
- Prior stats field inventory CSV exists.
- Rows cite real source files.
- The script does not fabricate workload names.
