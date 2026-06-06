# A12 workload and config lockdown

## Goal

Convert A10 row-level evidence into a unique workload/config/run-level lockfile that can drive future experiments.

A10 produced many evidence rows. A12 should deduplicate them into stable locked experiment candidates.

## Required tracked script

Create:

    scripts/accelsim/a12_workload_config_lockdown.py

## Inputs

Default newest inputs:

    .local_reports/A10B_prior_workload_inventory_*.csv
    .local_reports/A10C_trace_mapping_*.csv
    .local_reports/A11_stats_equivalence_matrix_*.csv

Allow overrides:

    ACCELSIM_A12_WORKLOAD_INVENTORY
    ACCELSIM_A12_TRACE_MAPPING
    ACCELSIM_A12_EQUIVALENCE_MATRIX

## Deduplication rules

Deduplicate by:

    paper
    normalized_workload
    suite_hint
    config_hint
    args_hint
    accel_trace_id or kernelslist_path

If multiple evidence rows point to the same unique workload/config/run:

- preserve the strongest evidence row
- aggregate all source paths into a semicolon-separated evidence_sources field
- count evidence rows
- keep high-evidence sources first

Evidence priority:

    high > medium > low

Trace mapping priority:

    exact > alias > suite_alias > approximate > none

## Lockfile CSV

Create:

    .local_reports/A12_workload_config_lock_TIMESTAMP.csv

Columns:

    lock_id
    paper
    workload
    normalized_workload
    suite
    prior_config_hint
    prior_args_hint
    prior_run_mode_hint
    evidence_strength
    evidence_count
    evidence_sources
    accel_trace_id
    accel_app_name
    kernelslist_path
    trace_root
    accel_config_name
    gpgpusim_config_path
    accelsim_trace_config_path
    mapping_status
    match_type
    runnable
    stats_readiness
    config_equivalence
    include_smoke
    include_pilot
    include_paper_candidate
    priority
    notes

## Field definitions

stats_readiness values:

    exact_fields_available
    partial_fields_available
    smoke_only
    missing_stats
    unknown

config_equivalence values:

    same_named_config
    approximate_qv100_sass
    prior_config_unknown
    not_equivalent
    unknown

include_smoke:

    yes for at most 2 to 3 very small high-confidence workloads.

include_pilot:

    yes for up to about 5 workloads.

include_paper_candidate:

    yes when workload has high evidence and trace availability.

priority:

    P0
    P1
    P2
    P3

P0 should include:

    Mascar / hotspot if available
    MeDiC / srad if available

If these are unavailable, choose the closest high-evidence available workloads and document why.

## Summary report

Create:

    .local_reports/A12_workload_config_lock_summary_TIMESTAMP.md

Include:

- input paths
- row-level workload count
- unique lockfile row count
- P0 rows
- P1 rows
- trace-missing rows
- config-unknown rows
- stats-readiness summary
- limitations

## Required tracked doc

Create:

    docs/accelsim_bringup/WORKLOAD_CONFIG_LOCKDOWN.md

It must explain:

- why a lockfile is needed
- lockfile schema
- deduplication rules
- config equivalence meanings
- how A13 should consume the lockfile
- what not to infer from the lockfile

Also update:

    docs/accelsim_bringup/A12_WORKLOAD_CONFIG_LOCKDOWN.md
    docs/accelsim_bringup/RUNBOOK.md
    docs/accelsim_bringup/KNOWN_ISSUES.md

## Pass criteria

A12 PASS requires:

- lockfile CSV exists
- summary report exists
- rows are unique workload/config/run-level, not raw evidence-row-level
- P0 smoke set is defined
- future A13 can consume the lockfile directly
