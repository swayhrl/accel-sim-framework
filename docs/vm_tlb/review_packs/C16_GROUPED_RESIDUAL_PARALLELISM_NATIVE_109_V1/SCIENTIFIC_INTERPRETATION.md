# Scientific interpretation

Decision: `LOW_CTA_SUPPLY_RESIDUAL_WITH_M64_CROSSOVER`.

All cells used the same patched target kernel and GROUP_FULL_M path.  Static
coverage/address-set proofs and dynamic launch checks passed.  Split1 and
split8 outputs were bitwise identical at every M, and weight-side bytes were
identical across the matrix.

Module medians establish a monotonic boundary:

| M | split1 CTA | split8 median | split1 median | outcome |
|---:|---:|---:|---:|---|
| 1 | 96 | 0.032976 ms | 0.074752 ms | split8 55.9% faster |
| 16 | 96 | 0.040976 ms | 0.076800 ms | split8 46.6% faster |
| 32 | 192 | 0.067584 ms | 0.086016 ms | split8 21.4% faster |
| 64 | 384 | 0.119808 ms | 0.113904 ms | split1 4.93% faster |

M1 and M16 have identical GEMM CTA counts, yet split8 helps more at M1.  This
shows partial-M tile utilization/effective work participates in the choice;
CTA count alone is insufficient.  From M16 through M64, split8 benefit steadily
decays as split1 supply rises from 96 to 384 CTAs and finally reverses.

Cache does not explain the trend.  Split1 GEMM L2 read hit is 100% for every M,
as is split8.  Weight-side footprint is 24.9375 MiB, and observed GEMM DRAM is
small; the old ROW capacity knee does not reappear.

NCU provides direct corroboration without a section sweep.  Split1 launch waves
per SM rise from 0.14 at M1/M16 to 0.28 at M32 and 0.56 at M64; active-warps
percent of elapsed peak rises from about 5.0% to 9.5% and 17.8%.  Split8 values
are higher throughout (waves 1.12/1.12/2.25/4.49; active warps
24.2%/24.3%/30.2%/33.6%).

The split8 GEMM duration advantage shrinks monotonically: split8/split1 GEMM
duration is 0.399x, 0.473x, 0.707x, then 0.961x.  Reduction consumes about
11.4%, 11.7%, 9.6%, and 8.1% of profile-local split8 GEMM+reduction kernel time.
Thus GEMM parallelism gain covers reduction at M1/M16/M32, but not at M64.

This closes the result as a classic low-parallelism decomposition boundary,
within existing Stream-K/parallel-decomposition territory.  It does not justify
a new cache mechanism or full-model extrapolation.
