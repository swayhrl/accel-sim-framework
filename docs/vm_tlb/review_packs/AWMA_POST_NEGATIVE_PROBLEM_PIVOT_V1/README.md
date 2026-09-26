# AWMA post-negative problem pivot V1

Final state: **AWMA_POST_NEGATIVE_NO_NEW_PROBLEM_V1**.

This pack is a fail-closed opportunity map after accepted negative results in
translation, model-derived UVM, and generic GPU-resource scaling. It screens
three candidate families without inventing a mechanism first.

Read in this order:

1. `FINAL_DECISION.md`
2. `POST_NEGATIVE_EVIDENCE_INDEX.tsv`
3. `RULED_OUT_SPACE.md`
4. `CANDIDATE_SCREEN.tsv` and `CLOSEST_WORK_MAP.md`
5. `PROBLEM_CARD_1.md` and `CONTEXT_DIAGNOSTIC_PREREGISTRATION.md`
6. `CONTEXT_PREFIX_DIAGNOSTIC.tsv`, `CONTEXT_MATCHED_PAIR_RESULTS.tsv`, and
   `CONTEXT_DIAGNOSTIC_DECISION.md`
7. `FINAL_CANDIDATE_DECISION.tsv`
8. `RAW_DATA_INDEX.tsv` and `SHA256SUMS`

No simulator performance run, GPU capture, model download, parameter sweep, or
prototype was executed. The only new analysis is deterministic offline joining
of accepted context-prefix TSVs.

`NEW_NATIVE_EVIDENCE_REQUEST.md` is intentionally absent: every candidate is
rejected before a novelty-qualified Native question remains.
