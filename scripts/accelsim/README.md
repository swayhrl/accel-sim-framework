# Accel-Sim Bringup Scripts

Reusable smoke scripts for local Accel-Sim bringup. Run them from the repository root unless noted.

## Environment

```bash
source scripts/accelsim/accelsim_env.sh
```

## A0 Environment Check

```bash
bash scripts/accelsim/a0_env_check.sh
```

## A1 Build Smoke

```bash
bash scripts/accelsim/a1_build_smoke.sh
```

## A2 Pre-Trace Smoke

Use an explicit trace root when available:

```bash
ACCELSIM_TRACE_ROOT=/path/to/traces bash scripts/accelsim/a2_pretrace_smoke.sh
```

Without `ACCELSIM_TRACE_ROOT`, the script searches `.local_traces` and `hw_run`. If no trace is found, it downloads the small official `tesla-v100/rodinia_2.0-ft` pre-trace suite.

## A3 Tracer Smoke

Requires a visible NVIDIA GPU, NVBit-compatible driver stack, and CUDA:

```bash
bash scripts/accelsim/a3_trace_rodinia_smoke.sh
```

No GPU is reported as `BLOCKED_NO_GPU`, not as a pass.

## A4 Smoke Suite

Dry-run:

```bash
ACCELSIM_DRY_RUN=1 bash scripts/accelsim/a4_run_smoke_suite.sh
```

Real run with an explicit trace root:

```bash
ACCELSIM_TRACE_ROOT=/path/to/traces bash scripts/accelsim/a4_run_smoke_suite.sh
```

Useful knobs:

```bash
ACCELSIM_BENCH_LIST=rodinia_2.0-ft
ACCELSIM_CONFIG_LIST=QV100-SASS
ACCELSIM_RUN_NAME=my_smoke
ACCELSIM_MAX_JOBS=1
```

## A5 Collect Results

```bash
bash scripts/accelsim/a5_collect_results.sh
```

## A6B-A9 Pipeline

Audit version strings:

```bash
bash scripts/accelsim/a6b_version_string_audit.sh
```

Clean baseline rerun:

```bash
bash scripts/accelsim/a7a_clean_baseline_hardened.sh
```

N-app smoke:

```bash
ACCELSIM_A7B_DRY_RUN=1 bash scripts/accelsim/a7b_n_app_smoke.sh
bash scripts/accelsim/a7b_n_app_smoke.sh
```

Small baseline and workflow alignment:

```bash
bash scripts/accelsim/a8_small_benchmark_baseline.sh
bash scripts/accelsim/a9_mascar_medic_alignment.sh
```

Local logs, reports, runs, traces, and review packs stay under ignored local paths.
