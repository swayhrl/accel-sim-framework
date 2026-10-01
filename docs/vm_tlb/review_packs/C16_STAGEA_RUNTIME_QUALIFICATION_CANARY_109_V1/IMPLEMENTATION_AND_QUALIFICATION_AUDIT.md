# Stage A runtime qualification canary audit

- Runtime and asset/input authorities were fetched and verified exactly. Only QWEN_BF16, QWEN_AWQ and OLMOE ran; no holdout point or output was touched.
- All six graph OFF/ON processes loaded and executed under one GPU lock. GPU-active wall was 151 seconds of the 240-second cap; each process returned VRAM to the 35 MiB baseline before the next.
- Qwen BF16 graph correctness, backend identity and instrumentation neutrality passed. MP01/02/03 are `RUNTIME_READY`.
- Qwen AWQ graph correctness passed and runtime selected `AutoAWQMarlinLinearMethod` / `MarlinLinearKernel`; full CPU canonical repack proved no requantization. Instrumentation changed median wall by about 8.09 ms, exceeding the frozen gate, so MP05 is blocked as `INSTRUMENTATION_NON_NEUTRAL`.
- OLMoE graph OFF/ON both fit. Runtime selected FlashAttention and emitted `fused_moe_kernel`, but graph modes differed in 4,761 routing values and sampled-token logprob tolerance failed; MP06 is blocked for correctness.
- Final status is `RUNTIME_QUALIFICATION_PARTIAL`. No scientific performance conclusion or automatic Tier0 contract follows.
