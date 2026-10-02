# RULE_U01 contract

Frozen before retrospective arithmetic:

```text
IF legal_union_fraction < 0.01:
    execute A3_RAGGED_DIRECT
ELSE:
    execute A0_DENSE_VENDOR
```

Definitions and restrictions:

- `legal_union_fraction = exact union count of all active requests / 151936`.
- The comparison is strict `< 0.01`; equality selects A0.
- The exact CPU XGrammar masks for the current step are the only legal source.
- No threshold sweep, learned classifier, step deletion, or outcome-dependent
  change is allowed.
- C0 and C1 are discovery cohorts. H0 has already been inspected and is not
  relabeled as an unseen holdout.
- A0/A3 values are joined only at identical `(cohort, repetition, step)` keys.
- The reported rule sum is head-region time before the unmeasured dispatch
  signal cost. It is not a live mixed trajectory or complete-generation result.
- Per-step `min(A0,A3)` is an explicitly nondeployable timing oracle only.

The output classification is deterministic and recorded in
`RULE_U01_STEP_CLASSIFICATION.tsv`.
