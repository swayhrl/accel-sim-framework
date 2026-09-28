# Lane 6 / 174-new independent consumer contract

Consume producer branch
`hrl/c16-splitk-crossm-reuse-causal-native-109-v1` only after fetch-back SHA
verification.  Recompute all four SHARED-vs-PER_MTILE rows directly from
`NCU_KERNEL_ROWS.tsv` and `TIMING_SAMPLES.tsv`; do not trust the producer's
derived table as an input.

Required checks:

1. Verify `SHA256SUMS`, source/gate/build bindings, one extension binary/path,
   and eight-cell matrix closure.
2. Verify all 96 replica slices are identity-pass with non-overlapping VA ranges
   per tensor allocation, same-split bitwise equality, and frozen A/B tolerance.
3. Verify one GEMM row per cell, one separate reduction row only for split8,
   exact grid/block/scratch, and 50 timing samples per cell.
4. Normalize NCU byte/time units before computing hit fractions, DRAM ratios,
   and timing ratios.
5. Test the preregistered ordering: K2560 split1 large degradation; K3072
   split1 same direction but smaller incremental degradation; split8 large
   degradation at both K values.

Do not use Lane 4 partial results.  Do not expand the matrix, run GPU work,
capture SASS, or run Accel-Sim.
