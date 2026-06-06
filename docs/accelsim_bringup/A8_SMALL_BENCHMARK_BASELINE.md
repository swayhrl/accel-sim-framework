# A8 small benchmark baseline

## Goal

Generate a bounded small benchmark baseline using the A7B N-app runner.

This is a small baseline for infrastructure validation, not a full paper evaluation.

## Required tracked script

Create:

    scripts/accelsim/a8_small_benchmark_baseline.sh

## Inputs

Support:

    ACCELSIM_TRACE_ROOT
    ACCELSIM_A8_RUN_NAME
    ACCELSIM_A8_MAX_APPS
    ACCELSIM_A8_TIMEOUT_SEC
    ACCELSIM_A8_INCLUDE_MICRO
    ACCELSIM_A8_DRY_RUN

Defaults:

    ACCELSIM_A8_RUN_NAME=A8_small_benchmark_baseline_TIMESTAMP
    ACCELSIM_A8_MAX_APPS=5
    ACCELSIM_A8_TIMEOUT_SEC=900
    ACCELSIM_A8_INCLUDE_MICRO=1
    ACCELSIM_A8_DRY_RUN=0

## Behavior

1. cd to repo root.
2. Source scripts/accelsim/accelsim_env.sh.
3. Refuse to run if simulator binary is missing.
4. Determine trace root from env or previous reports.
5. Discover available kernelslist.g files.
6. Build a small suite:
   - prefer Rodinia functional test traces first
   - optionally add GPU microbenchmark traces only if already present
   - do not download new datasets
   - do not exceed ACCELSIM_A8_MAX_APPS
7. Run via scripts/accelsim/a7b_n_app_smoke.sh or reuse its direct-run logic.
8. Save:
   - .local_reports/A8_small_benchmark_baseline_TIMESTAMP.md
   - .local_reports/A8_small_benchmark_baseline_TIMESTAMP_stats.csv
   - .local_logs/A8_*.log
9. Include summary:
   - number of candidates discovered
   - number selected
   - number passed
   - number failed
   - number timed out
   - trace root
   - config files
   - baseline commit

## Baseline quality rules

A8 should only be considered baseline-quality if A7A passed.

If A7A did not pass, A8 may still run for debugging, but status must be:

    PARTIAL_PASS_NOT_BASELINE_QUALITY

## Required tracked doc

Create or update:

    docs/accelsim_bringup/SMALL_BENCHMARK_BASELINE.md

It must explain:

- what is included.
- what is excluded.
- why this is not full Rodinia.
- how to rerun.
- how to interpret the CSV.
- how this prepares for later paper reproduction.

## A8 pass criteria

- A8 script exists and is executable.
- dry-run works.
- real run executes a bounded small suite if traces exist.
- aggregate stats CSV exists.
- A8 report exists.
- no full benchmark campaign is run.
