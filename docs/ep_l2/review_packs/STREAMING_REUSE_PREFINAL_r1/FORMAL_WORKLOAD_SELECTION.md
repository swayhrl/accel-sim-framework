# Additional-workload selection

The original Motivation ten remain the formal basis; one (`scan`) is still pending. Three additions were selected from completed, valid screening records on quantitative sector behavior, not benchmark names:

| Selected workload | Total sector references | Spatial-new fraction | Temporal-sector fraction | One-touch sector fraction | Rationale |
| --- | ---: | ---: | ---: | ---: | --- |
| BlackScholes | 62,500 | 75.000% | 0.000% | 100.000% | Clean spatial-only continuation control. |
| mergeSort | 19,701 | 65.240% | 10.497% | 90.268% | Low-but-nonzero exact temporal reuse contrast. |
| transpose | 1,867,776 | 63.158% | 15.789% | 93.750% | Higher temporal share while preserving dominant sector spatial continuation. |

No additional screened workload met a defensible *strong far-reuse* criterion. The largest new-pool `>1024` temporal-reuse share was bfs_65536 at 0.1674%, and its `>4096` share was 0%; selected candidates have 0% at both thresholds. Accordingly: `NO_STRONG_FAR_REUSE_FOUND_IN_SCREENED_POOL`. No archetype label was inferred from a name, and no far-reuse workload was fabricated.

