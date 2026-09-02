# Changed files

| Area | Review-fix purpose |
|---|---|
| `util/tracer_nvbit/tracer_tool/tracer_tool.cu` | exclude profiler-inactive HtoD memcpy from formal ROI replay list |
| `util/llm_trace_capture/build_nvbit_with_toolchain.sh` | force/record selected `nvcc` and `ptxas` despite PATH contamination |
| bootstrap, preflight, M4A driver, generic smoke | require explicit CUDA home and prove compiler/runtime provenance |
| classifier, policy, ROI/runbook/lock docs | explicit `MEMCPY` class and updated artifact provenance |
| tests | fake toolchain A/B and source-level ROI memcpy policy |

Route E is unchanged: one physical same-model 4xSM86 host, actual TP=4,
rank-0-only NVBit injection. Full-model one-GPU tracing remains rejected.
