# Native SM89 FP8 consumer identity

Source authority: NVIDIA Transformer Engine v2.19.0, exact checkout `5e52befd5262c06289106338c308079d6adb391f`. In `transformer_engine/pytorch/module/linear.py`, the FP8 forward path quantizes BF16 input unless it is already `QuantizedTensorStorage`, then prepares/reuses the FP8 weight workspace and calls `general_gemm`. In `transformer_engine/pytorch/cpp_extensions/gemm.py::general_gemm`, quantized tensors are unwrapped and the native non-custom branch calls `tex.generic_gemm`. Source alone does not prove which device kernel ran.

One bounded NSYS 2024.6 capture of three A1/D0 pairs provided runtime evidence. `parse_nsys.py` joined each CUPTI kernel's correlation ID to its CPU runtime launch, then to the same-thread NVTX range. It attributed 18 launches to six ranges:

- Each A1 range: four current-scaling preparation kernels and one `sm89_xmma_gemm_e4m3bf16_e4m3f32_f32_tn_n_tilesize64x128x64_stage4_warpsize2x2x1_tensor16x8x32_execute_kernel__5x_cublas`, `grid=(4,38,1)`, `block=(128,1,1)`.
- Each D0 range: only that **exact** cuBLAS FP8 GEMM function and same grid/block.
- The GEMM service durations were A1 `16.000/16.416/16.064 µs`, D0 `15.968/16.032/16.000 µs`. A1's four prep-kernel service totals were `4.832/5.024/4.864 µs` across the three ranges.

The explicit `sm89_xmma_gemm_e4m3...` runtime function plus source dispatch and exact quantized payload receipt establish a native Ada E4M3 consumer, not a BF16 fallback inferred from metadata. NSYS ranges had profiler-dependent inter-kernel idle time and do not replace the separate uninstrumented formal timing. Full function names, launch geometry, timestamps and correlation IDs are in node164 `raw/NSYS_KERNEL_IDENTITY.tsv`; raw `.nsys-rep` and exported SQLite are also retained. NCU was unnecessary for this identity question and was not run.
