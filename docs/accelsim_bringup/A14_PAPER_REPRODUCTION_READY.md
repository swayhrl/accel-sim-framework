# A14 paper reproduction readiness closeout

## Goal

Demonstrate the minimal paper-reproduction loop using the locked workloads and experiment matrix runner.

This is a rehearsal, not a full paper reproduction.

The loop should be:

    lockfile -> experiment matrix -> baseline run -> normalized stats -> comparability matrix -> mini table -> readiness checklist -> review pack

## Required tracked script

Create:

    scripts/accelsim/a14_reproduction_readiness_closeout.sh

This may call python helpers if needed.

## Inputs

Default newest inputs:

    .local_reports/A12_workload_config_lock_*.csv
    .local_reports/A11_stats_equivalence_matrix_*.csv
    .local_reports/A13_experiment_results_*.csv

Allow overrides:

    ACCELSIM_A14_LOCKFILE
    ACCELSIM_A14_EQUIVALENCE_MATRIX
    ACCELSIM_A14_RESULTS_CSV
    ACCELSIM_A14_RUN_NAME
    ACCELSIM_A14_FORCE_RERUN

Defaults:

    ACCELSIM_A14_RUN_NAME=A14_reproduction_readiness_TIMESTAMP
    ACCELSIM_A14_FORCE_RERUN=0

## Behavior

1. cd to repo root.
2. Source scripts/accelsim/accelsim_env.sh.
3. Verify git status and record it.
4. Locate A12 lockfile.
5. Locate A11 equivalence matrix.
6. Locate A13 results. If missing and force rerun is allowed, run A13 with smoke set.
7. Select the readiness pair:
   - Mascar / hotspot
   - MeDiC / srad
   If unavailable, use P0 rows from the lockfile.
8. Produce mini result table.
9. Produce readiness checklist.
10. Produce final local report.
11. Create an A14 review pack or add to final A11-A15 review pack in A15.

## Mini result table

Create:

    .local_reports/A14_mini_result_table_TIMESTAMP.csv

Columns:

    paper
    workload
    variant
    status
    comparable_exact_fields
    comparable_derived_fields
    comparable_approx_fields
    missing_fields
    key_cycles
    key_instructions
    key_ipc
    key_l2_accesses
    key_l2_misses
    notes

## Readiness checklist

Create:

    .local_reports/A14_readiness_checklist_TIMESTAMP.csv

Columns:

    item
    status
    evidence_path
    notes

Checklist items:

    clean_build_pipeline
    workload_lockfile
    trace_mapping
    stats_parser_modes
    stats_equivalence_matrix
    experiment_matrix_runner
    baseline_smoke_results
    variant_slot_supported
    resume_supported
    review_pack_supported
    tracer_gap_documented
    paper_mechanism_not_yet_implemented

## Local report

Create:

    .local_reports/A14_reproduction_readiness_TIMESTAMP.md

Include:

- status
- selected workloads
- lockfile path
- A13 result path
- mini table path
- checklist path
- exact readiness conclusion
- remaining blockers before actual paper reproduction
- recommended next step for a specific paper implementation

## Required tracked doc

Create or update:

    docs/accelsim_bringup/PAPER_REPRODUCTION_READY.md

This doc should be a stable runbook/checklist, not a run-specific log.

It must state:

- what is now ready
- what is not ready
- how to start reproducing a new paper
- how to add a paper-specific variant
- how to add workloads
- how to run baseline and variant
- how to parse and compare stats
- how to package review results

Also update:

    docs/accelsim_bringup/A14_PAPER_REPRODUCTION_READY.md
    docs/accelsim_bringup/RUNBOOK.md
    docs/accelsim_bringup/KNOWN_ISSUES.md

## Pass criteria

A14 PASS requires:

- mini result table exists
- readiness checklist exists
- local report exists
- stable PAPER_REPRODUCTION_READY.md exists
- conclusion clearly states whether paper-reproduction infrastructure is ready
