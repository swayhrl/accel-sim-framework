# Native residual-parallelism runner contract

Build one independent extension from `GROUP_FULL_M_SOURCE.patch.gz`; record exact patched source and module SHA256. All eight science cells import that module and pass mapping_mode=1. No ROW, extra M/K/N/split, GROUP_M sweep, replica, EVICT, SASS/NVBit, or simulation is allowed.

For each M, construct tensors exactly from `SYNTHETIC_CONTRACT.json`. The two split arms must share the same live input and weight tensors. Close shape/dtype/finiteness and split1-vs-split8 correctness at rtol=1e-2, atol=5e-2; record natural bitwise equality without generalizing it.

Validate every launch against `EXPECTED_LAUNCH.tsv`, including reduction grid derived as ceil(M*N/512), scratch shape/bytes, block, and GROUP_FULL_M mapping. Stop on any source/module/synthetic/launch/memory drift.

Timing uses 10 global warmups per cell and 25 complete superblocks. Within each M use `A8,B1,B1,A8`; rotate the M order by block index through `[1,16,32,64]`, `[16,32,64,1]`, `[32,64,1,16]`, `[64,1,16,32]`. Use two same-cell warmups per measured call, producing 50 samples/cell. CUDA events enclose only the module call; no conditioner.

Run one NCU profile per cell under the same GPU lock. Separate split8 GEMM and reduction. Freeze L2 read hit/miss sectors, L1/TEX bytes, L2 bytes, DRAM bytes, and duration. Query only a minimal, semantically clear launch waves/SM or active-warps/SM/SM-throughput metric; absence does not block the screen but limits the claim to launch-level CTA supply plus timing.

If split1 L2 hit unexpectedly falls at these capacity-safe points, stop parallelism interpretation and explain cache first. Otherwise interpret split benefit only as a CTA-supply/tile-utilization/reduction tradeoff unless M64 still shows a clear residual with high split1 hit and grid=384.
