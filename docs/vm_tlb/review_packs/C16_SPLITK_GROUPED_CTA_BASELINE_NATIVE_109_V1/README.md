# C16 Split-K Grouped CTA Baseline Native — Lane 7

Task: `C16_SPLITK_GROUPED_CTA_BASELINE_NATIVE_109_V1`

Status: complete.  Final decision:
`GROUPED_MAPPING_SOLVES_MOST_SPLIT1_REUSE_PROBLEM`.

Lane 8 gate commit `4e7e277ad988155d1c2381700d9ef515dc08b9f0` published
`READY_FOR_GROUPED_CTA_NATIVE_BASELINE`; every bound SHA was verified before
GPU use.  The single lock interval was `2026-09-29T02:11:34Z` through
`2026-09-29T02:11:59Z`, with exit code zero and a confirmed release.

Frozen matrix: `M=256`, `N=49152`, `K={3072,4096}`,
`split={8,1}`, `mapping={ROW,GROUP_M16}`.  No other point is authorized.

All ROW/GROUP_M16 same-split outputs were bitwise identical, ROW output hashes
matched accepted authority, A/B correctness passed, and all launch/coverage
checks closed.  ROW calibration deviations were 0.67%–1.78%, below the frozen
5% materiality boundary.

GROUP_M16 restored split1 L2 read hit from 63.56%/63.26% to 95.95%/95.95% at
K3072/K4096, reduced DRAM to 14.48%/13.51% of ROW, and reduced median module
time to 72.37%/66.93% of ROW.  Under identical GROUP_M16 mapping, split1 was
38.73% and 30.90% faster than split8 at K3072 and K4096.

Recommended reading order: `SOURCE_AND_GATE.json`, `BUILD_RECEIPT.json`,
`CORRECTNESS.tsv`, `ROW_CALIBRATION.tsv`, `GROUPED_BASELINE_SUMMARY.tsv`,
`GROUPED_SPLIT_COMPARISON.tsv`, and `SCIENTIFIC_INTERPRETATION.md`.

No Lane 4 partial result was accessed.  No GROUP_M sweep, extra shape/split/K,
replica/EVICT experiment, SASS capture, or Accel-Sim run was added.
