# Final R19E1 decision

`R19E1_IBP_DIRECT_CONSUMER_DIAGNOSTIC_NOT_QUALIFIED`

The R19 parent correctly identified a real sampled-feature dense boundary in Legion/Reddit. The pinned implementation makes this boundary harder to isolate than the parent preparation card assumed: sampler writes a full `N2×602` GPU feature buffer, and trainer `cuda_get_next` creates and copies a second full tensor before the first `SAGEConv`. The first layer computes one `fc_neigh` transformation per sampled source, reuses those transformed rows for multiple edges, separately transforms the `N1` destination prefix, and uses DGL g-SpMM sum/degree mean. The same model/optimizer and backward pass live in the trainer process.

- P1 moves trainable first-layer forward across the process boundary and would require remote autograd, gradient and optimizer state transfer.
- P2 can bound raw staging only by adding per-tile IPC and splitting whole-matrix linears; that changes launch/GEMM structure and introduces a second timing cause. A two-arm B0–D1 result would not isolate raw materialization.
- P3 requires custom decode+first-layer forward/backward, with source-row reuse and FP32 order unresolved.

The source-only work cannot establish repeated B0 bitwise determinism, select actual runtime DGL sparse format, or freeze real Reddit batch/cache/model hashes. All three options therefore fail the mandated same-semantics causal diagnostic gate. No D1 patch or future 109 performance command is issued. The parent R19 opportunity status is preserved as a problem hypothesis; this design does not authorize its experiment.

The exact blocked replay fields and pre-performance numerical rule are in `FUTURE_REPLAY_CONTRACT.md` and `NUMERICAL_CONTRACT.md`. This is a negative design qualification, not evidence that the full dense buffer has zero cost.
