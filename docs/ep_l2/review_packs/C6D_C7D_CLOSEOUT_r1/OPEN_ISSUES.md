# Open issues

1. **L1 characterization completeness — blocking.** Native L1 failure
   classes exist but final EPL2B0V1 has no stable launch/application aggregate.
   The analyzer correctly emits unavailable rather than guessing from
   `block_l1`. The final campaign cannot answer whether L1 is limiting.
2. **Final-SHA validation evidence — blocking.** No retained compact outputs
   demonstrate full Release build, combined C3-C7/C6d regressions, exact
   OFF/ON timing neutrality, or host-overhead measurement for the final source
   pair.
3. **Generated validation outputs are untracked — nonfunctional hygiene.**
   `c7d_validation_clean/` and `c7d_validation_diagnostic/` are intentionally
   excluded to avoid committing raw logs. They are indexed in
   `RAW_LOG_INDEX.tsv`; source files are otherwise clean.

There is no open C6d payload/bank correctness failure in the retained smoke
evidence. No Unified, RO, TVD, 1GHz, or final campaign work was started.
