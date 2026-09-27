# R101 NCU preregistration

Stage `AWMA_R101_FIXED_NS_INTERMEDIATE_LIFECYCLE_V1`. Written after formal CUDA-event timing and before any NCU collection.

Admission: same-map S128 F128/K128 numerical gate passed; formal graph replay F128 improved over K128 by about 20.9%, exceeding the frozen 5% and 3× noise gates. Real L256/L512 author compiled paths are material within the selected three-parameter graph optimizer replay. The independent layer12 holdout remains unopened.

Use Nsight Compute 2025.1.1 on node109/RTX4080/SM89. Local `--query-metrics --devices 0` and suffix query confirmed these exact metrics:

- `dram__bytes_read.sum`
- `dram__bytes_write.sum`
- `lts__t_bytes.sum` (L2 requested bytes, not DRAM bytes)
- `sm__cycles_active.sum`
- `sm__warps_active.avg.pct_of_peak_sustained_active`

At most two standalone profiles, each using the frozen discovery gradient-derived tile payload, author 5-step coefficients and compiled 3-kernel path:

1. `K128`: 581 BF16 128×128 tiles, identical to the F128 control input. NVTX range `R101_NCU_K128`.
2. `L512`: 44 BF16 512×512 tiles. NVTX range `R101_NCU_L512`.

Warm JIT/autotune outside each NVTX range. Use the existing GPU campaign lock for the complete process. Use `--nvtx --nvtx-include` to profile one source-correct call. Collect only the five listed metrics, with `--cache-control none`; save `.ncu-rep` and raw CSV on node164. Verify the output against the accepted numerical canary after the profiled call. Do not use NCU replay durations as operator latency and do not infer physical page/TLB behavior from these counters. Distinguish source-derived logical intermediate bytes from the measured NCU DRAM/L2 counters. If the first profile fails due platform/permission availability, record that and do not attempt a redundant second profile.
