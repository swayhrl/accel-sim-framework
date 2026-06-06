# Accel-Sim Bringup Runbook

## 1. Environment

```bash
source scripts/accelsim/accelsim_env.sh
bash scripts/accelsim/a0_env_check.sh
```

## 2. Build

```bash
bash scripts/accelsim/a1_build_smoke.sh
```

Verify `gpu-simulator/bin/release/accel-sim.out` exists and is executable.

## 3. Pre-Trace Smoke

```bash
bash scripts/accelsim/a2_pretrace_smoke.sh
```

To force a trace root:

```bash
ACCELSIM_TRACE_ROOT=/path/to/trace/root bash scripts/accelsim/a2_pretrace_smoke.sh
```

## 4. Tracer Smoke

Run only on a GPU-enabled machine:

```bash
bash scripts/accelsim/a3_trace_rodinia_smoke.sh
```

`BLOCKED_NO_GPU` means the tracer path was not tested.

## 5. Benchmark Smoke Suite

Dry-run:

```bash
ACCELSIM_DRY_RUN=1 bash scripts/accelsim/a4_run_smoke_suite.sh
```

Real smoke:

```bash
bash scripts/accelsim/a4_run_smoke_suite.sh
```

Useful overrides:

```bash
ACCELSIM_BENCH_LIST=rodinia_2.0-ft
ACCELSIM_CONFIG_LIST=QV100-SASS
ACCELSIM_TRACE_ROOT=/path/to/trace/root
ACCELSIM_RUN_NAME=my_run
ACCELSIM_MAX_JOBS=1
```

## 6. Stats And Review Pack

```bash
bash scripts/accelsim/a5_collect_results.sh
```

Stats CSV files are written to `.local_reports/*_stats.csv`.

## A6B-A9 Baseline Pipeline

```bash
bash scripts/accelsim/a6b_version_string_audit.sh
bash scripts/accelsim/a7a_clean_baseline_hardened.sh
ACCELSIM_A7B_DRY_RUN=1 bash scripts/accelsim/a7b_n_app_smoke.sh
bash scripts/accelsim/a7b_n_app_smoke.sh
ACCELSIM_A8_DRY_RUN=1 bash scripts/accelsim/a8_small_benchmark_baseline.sh
bash scripts/accelsim/a8_small_benchmark_baseline.sh
ACCELSIM_A9_DRY_RUN=1 bash scripts/accelsim/a9_mascar_medic_alignment.sh
bash scripts/accelsim/a9_mascar_medic_alignment.sh
```

For rebuild or baseline-quality runs, commit tracked changes first and confirm `git status --short` is empty before starting.

## A10 Real Workload Alignment

Run A10 only from a clean committed tree:

```bash
bash scripts/accelsim/a10a_discover_prior_workflows.sh
python3 scripts/accelsim/a10b_extract_prior_inventory.py
python3 scripts/accelsim/a10c_build_trace_mapping.py
ACCELSIM_A10D_DRY_RUN=1 bash scripts/accelsim/a10d_run_aligned_smoke.sh
bash scripts/accelsim/a10d_run_aligned_smoke.sh
bash scripts/accelsim/a10e_collect_alignment_pack.sh
```

Or use:

```bash
bash scripts/accelsim/a10_run_all.sh
```

A10 is read-only with respect to prior repos under `/workspace/repos`. It writes inventories, mappings, smoke stats, and review packs only under ignored local output paths.

## 7. Local Outputs

- Reports: `.local_reports/`
- Logs: `.local_logs/`
- Runs: `.local_runs/`
- Pre-traces: `.local_traces/`
- Generated hardware traces: `hw_run/`
- Review packs: `review_packs/`

## 8. Cleanup

```bash
rm -rf .local_reports .local_logs .local_runs .local_traces hw_run review_packs sim_run_*
```

## 9. Do Not Commit

Do not commit logs, traces, run directories, build outputs, `hw_run`, `review_packs`, or downloaded `gpu-app-collection` contents.
