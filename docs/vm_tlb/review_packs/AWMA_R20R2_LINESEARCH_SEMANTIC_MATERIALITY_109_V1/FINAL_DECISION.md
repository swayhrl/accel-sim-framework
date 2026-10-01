# R20R2 scientific decision

`R20R2_LINESEARCH_DIAGNOSTIC_THRESHOLD_ONLY`

The goal captured both `LS_ITERATIONS` outcomes for the same hash-frozen t152/world413 solver entry. The flag flip is localized to the fixed source's inner line-search convergence threshold at outer iteration 2. The set case uses the same kind of selected step but reaches the unchanged 20-iteration bound; complete-solver coverage and outer iteration count are identical, while final valid numerical outputs remain inside the pre-existing local B0 numerical contract. The fixed source writes the bit after applying the step and does not consume the bit as a subsequent numerical-control input in this path. The bounded graph-local scratch audit found no specific hidden-state error required to explain the observation.

This classification is scoped to this solver-entry diagnostic. It does **not** say the line search mathematically converged in the set-bit run, that every future LS bit flip is harmless, or that a future active-world S1 is correct or fast. R20R1's accepted `exact stop-signature` failure is unchanged. A future revised contract is proposed separately for review; no S1 or performance measurement was run in this Goal.

Evidence: `SOURCE_SEMANTICS.md`, `OBSERVER_CONTRACT.md`, `OBSERVER_OFF_REGRESSION.json`, `T152_REPEAT_SUMMARY.tsv`, `WORLD413_LINESEARCH_TRACE_SUMMARY.md`, `WORLD413_LINESEARCH_TRACES.json`, `WORLD413_FLAG_PAIR_ANALYSIS.json`, `SCRATCH_AUDIT.md`, raw receipts and immutable hashes on node164.
