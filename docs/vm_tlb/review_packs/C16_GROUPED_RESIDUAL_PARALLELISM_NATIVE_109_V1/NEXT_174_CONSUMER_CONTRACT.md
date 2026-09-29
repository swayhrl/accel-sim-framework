# Lane 6 / 174-new independent consumer contract

Consume branch `hrl/c16-grouped-residual-parallelism-native-109-v1` only after
fetch-back verification.  Independently recompute all derived quantities from
`NCU_KERNEL_ROWS.tsv` and `TIMING_SAMPLES.tsv`.

Required checks:

1. Verify `SHA256SUMS`, gate/build/synthetic bindings, the one extension path,
   all eight `GROUP_FULL_M` mapping-mode receipts, and exact launches.
2. Verify four bitwise A/B correctness rows and the fixed rotated timing
   schedule with 50 samples per cell.
3. Normalize NCU units; keep split8 GEMM and reduction rows separate.
4. Recompute L2 hit, DRAM, duration, launch waves/SM, active-warps percentage,
   reduction fraction, and split1 relative gain for each M.
5. Test the preregistered sequence: M1 vs M16 partial-tile difference, monotonic
   decay from M16 to M64, high split1 hit, and M64 crossover.

Do not access Lane 4 partial results, run GPU work, add shapes/splits/GROUP_M,
capture SASS, or run Accel-Sim.
