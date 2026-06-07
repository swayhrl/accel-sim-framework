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

## A10 Real Workload Alignment

A10 reads prior Mascar/MeDiC GPGPU-Sim artifacts under `/workspace/repos`, extracts real workload/stat evidence, maps the intersection to available Accel-Sim traces, and runs a bounded aligned smoke.

```bash
bash scripts/accelsim/a10a_discover_prior_workflows.sh
python3 scripts/accelsim/a10b_extract_prior_inventory.py
python3 scripts/accelsim/a10c_build_trace_mapping.py
ACCELSIM_A10D_DRY_RUN=1 bash scripts/accelsim/a10d_run_aligned_smoke.sh
bash scripts/accelsim/a10d_run_aligned_smoke.sh
bash scripts/accelsim/a10e_collect_alignment_pack.sh
```

Coordinator:

```bash
bash scripts/accelsim/a10_run_all.sh
```

The coordinator requires a clean git tree before it starts.

## A11-A15 Paper Reproduction Pipeline

A11-A15 prepares the bounded paper-reproduction infrastructure without implementing paper mechanisms:

```bash
python3 scripts/accelsim/a11_stats_equivalence_narrow.py
python3 scripts/accelsim/a12_workload_config_lockdown.py
ACCELSIM_A13_DRY_RUN=1 python3 scripts/accelsim/a13_experiment_matrix_runner.py
python3 scripts/accelsim/a13_experiment_matrix_runner.py
bash scripts/accelsim/a14_reproduction_readiness_closeout.sh
bash scripts/accelsim/a15_trace_gpu_gap_plan.sh
```

Coordinator:

```bash
bash scripts/accelsim/a11_a15_run_all.sh
```

A13 defaults to the smoke set and baseline variant only. A15 records GPU/tracer gaps and does not fail only because no GPU is visible.

## A16 LATPC No-op Variant Slot

A16 validates a paper-specific baseline-vs-variant path for LATPC without implementing LATPC:

```bash
python3 scripts/accelsim/a16_latpc_paper_profile.py
python3 scripts/accelsim/a16_latpc_variant_slot.py
python3 scripts/accelsim/run_a16_latpc_variant_matrix.py
python3 scripts/accelsim/a16_latpc_validate_noop.py
python3 scripts/accelsim/a16_latpc_closeout.py
```

`latpc_noop` must use the same simulator binary, trace, config, and simulator arguments as `baseline`.
