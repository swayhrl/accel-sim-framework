# R19E1 IBP direct-consumer design — Lane E / 174-new

Stage: `AWMA_R19E1_IBP_DIRECT_CONSUMER_DESIGN_V1`.

Decision: `R19E1_IBP_DIRECT_CONSUMER_DIAGNOSTIC_NOT_QUALIFIED`.

Pinned Legion/Reddit source writes a full sampled `[N2,602]` FP32 feature buffer in the sampler. Trainer IPC then allocates and copies a second full `[N2,602]` tensor before first-layer `SAGEConv`. With `602>256`, that layer transforms each source row once to `[N2,256]`, reuses it across first-block edges for DGL mean, separately transforms the `N1` destination prefix, and participates in trainer-owned autograd/Adam.

P1 moves trainable first-layer work across processes and requires remote gradients/optimizer/IPC. P2 requires per-tile IPC and tiled linears that change kernel/rounding/latency alongside the raw-buffer boundary. P3 requires a custom first-layer forward/backward and cannot match reuse/order with a small isolated patch. None supports the required two-arm, single-boundary Native falsification. DGL's available COO path uses floating atomic sum; actual runtime dispatch and B0 bitwise repeatability remain unknown because this Goal ran no GPU.

The parent R19 problem hypothesis remains recorded. Its preparation card now explicitly blocks the old 109 performance sketch. The review pack contains exact source receipts, the P1/P2/P3 assessment, numerical pre-run rule, unfilled real-batch manifest, and file/function impact ledger.

No CUDA, GPU lock, 109, Reddit download, GPU compilation, Accel-Sim or hardware design was performed.
