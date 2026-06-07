# A18C LATPC build and stats probe guidance

## Goal

Build the repository after A18B and run a bounded stats probe on the A16 selected workload.

The preferred workload is NW from A16.

## Required script

Create:

scripts/accelsim/a18_latpc_stats_probe_runner.py

## Inputs

Latest A18B summary:

.local_reports/A18B_latpc_stats_instrumentation_summary_*.md

Latest A16 selected workload JSON:

.local_reports/A16A_latpc_selected_workload_*.json

Existing A16/A13 runner scripts and reports.

## Runner behavior

The runner should:

1. Record start time, end time, and wall seconds.
2. Determine whether A18B made source changes.
3. If source changes were made, run the appropriate build command.
4. Reuse the A16 selected workload and command pattern.
5. Run a bounded baseline command.
6. Run a stats-only command only if there is a harmless metadata/config way to distinguish it.
7. If no stats-only variant config exists, run the same baseline command once or twice and document the mode.
8. Parse standard stats.
9. Parse latpc_* stats from logs or stats output.
10. Write probe result CSV, extracted stats CSV, and summary MD.

## Build command policy

First search existing scripts for the established build command.

Likely candidates:

- make -C gpu-simulator
- make -C gpu-simulator -j
- scripts/accelsim existing A1/A6 build scripts

Use the repository's existing pattern.

Write build output to:

.local_logs/A18C_<timestamp>_build.log

Do not paste long build logs into chat.

## Run command policy

Reuse A16 runner logic where possible.

Search and reuse:

- scripts/accelsim/run_a16_latpc_variant_matrix.py
- scripts/accelsim/a16_latpc_variant_lib.py
- A16C command matrix report

The run must be bounded:

- selected workload only
- baseline and possibly stats-only only
- no full benchmark campaign
- no 24 workload campaign
- no NVBit tracer generation

## Required output files

.local_reports/A18C_latpc_build_and_probe_summary_<timestamp>.md
.local_reports/A18C_latpc_stats_probe_results_<timestamp>.csv
.local_reports/A18C_latpc_extracted_stats_<timestamp>.csv

Logs:

.local_logs/A18C_<timestamp>_build.log
.local_logs/A18C_<timestamp>_baseline.log
.local_logs/A18C_<timestamp>_stats_only.log

If only one run is executed, still write a stats_only log path column as empty or same-as-baseline with notes.

## Probe results CSV columns

Include at least:

- paper
- workload
- run_id
- run_kind
- command
- log_path
- return_code
- status
- cycles
- instructions
- ipc
- l2_accesses
- l2_misses
- latpc_stats_count
- notes

## Extracted stats CSV columns

Include at least:

- run_id
- stat_name
- value
- source
- availability
- notes

## Latpc stats parser

Parse lines like:

latpc_name = value
latpc_name: value
latpc_name value

Be robust to spaces.

Only parse numeric values.

## Summary MD sections

1. Build status.
2. Run status.
3. Selected workload.
4. Commands used.
5. Standard stats found.
6. latpc_* stats found.
7. Missing latpc stats.
8. Limitations.
9. Whether A18D validation can proceed.

## Status rules

PASS:
Build passed, selected workload ran, standard stats parsed, and at least one latpc_* stat parsed.

PASS_WITH_WARNINGS:
Build and run passed, but only partial latpc stats are present.

PASS_DESIGN_ONLY:
A18B had no source changes due to blocked foundation; no build/run required.

FAIL_BUILD:
Build failed.

FAIL_RUN:
Run failed.

FAIL_STATS_MISSING:
Run passed but no standard stats or no expected latpc stats can be parsed after instrumentation.

## Important notes

A18C should not try to fix complex simulator bugs. If build or run fails, preserve logs and write a clear report.

Do not run full workloads.
Do not run tracer.
