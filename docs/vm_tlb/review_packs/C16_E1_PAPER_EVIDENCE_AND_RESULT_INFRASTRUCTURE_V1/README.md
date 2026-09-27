# C16 E1 paper evidence and result infrastructure V1

Authority snapshot: framework `8dfd9c0fdc98314c2aa11710da9b89f59e4c7a66` (B16 canary branch, read only), then this isolated paper branch. The accepted independent 174 consumer packs in this tree are the current numeric authority; their `SOURCE_ANCHORS`, decisions and raw-provenance audits bind producer commits. The 109 bounded D1-D3 trace is represented here by the accepted 174 upstream admission audit and address integration pack; the full raw trace is not copied into this branch. The B16 canary pack currently specifies run design and partial diagnostic admission, not an accepted timing result.

Read in order:

1. `C16_E1_EVIDENCE_LEDGER.md` (also JSON/TSV, with authoritative artifact commit and SHA256 for every claim).
2. `C16_E1_PAPER_DRAFT_V0_1.md` and `CLAIM_BOUNDARY_MATRIX.md`.
3. `FIGURE_TABLE_PLAN.md`, generated `PAPER_RESULTS_CURRENT.tsv/json`, and `figures/`.
4. `B16_DECISION_TEMPLATE.md` and `RELATED_WORK_INDEX.md`.
5. `SOURCE_ANCHORS.json`, `SOURCE_CLOSURE.json`, `RAW_LOG_INDEX.tsv`, `VALIDATION_SUMMARY.json`, `OPEN_ISSUES.json`, `CHANGE_SUMMARY.md`, `COMMIT_HISTORY.md` and `SHA256SUMS` for review closure.

Rebuild from a clean checkout of the branch:

```bash
python3 util/vm_tlb/c16/paper_result_ingest/ingest.py
python3 util/vm_tlb/c16/paper_result_ingest/ledger.py
python3 util/vm_tlb/c16/paper_result_ingest/plot.py
python3 -m unittest discover -s util/vm_tlb/c16/paper_result_ingest -p 'test_*.py'
python3 util/vm_tlb/c16/paper_result_ingest/closure.py
```

The consumer checks that each required review-pack source is tracked and byte-identical to `HEAD`, checks the accepted stage decision, rejects missing/non-finite/incorrect native fields, and emits source SHA256 plus the artifact's introducing commit on every accepted row. B16/B8/B24/BFULL simulator slots are explicit `PENDING` with null JSON values and no plotted point until an accepted result pack exists. The plots read only the generated machine table. No GPU, full simulator timing or mechanism changes are involved in this goal.

## Future simulator publication contract

An independently reviewed C16 E1 pack may commit `PAPER_SIM_RESULTS_ACCEPTED.json` anywhere under `docs/vm_tlb/review_packs/C16_E1_*/`. Exactly one such file may be present. Required schema is `C16_E1_PAPER_SIM_RESULTS_ACCEPTED_V1`, status `INDEPENDENT_ACCEPTED`, 40-hex `framework_commit` and `core_commit`, 64-hex `trace_sha256`, nonempty `independent_review_pack`, and a `results` object keyed only by B8/B16/B24/BFULL. Each present budget must contain `correctness_pass: true`, `terminal_pass: true`, positive `baseline_cycles` and `candidate_cycles`, and nonnegative integer `mechanism_activations`, `protected_hits`, `admission_denials`. The source itself must be committed. The independent review pack must carry its normal raw index, identity and comparison gates; this publication file is a machine interface to that closed review, not a substitute for it. Missing budgets remain pending. After accepted publication, rerunning the three commands refreshes the tables and simulator panel without hand-entered measurements or code changes.

The current story closes the observation and mechanism rationale. A positive simulator system result, a unique explanation of the native offset, and a final related-work section are not yet established.
