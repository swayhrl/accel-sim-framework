# Native runner contract

This pack prepares but does not run the experiment. A future Lane 7 run must first bind the exact early-gate commit and obtain one GPU lock covering build qualification, correctness, timing, and eight NCU profiles.

Build one independent extension from `REPLICA_SOURCE.patch`. Record patched source hashes and the resulting module SHA256. Every K/split/state cell must import that same module and launch the same patched target kernel; state is only runtime mask 0 or 15.

For each K, allocate one input and direct final contiguous 16-replica qweight/qzeros/scales tensors. Hash every replica slice and record non-overlapping VA ranges. Reuse the identical live assets across SHARED/PER_MTILE; do not regenerate or reallocate between those states.

Qualify all eight cells against `EXPECTED_LAUNCH.tsv`. Within a split, SHARED and PER_MTILE outputs must be bitwise equal. Across split8/split1, retain rtol=1e-2 and atol=5e-2; record naturally bitwise-equal cases without generalizing them.

Timing uses 10 global warmups, then 25 mirror blocks and 50 samples/cell with two same-cell warmups per sample. Frozen mirror order is `A_SHARED,B_SHARED,A_PER_MTILE,B_PER_MTILE,B_PER_MTILE,A_PER_MTILE,B_SHARED,A_SHARED`.

Run exactly one NCU profile per cell. Separate split8 GEMM and reduction rows. The primary causal comparison uses GEMM L2 read hit/miss sectors, GEMM DRAM bytes, and module timing; reduction is reported but excluded from the weight-side mechanism contrast.

Stop on module/source drift, tensor hash or VA overlap failure, allocation asymmetry, launch/scratch/grid drift, same-split non-bitwise output, missing GEMM/reduction separation, NCU metric ambiguity, or any lock failure. Do not fall back to original binaries or broaden K/M/N/split.
