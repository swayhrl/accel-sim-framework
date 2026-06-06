# A10C Accel-Sim trace mapping

## Goal

Map real prior Mascar and MeDiC workload names from A10B to available Accel-Sim traces in the current repo.

This phase should answer:

- Which prior workloads have an available Accel-Sim trace now?
- Which are missing?
- Which have approximate aliases?
- Which can be used for bounded aligned smoke?

## Required tracked script

Create:

    scripts/accelsim/a10c_build_trace_mapping.py

## Inputs

Default inputs:

    newest .local_reports/A10B_prior_workload_inventory_*.csv
    newest .local_reports/A10B_prior_stats_field_inventory_*.csv

Allow overrides:

    ACCELSIM_A10B_WORKLOAD_INVENTORY
    ACCELSIM_A10B_STATS_INVENTORY
    ACCELSIM_TRACE_ROOT

## Accel-Sim trace inventory

Discover kernelslist.g files under:

    ACCELSIM_TRACE_ROOT if set
    .local_traces
    hw_run
    current repo tree

Do not inspect huge binary contents.

For each kernelslist.g path, infer:

    trace_id
    trace_root
    kernelslist_path
    app_name
    normalized_name
    suite_hint
    cuda_version_hint
    device_hint
    arg_hint

Strip carriage returns from all fields.

## Mapping CSV

Create:

    .local_reports/A10C_trace_mapping_TIMESTAMP.csv

Columns:

    mapping_id
    paper
    prior_workload_id
    prior_original_name
    prior_normalized_name
    prior_source_path
    evidence_strength
    accel_trace_id
    accel_app_name
    accel_normalized_name
    kernelslist_path
    trace_root
    match_type
    mapping_status
    runnable
    config
    notes

match_type values:

    exact
    alias
    suite_alias
    approximate
    none

mapping_status values:

    TRACE_AVAILABLE
    TRACE_MISSING
    AMBIGUOUS_MULTIPLE_TRACES
    LOW_EVIDENCE_PRIOR_WORKLOAD
    UNMAPPED

runnable values:

    yes
    no

Default config:

    QV100-SASS or direct SM7_QV100 config pair

## Alias rules

Implement explicit alias mapping for common names:

    backprop, bp -> backprop
    bfs -> bfs
    hotspot -> hotspot
    lud -> lud
    nw, needle, needleman -> nw
    srad -> srad
    pathfinder -> pathfinder
    streamcluster -> streamcluster
    gaussian -> gaussian
    lavaMD, lava_md -> lavamd
    kmeans -> kmeans
    mri-q, mriq -> mriq
    stencil -> stencil

Do not over-match vague names.

## Mapping summary

Create:

    .local_reports/A10C_mapping_summary_TIMESTAMP.md

Include:

- prior workload inventory used
- number of trace candidates
- number mapped exact
- number mapped alias
- number missing
- high evidence mapped workloads
- high evidence missing workloads
- recommended A10D aligned smoke set

## Required tracked doc

Create:

    docs/accelsim_bringup/A10_TRACE_MAPPING_SCHEMA.md

Explain mapping fields and status meanings.

## A10C pass criteria

- Trace mapping CSV exists.
- Mapping summary exists.
- Existing Accel-Sim traces are inventoried.
- No template-only mapping is presented as real mapping.
