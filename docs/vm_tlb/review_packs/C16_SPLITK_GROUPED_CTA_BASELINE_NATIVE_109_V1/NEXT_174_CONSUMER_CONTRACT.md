# Lane 6 / 174-new independent consumer contract

Consume branch `hrl/c16-splitk-grouped-cta-baseline-native-109-v1` only after
fetch-back verification.  Recompute every derived quantity from
`NCU_KERNEL_ROWS.tsv` and `TIMING_SAMPLES.tsv`, not from producer summaries.

Required checks:

1. Verify `SHA256SUMS`, gate/build bindings, one extension path/function, and
   mapping-mode receipts (`ROW=0`, `GROUP_M16=1`).
2. Verify ROW/GROUP bitwise equality, accepted ROW output SHA closure, A/B
   correctness, static bijection/coverage, exact launches, and 50 samples/cell.
3. Independently recompute ROW calibration using the accepted historical
   median/CV contract and confirm no material-overhead STOP.
4. Normalize NCU units before recomputing hit fractions, miss sectors, DRAM,
   duration, ROW-to-GROUP effects, and GROUP_M16 split1-vs-split8 comparisons.
5. Preserve the claim boundary: software mapping strong baseline only; no claim
   about physical issue order or universal kernel policy.

Do not access Lane 4 partial results, run GPU work, sweep GROUP_M, add points,
capture SASS, or run Accel-Sim.
