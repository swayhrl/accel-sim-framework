# Scientific interpretation

## Independent result

The independently consumed evidence is classified as `CASE_B_WITH_CASE_D_ROLE_DEPENDENCE`.

- Refill: AWQ K2/K1 DRAM ratios are 0.00978577 (q_proj), 0.00220884 (down_proj), and 0.00205192 (up_proj), showing a clear immediate-refill transition. RAW_FP16 remains comparatively high-DRAM. Timing K1..K6 statistics, ratios, recovery, and monotonicity diagnostics were independently recomputed; monotonicity is diagnostic, not a gate.
- Capacity-dose: first tested DRAM triggers are q=32 MiB with tested bracket (0,32], down=16 MiB with (0,16], and up=16 MiB with (0,16]. First tested material timing doses are q=32 MiB with (0,32], down=24 MiB with (16,24], and up=28 MiB with (24,28]. These are tested-point observations, not exact physical knee locations or capacity theorems.
- Natural layer-0 reuse: natural DRAM warm fractions are 1.3921–1.4125 for up_proj and 1.0349–1.0459 for down_proj, placing the profiled occurrences at or beyond the isolated dense bracket. Timing is also beyond dense for layer-0 up_proj, while down_proj timing lies between isolated WARM and DENSE.
- Layer 14: timing and DRAM comparisons are explicitly `NO_EXACT_ISOLATED_AUTHORITY`. Layer-0 references are not projected onto layer 14.
- Optional RAW control: seven fresh BF16 full-model processes preserve the accepted token sequence; D0/D3 timing medians are both 0.204800 ms and direct D0 NCU DRAM is 136,006,784 B. This remains a BF16 full-model control only.

## Separated effects

Capacity effect, role/access-policy effect, and natural inter-module interference effect are recorded separately. The evidence supports descriptive natural-reuse/residency closure under the tested points. It does not prove an exact cache capacity, make L2 the unique cause, eliminate TLB contributions, or authorize a cache/TLB mechanism.

Producer summaries were consulted only after independent raw closure. All selected cross-checks matched.
