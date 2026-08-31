# Motivation findings

The final quantified findings are generated from the committed CSVs in this
pack. Interpretation is intentionally scoped as follows:

- **Measured reuse distribution:** the nine Figure-1 bars are exact bounded
  stack distances for frontend L2 demand references in their slice/kernel
  epochs.
- **Measured reuse coverage:** `reuse_coverage.csv` reports reuse-instance
  fraction, unique-line reuse coverage, and one-touch-line fraction.
- **Measured structural blocking composition:** Figure 2 gives the exclusive,
  source-ordered primary reason for each blocked frontend demand-miss
  admission cycle at WBUF=8.
- **Trace-projected WBUF capacity pressure:** Figure 2S reports the same
  observed stream under shadow C=4/8/16 occupancy views. It is neither a
  counterfactual performance simulation nor a speedup result.
- **Archetype inference:** differences across workloads may motivate later
  mechanism evaluation, but these observations do not establish a mechanism
  performance claim.

`OTHER` is retained in `blocking_breakdown.csv` and rendered as a fifth
segment whenever its per-workload rate exceeds 2%.
