# Numerical and lossless contract

## Invariant regardless of design

For every sampled local row `i` and FP32 component `k`, the reconstructed feature's 32-bit pattern must equal the corresponding original Reddit feature's pattern. This includes cache-hit, pinned-host miss and uncompressed-row cases. IDs, first/second block edge arrays and order, cache hit/miss decisions, IBP metadata, model weights, AMP mode and optimizer state are fixed. Exact feature bits do not imply identical floating-point reductions if the first-layer implementation changes.

Pinned GraphSAGE first-layer operator is the source-order expression in `GRAPH_SAGE_SEMANTICS.md`: whole-source `fc_neigh`, DGL g-SpMM sum then degree division, destination-prefix `fc_self`, addition, then outer ReLU/dropout. A D1 must preserve this mathematical expression and the number of unique-row decodes and edge contributions. It may not skip duplicate-edge contributions or replace mean aggregation by a changed algorithm.

## Baseline bitwise status

`UNKNOWN_CPU_ONLY`. The pinned DGL source contains both a CUDA COO floating-point `AtomicAdd` sum path and CSR/CSC traversal paths, and CUDA arithmetic order is relevant to rounding. The source does not pin the runtime sparse format, cuBLAS algorithm, or repeated-output hashes on RTX4080. Calling B0 deterministic or nondeterministic now would fabricate a run result.

The **pre-performance rule**, frozen here, would be:

1. Restore the exact real batch, model, Adam, RNG, cache and process state; run correctness-only B0 replay at least 30 times before any D1 timing. Record pre-ReLU/pre-dropout first-layer `H1[N1,256]` bit patterns, NaN/Inf masks, and first-layer weight-gradient hashes.
2. If all B0 `H1` bit patterns match, D1 must match that exact bit pattern. If they differ, freeze a per-element engineering interval from B0 alone: `[min_r H1_r[i] minus one FP32 ULP, max_r H1_r[i] plus one FP32 ULP]` for finite values, with exact NaN/Inf location/sign rules. The numeric interval and its source B0 hashes must be written to an immutable receipt **before** a D1 performance command. D1 must also preserve the operator/edge order and model/optimizer update contract; this interval cannot legalize an algorithm change.
3. If the B0 variability is too large to make this interval discriminating, or any first-layer-gradient/update comparison fails, do not run D1 performance. No tolerance may be widened after seeing D1.

This pre-registered rule is not a numerical tolerance value: no Reddit batch or B0 replay exists in this CPU-only Goal, and there is no qualified D1. Thus `first_layer_numeric_threshold=NOT_FROZEN_NO_PERFORMANCE_AUTHORITY` in the current replay ledger.
