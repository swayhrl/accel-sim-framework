# A16D LATPC baseline vs no-op validation guidance

## Goal

Compare baseline and latpc_noop results from A16C and validate that the no-op variant slot is equivalent to baseline.

A16D determines whether the variant pipeline is trustworthy before any LATPC mechanism implementation.

## Inputs

A16C results:

.local_reports/A16C_latpc_experiment_results_*.csv
.local_reports/A16C_latpc_command_matrix_*.csv
.local_reports/A16C_latpc_runner_summary_*.md

A11 stats equivalence matrix, if present:

.local_reports/A11_stats_equivalence_matrix_*.csv

A14 mini result table, if present:

.local_reports/A14_mini_result_table_*.csv

## Required tracked script

Create or update:

scripts/accelsim/a16_latpc_validate_noop.py

## Validation behavior

The validator should:

1. Record start time, end time, and wall seconds.
2. Load the latest A16C result CSV.
3. Ensure exactly one baseline row and one latpc_noop row for the selected workload.
4. Identify comparable stats fields.
5. Compare baseline vs latpc_noop.
6. Write comparison CSV and validation summary MD.
7. Assign a final status.

## Comparable field policy

Prefer A11 fields where equivalence class is exact or approximate.

Because A11 column names may differ, implement robust detection:

- Read latest A11_stats_equivalence_matrix_*.csv if present.
- Identify columns containing field names and equivalence labels by case-insensitive matching.
- Treat values containing exact as exact fields.
- Treat values containing approx or approximate as approximate fields.

If A11 is missing or unparsable, fall back to these normalized fields if present:

- cycles
- instructions
- ipc
- l2_accesses
- l2_misses

## Tolerance policy

For no-op equivalence:

Exact integer fields:

- expected difference: 0
- tolerance: 0

Floating fields:

- absolute tolerance: 1e-9
- relative tolerance: 1e-6

If prior scripts already use a different tolerance for approximate fields, document and use the stricter reasonable tolerance.

If a field is missing from either variant:

- mark field status as MISSING
- do not fail the whole round if at least one meaningful field passes
- use PASS_WITH_WARNINGS if enough fields pass but some expected fields are missing

## Required output files

.local_reports/A16D_latpc_baseline_vs_noop_compare_<timestamp>.csv
.local_reports/A16D_latpc_validation_summary_<timestamp>.md

Optionally rewrite or copy normalized pair result:

.local_reports/A16D_latpc_baseline_vs_noop_results_<timestamp>.csv

## Comparison CSV columns

Include at least:

- paper
- workload
- field
- field_class
- baseline_value
- latpc_noop_value
- abs_diff
- rel_diff
- tolerance_abs
- tolerance_rel
- status
- notes

Field status values:

- PASS
- FAIL
- MISSING
- NON_NUMERIC
- SKIPPED

## Summary MD contents

Include:

- selected workload
- input result CSV
- number of fields compared
- number of pass, fail, missing, skipped fields
- final status
- any blocker
- statement that latpc_noop is an infrastructure validation only
- next recommended step after A16

## A16D status rules

PASS:

- both variants ran successfully
- at least one meaningful comparable field exists
- all compared exact or approximate fields are within tolerance

PASS_WITH_WARNINGS:

- core fields pass, but some expected fields are missing or skipped

FAIL_NOOP_MISMATCH:

- any compared exact field differs beyond tolerance
- or approximate fields differ beyond tolerance without explanation

FAIL_NO_RESULTS:

- missing A16C result CSV
- or missing baseline/no-op row

## Important notes

A no-op mismatch is serious. Do not paper over it.

If baseline and no-op differ, inspect A16C command matrix first. Most likely causes:

- config path differs
- kernelslist differs
- working directory differs
- environment variable accidentally affects simulator behavior
- parser used different stats files

Do not proceed to A17 mechanism implementation if A16D fails.
