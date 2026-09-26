# Closest-work screen

- Shao et al., *Oversubscribing GPU Unified Virtual Memory: Implications and Suggestions* (ICPE 2022), https://doi.org/10.1145/3489525.3511691 — already establishes access-pattern and prefetch sensitivity under UVM oversubscription.
- Allen and Ge, *Demystifying GPU UVM Cost with Deep Runtime and Workload Analysis* (IPDPS 2021), https://doi.org/10.1109/IPDPS49936.2021.00055 — already analyzes migration/fault overhead and counterproductive prefetch behavior.
- Jones et al., *HELM* (SC 2025), https://doi.org/10.1145/3712285.3759812 — telemetry-driven UVM characterization and policy selection are existing work; this run lacks HELM-style dedicated fault telemetry.
- Jung et al., *DeepUM: Tensor Migration and Prefetching in Unified Memory* (ASPLOS 2023), https://doi.org/10.1145/3575693.3575736 — tensor-aware UVM prefetch and migration for DNNs are existing mechanism territory.
- Sheng et al., *FlexGen* (ICML 2023), https://proceedings.mlr.press/v202/sheng23a.html, and Jiang et al., *NEO* (2024), https://arxiv.org/abs/2411.01142 — weight/KV placement and CPU offload for constrained LLM inference are established.
- Kim et al., *ES-MoE* (ICML 2024), https://proceedings.mlr.press/v235/kim24w.html, and Zhou et al., *FloE* (ICML 2025), https://proceedings.mlr.press/v267/zhou25j.html — expert offload, overlap, and sparse expert residency are established. Sparse activation itself is not treated as novelty here.

Screen result: the observed KV oversubscription transition and current-step-prefetch penalty are concrete, but not distinct from known UVM/offloading problems. The resident actual-route MoE replay does not expose a new oversubscribed regime.
