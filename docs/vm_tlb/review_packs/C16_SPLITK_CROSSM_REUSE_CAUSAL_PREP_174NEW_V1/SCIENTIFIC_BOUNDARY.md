# Scientific boundary

This is an artificial address-sharing intervention. It tests whether cross-M reuse of the combined qweight/qzeros/scales address set is an important source of the observed L2 advantage, and whether split-K's smaller local set helps that reuse survive.

A supported screen may claim an important weight-side cross-M reuse contribution for this exact AutoAWQ kernel, GPT-3 proxy shape family, K2560/K3072, and RTX4080 experiment. It may not attribute the effect to qweight alone, infer NVIDIA replacement details, claim a pure-capacity isolation, or generalize to all GEMMs/LLMs.

If PER_MTILE does not materially reduce GEMM read hits and increase misses/DRAM, the current cross-M reuse explanation must be downgraded. Correctness, allocation, and same-binary closure are prerequisites, not evidence for the causal effect by themselves.
