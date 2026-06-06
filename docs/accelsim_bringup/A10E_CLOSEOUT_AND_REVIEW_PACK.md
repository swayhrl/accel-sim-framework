# A10E closeout and review pack

## Goal

Produce final A10 documentation, gaps, and review pack.

## Required tracked script

Create:

    scripts/accelsim/a10e_collect_alignment_pack.sh

Also create coordinator:

    scripts/accelsim/a10_run_all.sh

The coordinator should run:

    a10a_discover_prior_workflows.sh
    a10b_extract_prior_inventory.py
    a10c_build_trace_mapping.py
    a10d_run_aligned_smoke.sh
    a10e_collect_alignment_pack.sh

It should stop only on hard script errors. For blocked phases, write status and continue to closeout.

## Final summary

Create local final summary:

    .local_reports/A10E_final_alignment_summary_TIMESTAMP.md

Include:

- baseline commit
- A10A status and inventory path
- A10B workload inventory path
- A10B stats field inventory path
- A10C mapping path
- A10D smoke stats path if any
- number of prior artifacts found
- number of real prior workload rows
- number of high evidence prior workload rows
- number of mapped trace-available rows
- number of aligned smoke runs
- Mascar gaps
- MeDiC gaps
- exact next recommended round

## Review pack

Create:

    review_packs/A10_REAL_WORKLOAD_ALIGNMENT_review_pack_TIMESTAMP.tar.gz

Include:

- docs/accelsim_bringup/A10*.md
- docs/accelsim_bringup/RUNBOOK.md
- docs/accelsim_bringup/KNOWN_ISSUES.md
- scripts/accelsim/a10*.sh
- scripts/accelsim/a10*.py
- scripts/accelsim/README.md
- .local_reports/A10A*.md
- .local_reports/A10A*.csv
- .local_reports/A10B*.md
- .local_reports/A10B*.csv
- .local_reports/A10C*.md
- .local_reports/A10C*.csv
- .local_reports/A10D*.md
- .local_reports/A10D*.csv
- .local_reports/A10E*.md
- selected small .local_logs/A10*.log

Do not include:

- traces
- hw_run directories
- build directories
- old repo copies
- gpu-app-collection
- nested review packs
- large logs
- binary files

## Required tracked doc

Create or update:

    docs/accelsim_bringup/A10_MASCAR_MEDIC_GAPS.md

It must list:

- what prior artifacts were found
- what was truly mapped
- what remains missing
- whether workload equivalence is exact or approximate
- what stats fields are currently comparable
- what stats fields need future work

Update:

    docs/accelsim_bringup/A10_REAL_WORKLOAD_ALIGNMENT.md
    docs/accelsim_bringup/RUNBOOK.md
    docs/accelsim_bringup/KNOWN_ISSUES.md
    scripts/accelsim/README.md

## Final status values

Use one of:

    PASS
    PARTIAL_PASS_NO_ALIGNED_RUNS
    PARTIAL_PASS_NO_PRIOR_ARTIFACTS
    BLOCKED_NO_PRIOR_ARTIFACTS
    FAILED

PASS requires:
- real prior artifacts found
- real prior workload inventory generated
- mapping generated
- at least one aligned smoke run attempted or a documented reason why none is runnable
- review pack generated
- final git status clean

## A10E pass criteria

- Final summary exists.
- Review pack exists.
- Final git status is clean.
- Final response can cite exact CSV and review pack paths.
