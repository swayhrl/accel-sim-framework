# Ruled-out scientific space

This stage begins after three independent negative pivots. The following spaces
are closed for this Goal and are not treated as candidate mechanisms.

## Translation and address translation

Classic intra-warp VPN dedup covers the earlier PREL1 opportunity. Native Atlas
finds path sensitivity but no capacity/walker/queue residual, and L2/M2 controls
show no new translation problem. TLB hit latency, PTW, page size, coalescing,
translation prefetch, and translation sharing are therefore ruled out.

## UVM and placement

The 1.094x-VRAM Llama KV transition is real but belongs to established UVM,
KV placement, and offload territory. OLMoE is naturally resident. The PyTorch
managed bridge remains an engineering gap and is not repaired here. No larger
model or artificial expert oversubscription is introduced.

## Generic modeled GPU resources

Cache/MSHR/DRAM scaling produced low, diminishing, or non-monotonic responses;
the one larger L1/M1 response is scale sensitivity rather than model-family
causality. CCWS, adaptive cache management, cache bypass, memory scheduling,
and backend-pressure scheduling directly cover generic pressure control.
Tensor/SFU source coupling is not repaired to fill a matrix.

## Object names without semantic evidence

The accepted formal NVBit ingest preserves all Q05 attention/GEMM addresses as
`UNKNOWN_RUNTIME`. One older formal simulator target has KV versus unknown-data
counts, but no matched weights/activation/lifetime contrast and no attributed
performance cost. Naming weights, KV, activations, or metadata does not create
a problem statement.

## Generic fusion and representation overhead

Intermediate HBM materialization and launch overhead are the explicit targets
of ClusterFusion/DeepFusion-style work. Dequantization overhead, low-bit kernel
packing, and memory-side dequantization are explicit targets of AWQ, QServe/QoQ,
and StreamDQ. Existing AWQ evidence lacks a matched raw-7B timing/traffic arm;
the raw deployment is OOM and the semantic diagnostic forbids timing use.

## Provisional C16 assets

Blocked-model campaign rows, missing-payload identities, semantic-diagnostic
timing, and `UNKNOWN_RUNTIME` addresses are indexed as boundaries, not silently
promoted into evidence.
