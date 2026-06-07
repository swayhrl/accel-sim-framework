# A16C LATPC variant matrix runner guidance

## Goal

Extend or create a bounded matrix runner that can run baseline and latpc_noop for the selected LATPC workload.

The runner must be small, safe, and reuse existing A0-A15 smoke or matrix logic where practical.

## Inputs

A16B manifest:

.local_reports/A16B_latpc_variant_manifest_*.json

A16A selected workload JSON:

.local_reports/A16A_latpc_selected_workload_*.json

Existing scripts under:

scripts/accelsim/

Existing prior matrix examples:

.local_reports/A13_experiment_matrix_*.csv
.local_reports/A13_experiment_results_*.csv

## Required tracked script

Create or update:

scripts/accelsim/run_a16_latpc_variant_matrix.py

Optional helper:

scripts/accelsim/a16_latpc_variant_lib.py

## Runner behavior

The runner should:

1. Record start time, end time, and wall seconds.
2. Load the latest A16B manifest.
3. Build a two-row matrix:
   - baseline
   - latpc_noop
4. Resolve simulator command using existing Accel-Sim scripts if possible.
5. Use the exact same simulator inputs for both variants.
6. Run only the selected workload.
7. Write one log file per row under .local_logs.
8. Parse stats using the same parser style as A13 if possible.
9. Write matrix CSV, command matrix CSV, result CSV, and summary MD.

## Reuse policy

First inspect existing scripts in scripts/accelsim.

Search for:

- A13
- experiment matrix
- small benchmark
- smoke suite
- pretrace smoke
- stats parser
- kernelslist
- accel-sim.out

If a reusable A13 runner exists, use it or wrap it.

If no clean reusable entry point exists, implement a small runner by following the actual command pattern in prior A13/A8 reports or scripts.

Do not guess a simulator command without verifying it against existing scripts or reports.

## Required output files

.local_reports/A16C_latpc_variant_matrix_<timestamp>.csv
.local_reports/A16C_latpc_command_matrix_<timestamp>.csv
.local_reports/A16C_latpc_experiment_results_<timestamp>.csv
.local_reports/A16C_latpc_runner_summary_<timestamp>.md

Log files:

.local_logs/A16C_<timestamp>_baseline.log
.local_logs/A16C_<timestamp>_latpc_noop.log

## Matrix CSV columns

Include at least:

- paper
- workload
- variant_id
- variant_kind
- kernelslist_path
- config_path
- simulator_binary
- command_id
- expected_equivalence
- status

## Command matrix CSV columns

Include at least:

- command_id
- variant_id
- cwd
- command
- log_path
- start_time
- end_time
- wall_seconds
- return_code

## Result CSV columns

Include at least:

- paper
- workload
- variant_id
- status
- log_path
- stats_path
- cycles
- instructions
- ipc
- l2_accesses
- l2_misses
- raw_stats_fields_count
- notes

Use the exact field names available from existing parser where possible. If field names differ, include normalized names plus raw field names in notes.

## A16C status rules

PASS:

- both baseline and latpc_noop commands return 0
- required result CSV exists
- at least cycles or instructions or IPC-like field is parsed

PASS_WITH_WARNINGS:

- both commands return 0
- stats parsing is partial but enough for A16D to compare at least one exact or approximate field

FAIL_RUNNER:

- one or both commands fail

BLOCKED_NO_COMMAND:

- runner cannot determine a valid command from existing scripts or reports

BLOCKED_NO_A16B:

- no A16B manifest exists

## Runtime limits

Only run the selected workload.

Do not run all 24 paper workloads.

Do not run the full benchmark suite.

If a simulator command appears to hang or exceeds the existing smoke timeout policy, stop that row, mark it failed, and write logs.

## Important notes

latpc_noop should be deterministic and equivalent to baseline. Any difference in command inputs is a bug unless it is pure metadata that does not affect simulator behavior.

Do not hide failed commands. Write the return code and tail of log path into the summary.
