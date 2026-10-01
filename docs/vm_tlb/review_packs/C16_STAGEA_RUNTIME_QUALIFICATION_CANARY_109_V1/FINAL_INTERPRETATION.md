# Final qualification interpretation

This goal is partial. Qwen BF16 qualifies the runtime for MP01/02/03. Qwen AWQ is blocked by the pre-registered instrumentation-neutrality gate despite graph correctness and a valid Marlin/no-requantization path. OLMoE fits in both graph modes but fails graph OFF/ON routing and numeric correctness. Therefore MP05 and MP06 are not runtime-ready, and the Stage A Tier0 formal contract cannot yet be prepared. No latency values in this pack are scientific performance evidence.
