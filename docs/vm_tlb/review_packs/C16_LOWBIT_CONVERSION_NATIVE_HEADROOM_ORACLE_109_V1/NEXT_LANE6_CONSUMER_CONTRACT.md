# Lane 6 independent consumer contract

Recompute all medians, CVs, intervals, and speedup ratios from
`TIMING_SAMPLES.tsv`; do not use `HEADROOM_SUMMARY.json` as input.

Verify:

1. accepted strong-W4 source/binary authority and discovery output hash;
2. accepted/baseline SASS key-count equality;
3. oracle LDG/LDS/STS/HMMA/STG/BAR preservation and HADD2/HFMA2 removal;
4. all three runtime compressed-source dependency canaries;
5. predecoded correctness and expanded-byte accounting;
6. the 1.10 discovery gate and the absence of validation samples;
7. both lock receipts, including the disclosed zero-sample failed preflight.

Do not run GPU work, expand targets, read Lane4 partial results, or reinterpret
the oracle as an implementable speedup or strict physical upper bound.
