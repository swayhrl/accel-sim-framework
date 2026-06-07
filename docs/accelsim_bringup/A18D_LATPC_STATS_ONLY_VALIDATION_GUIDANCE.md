# A18D LATPC stats-only validation guidance

## Goal

Validate that A18 stats-only instrumentation did not change simulator behavior and that LATPC stats are present or correctly marked unavailable.

## Required script

Create:

scripts/accelsim/a18_latpc_validate_stats_only.py

## Inputs

Latest A18C outputs:

.local_reports/A18C_latpc_stats_probe_results_*.csv
.local_reports/A18C_latpc_extracted_stats_*.csv

Latest A18A stats field spec:

.local_reports/A18A_latpc_stats_field_spec_*.csv

Latest A18B stats availability matrix:

.local_reports/A18B_latpc_stats_availability_matrix_*.csv

A16 reference results, if present:

.local_reports/A16C_latpc_experiment_results_*.csv
.local_reports/A16D_latpc_baseline_vs_noop_compare_*.csv

## Validation objectives

1. Behavior neutrality

Stats-only instrumentation should not change baseline behavior.

Compare standard fields:

- cycles
- instructions
- ipc
- l2_accesses
- l2_misses

Prefer comparing A18 baseline vs A18 stats-only if both runs exist.

If only one A18 run exists, compare against latest A16 baseline for the same workload if available, but document that build/config changes may make this a weaker comparison.

2. Latpc stats presence

For every field in A18A/A18B:

- IMPLEMENTED fields should appear in extracted stats.
- DERIVED fields should be produced by scripts or listed as derived.
- APPROXIMATED fields should have notes.
- UNAVAILABLE fields should not be treated as failure.
- DEFERRED fields should not be treated as failure.

3. Sanity checks

Where values exist:

- counts should be non-negative.
- histogram bins should be non-negative.
- page divergence bin sum should be consistent with sample count if both exist.
- reservation failure rate denominator should not be zero before computing rate.
- avg unique stride should not be computed without samples.

## Tolerance policy

Integer exact fields:

- tolerance 0

Floating fields:

- absolute tolerance 1e-9
- relative tolerance 1e-6

If A18 is compared to A16 and build string or source changed, use strict comparison but report mismatches carefully.

## Required output files

.local_reports/A18D_latpc_stats_only_validation_<timestamp>.md
.local_reports/A18D_latpc_behavior_compare_<timestamp>.csv
.local_reports/A18D_latpc_stats_presence_<timestamp>.csv

## Behavior compare CSV columns

Include at least:

- field
- reference_run
- instrumented_run
- reference_value
- instrumented_value
- abs_diff
- rel_diff
- tolerance_abs
- tolerance_rel
- status
- notes

status values:

- PASS
- FAIL
- MISSING
- SKIPPED

## Stats presence CSV columns

Include at least:

- stat_name
- expected_availability
- found
- value
- status
- source
- notes

status values:

- PASS
- MISSING_IMPLEMENTED
- UNAVAILABLE_OK
- DEFERRED_OK
- DERIVED_OK
- APPROXIMATED_OK
- FAIL_INVALID_VALUE

## Summary MD sections

1. Validation summary.
2. Behavior comparison.
3. Stats presence summary.
4. Sanity check summary.
5. Final A18D status.
6. Whether A18 is ready for future A19/A20.
7. Limitations.

## Status rules

PASS:
Behavior comparison passes and implemented stats are present.

PASS_WITH_WARNINGS:
Behavior passes but some optional or partial stats are missing, or comparison used A16 reference instead of A18 paired run.

PASS_DESIGN_ONLY:
A18B did not instrument source due to blocked foundation.

FAIL_BEHAVIOR_CHANGED:
Any exact behavior field differs beyond tolerance in a paired A18 baseline vs stats-only comparison.

FAIL_STATS_MISSING:
Implemented stats are missing from output.

FAIL_NO_RESULTS:
A18C results are missing.

## Important notes

Do not hide behavior changes.

If behavior changed, mark FAIL_BEHAVIOR_CHANGED and do not recommend mechanism implementation.

If stats are all zero, decide based on context:

- zero warp or translation stats on a memory workload is suspicious and should be warning or fail
- zero MSHR reservation failures may be valid for a low-pressure run
- zero PTW stall cycles may be valid but should be documented
