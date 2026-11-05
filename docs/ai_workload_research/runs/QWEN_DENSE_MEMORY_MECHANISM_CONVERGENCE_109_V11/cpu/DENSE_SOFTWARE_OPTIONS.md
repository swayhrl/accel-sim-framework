# V11 Dense software options

The installed official Torch API preferred_blas_library can set a process-local ATen preference to cublaslt before a fresh engine compiles and captures its graphs. It is a credible small software configuration variable; it is not a guarantee of a different kernel, a speedup, or an independent memory-versus-SM control.

Installed vLLM UnquantizedLinearMethod dispatches CUDA auto through default_unquantized_gemm to F.linear. Accepted generated code uses extern_kernels.mm/addmm. This makes a BLAS preference potentially relevant, but its documented fallback and compiler-generated kernel bypass mean effect must be measured. The B2 CUTLASS WMMA symbol does not alone prove a cuBLASLt API call; existing native CUDA/NVTX traces do not establish that frontend library selection.

If the owner elects one isolated cublaslt-preference engine, record the preference inside the actual worker, use independent caches before compile/capture, verify actual Dense symbols/grid, generated calls, Graph/backend identity and numerical behavior. Unchanged kernels mean NO_OBSERVED_PATH_EFFECT and no expanded sweep. Changes in memory scheduling, tiles and computation are coupled, so a difference would test software choice, not prove memory or compute causality.

Do not blindly try every vLLM linear_backend name. The inspected unquantized BF16 dispatcher only has a non-default flashinfer_cutedsl path requiring SM100; it is not eligible on the SM89 RTX4080. Other generic backend names in the config list may serve quantized or other-platform implementations and fall through to the same F.linear here. Inductor autotune sweeps are more invasive and not justified by the current residual evidence.

No GPU, NVML, Torch/vLLM import, production edit or new execution was performed by this CPU review. DENSE_SOFTWARE_OPTIONS.json records source hashes, line ranges, accepted generated calls and the observation limits.
