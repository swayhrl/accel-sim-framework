# Native grouped-CTA runner contract

Build one independent extension from `MAPPING_SOURCE.patch.gz`; record patched source/module hashes. All eight cells import the same module and differ only in K, split, and runtime mapping_mode.

First close correctness and launch identity. Within a split, ROW and GROUP_M16 outputs must be bitwise equal. Across split1/split8 retain rtol=1e-2 and atol=5e-2. Every row must match `EXPECTED_LAUNCH.tsv` and show no data-layout or allocation change.

ROW cells are the mandatory calibration. Compare their medians with `ROW_CALIBRATION.tsv`; if relative deviation exceeds 5% and both accepted and new CV, STOP before interpreting GROUP_M16.

Timing uses 10 global warmups, 25 complete mirror blocks, 50 samples/cell, and two same-cell warmups/sample. Frozen mirror order: `A_ROW,B_ROW,A_GROUP,B_GROUP,B_GROUP,A_GROUP,B_ROW,A_ROW`.

Run one NCU profile per cell under the same GPU lock. Separate split8 GEMM and reduction. Primary mapping comparisons use GEMM L2 read hit/miss sectors, GEMM DRAM bytes, and module timing. Stop on patch/module drift, correctness/coverage/launch failure, ROW calibration failure, metric ambiguity, incomplete mirror blocks, or lock failure.
