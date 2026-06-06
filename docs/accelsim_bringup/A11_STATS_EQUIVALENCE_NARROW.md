# A11 stats equivalence narrow plan

## Goal

Upgrade the current smoke-level stats parsing into comparison-grade stats parsing for a narrow workload set.

This phase must not expand benchmark scope. Use only:

    Mascar / hotspot
    MeDiC / srad

If one of these is unavailable in the current mapping or traces, choose the closest high-evidence trace-available replacement and document why.

## Required tracked script

Create:

    scripts/accelsim/a11_stats_equivalence_narrow.py

Optional helper:

    scripts/accelsim/accelsim_stats_parser.py

## Inputs

Default inputs should be the newest files from A10:

    .local_reports/A10B_prior_stats_field_inventory_*.csv
    .local_reports/A10C_trace_mapping_*.csv
    .local_reports/A10D_aligned_smoke_*.csv
    .local_reports/A10D_aligned_smoke_*.md

Also inspect A10D logs referenced by the A10D CSV.

Allow overrides:

    ACCELSIM_A11_STATS_INVENTORY
    ACCELSIM_A11_TRACE_MAPPING
    ACCELSIM_A11_ALIGNED_SMOKE_CSV
    ACCELSIM_A11_LOG_ROOT
    ACCELSIM_A11_WORKLOADS

Default workloads:

    Mascar:hotspot,MeDiC:srad

## Parser requirements

The parser must support at least four modes:

    first
    last
    aggregate_sum
    per_kernel

Definitions:

- first: first occurrence of a stat key in the log.
- last: last occurrence of a stat key in the log.
- aggregate_sum: numeric sum across all occurrences when this is meaningful.
- per_kernel: preserve one row per kernel or per stat block if kernel boundaries can be detected.

Do not silently mix these modes.

If kernel boundaries cannot be robustly detected, mark per_kernel as PARTIAL and record the reason.

## Stat extraction rules

Extract generic GPGPU-Sim and Accel-Sim stat lines of the form:

    key = value
    key: value
    key value

Use conservative parsing.

Suggested fields to extract when present:

    gpgpu_simulation_time
    gpgpu_simulation_rate
    gpgpu_n_tot_w_icount
    gpu_tot_sim_cycle
    gpu_tot_ipc
    gpu_total_sim_rate
    L2_total_cache_accesses
    L2_total_cache_misses
    l2_total_cache_accesses
    l2_total_cache_misses
    total_cache_accesses
    total_cache_misses

The script should also collect all unknown key-value stats into a wide or long CSV if practical.

## Normalized stats CSV

Create:

    .local_reports/A11_normalized_stats_TIMESTAMP.csv

Columns:

    row_id
    paper
    workload
    normalized_workload
    source
    run_id
    log_path
    stats_mode
    stat_key
    normalized_stat_key
    stat_value
    stat_unit
    occurrence_count
    selected_occurrence
    kernel_hint
    notes

## Equivalence matrix CSV

Create:

    .local_reports/A11_stats_equivalence_matrix_TIMESTAMP.csv

Columns:

    matrix_id
    paper
    workload
    prior_field
    prior_normalized_field
    accel_field
    accel_normalized_field
    equivalence_class
    conversion_needed
    conversion_rule
    stats_mode_required
    confidence
    evidence_source
    notes

equivalence_class values:

    exact
    derived
    approximate
    accel_missing
    prior_missing
    not_comparable
    unknown

confidence values:

    high
    medium
    low

## Recommended equivalence rules

Use conservative rules.

Examples:

- prior gpgpu_n_tot_w_icount to accel gpgpu_n_tot_w_icount:
    exact if same definition appears in logs.
- prior gpu_tot_sim_cycle to accel gpu_tot_sim_cycle:
    exact if both present in same GPGPU-Sim style output.
- IPC:
    exact only if same stat key and same aggregation mode.
    derived if computed as instructions / cycles.
- simulation wall time:
    not comparable for performance effects unless explicitly used as simulator runtime metric.
- L2 metrics:
    approximate unless same exact stat key is present and config/cache hierarchy is known equivalent.

## Markdown report

Create:

    .local_reports/A11_stats_equivalence_TIMESTAMP.md

Include:

- input paths
- selected workloads
- selected logs
- parser modes tested
- number of stats extracted
- number of exact fields
- number of derived fields
- number of approximate fields
- number of missing fields
- limitations
- next step for A12

## Required tracked doc

Create:

    docs/accelsim_bringup/STATS_EQUIVALENCE_SCHEMA.md

It must explain:

- parser modes
- normalized stats schema
- equivalence matrix schema
- how exact, derived, approximate, and not_comparable are defined
- why A11 is narrow and not a full evaluation

Also update:

    docs/accelsim_bringup/A11_STATS_EQUIVALENCE_NARROW.md
    docs/accelsim_bringup/RUNBOOK.md
    docs/accelsim_bringup/KNOWN_ISSUES.md

## Pass criteria

A11 PASS requires:

- script exists and runs
- normalized stats CSV exists
- equivalence matrix CSV exists
- report exists
- Mascar/hotspot and MeDiC/srad are handled, or replacements are documented
- no broad benchmark run is launched
