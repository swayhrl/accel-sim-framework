# Runtime environment audit final

- Node109 is RTX4080 AD103/SM89, driver 580.178.04, CUDA-driver compatibility 13.0.
- The isolated environment is `/data/c16/envs/c16-vllm-v0.30.0-sm89-v1`; historical AutoAWQ/NVBit environments were not modified.
- Official vLLM 0.30.0 wheel/sdist are hash-pinned, and every preflight-pinned runtime source anchor matches the installed package.
- Torch is 2.13.0+cu130; the default host toolkit remains 12.8, while the wheel carries its CUDA 13 runtime. `pip check` and the candidate-library-path ELF dependency audit pass.
- Qwen BF16 merged MLP, AWQ group128 zero-point/lossless repack/Marlin, and OLMoE FusedMoE/routing are source-qualified. Actual selected kernels remain unknown and require an approved GPU canary.
- NSYS 2024.6.2 and NCU 2025.1.1 metadata are available; NCU lists AD103. Exact metric names are not frozen. Direct translation/PTW blocked-time remains unqualified.
- OLMoE graph ON is `STRONG_RUNTIME_VRAM_RISK`; static estimates do not declare failure.
- Final status: `RUNTIME_ENV_READY_FOR_GPU_CANARY_REVIEW`. No model load, CUDA execution, capture, profiling, or campaign measurement occurred.
