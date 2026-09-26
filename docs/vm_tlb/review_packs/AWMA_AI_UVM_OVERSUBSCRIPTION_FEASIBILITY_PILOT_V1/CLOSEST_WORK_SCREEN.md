# Closest-work screen

- Shao et al., *Oversubscribing GPU Unified Virtual Memory: Implications and Suggestions* (ICPE 2022), https://doi.org/10.1145/3489525.3511691 — closest ratio/access-pattern characterization and complex prefetch sensitivity; it does not establish these AI-shaped laws on this platform.
- Kim et al., *Batch-Aware Unified Memory Management in GPUs* (ASPLOS 2020), https://hparch.gatech.edu/papers/kim-asplos20.pdf — analyzes fault batching and eviction scheduling; this pilot observes migration but proposes no scheduling mechanism.
- Ganguly et al., *Adaptive Page Migration for Irregular Data-intensive Applications under GPU Memory Oversubscription* (IPDPS 2020), https://doi.org/10.1109/IPDPS47924.2020.00054 — distinguishes regular and sparse patterns and migration/zero-copy choices; P1/P2/P3 provide a bounded AI-shaped problem-discovery bridge only.
- Jones et al., *HELM* (SC 2025), https://doi.org/10.1145/3712285.3759812 — closest telemetry-driven UVM characterization; this platform exposes migration memcpy but not dedicated fault counters.
- Park et al., *Avatar* (MICRO 2024), https://www.cs.cmu.edu/~18742/papers/Park2024.pdf — studies speculative address translation and reports 130% oversubscription sensitivity. This pilot does not measure TLB behavior and cannot validate or refute Avatar.
- NVIDIA, *Improving GPU Memory Oversubscription Performance*, https://developer.nvidia.com/blog/?p=37205 — platform guidance that access pattern and placement strongly affect oversubscription.
