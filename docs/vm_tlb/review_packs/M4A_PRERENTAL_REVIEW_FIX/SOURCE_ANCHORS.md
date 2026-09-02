# Source anchors

| RF gate | Evidence |
|---|---|
| RF0 | Started clean at required `38c9b224dae55002b159f07c9f4fc3b4035ce8d5`; prior package `f74b08f8` |
| RF1 | `build_nvbit_with_toolchain.sh`; frozen tracer Makefile `NVCC`, `PTXAS`, and `NVCC_PATH` behavior; fake A/B toolchain test |
| RF2 | `capture_ready_preflight.py:inspect_toolchain`; explicit `--cuda-home` routed by `run_m4a_c.sh` |
| RF3 | `util/tracer_nvbit/tracer_tool/tracer_tool.cu` `API_CUDA_cuMemcpyHtoD_v2`; `test_roi_memcpy_policy.py` |
| RF4 | `classify_kernels.py` v2 and `NCCL_KERNEL_POLICY.md` |
| RF5 | `CAPTURE_ENV_LOCK.md` artifact digests and `LOCKED_ARTIFACTS` validation table |
| RF6 | `VALIDATION_SUMMARY.md` |
| RF7 | this review pack and `LATEST_REPORT.md` |

The tracer source change is a project capture-tracer correction only: it gates
HtoD list insertion by the pre-existing profiler ROI state. No VM/TLB semantic
or Segmentation source changed.
