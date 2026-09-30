# AWMA R101R5 Native post-L1 downstream realism check

Stage: `AWMA_R101R5_NATIVE_POST_L1_DOWNSTREAM_REALISM_CHECK_V1`
Lane F: node109 / RTX4080 SM89
Scientific parent: `d96a64da8311c1bdee8f23f3d83ce665395060d1`
Handoff HEAD: `ef01d870d90eae89f529bad31a882debd1139b2b`

Decision: **`NATIVE_POST_L1_DOWNSTREAM_SUPPORT_NOT_OBSERVED`**. See `FINAL_DECISION.md` for the exact three-target facts and scope. This is a bounded native counter check, not a re-run of the accepted R101 graph timing or the R101R4 simulator.

Phase A verified accepted L512 NCU report/CSV/receipt hashes and found that the report lacked all core issue/stall evidence. Phase B therefore made exactly three serial, lock-held NCU jobs, one each for the second NS recurrence XXT, BA, and BMM-add. The profiler selected exact function names within the accepted natural L512 five-step invocation, with `--launch-skip 1 --launch-count 1`, same grid/block, same accepted input, source, and author numerical tolerance. Each job required 11 internal NCU replay passes. No GPU work ran outside the campaign lock; it was released when the three jobs finished.

`EXISTING_NCU_AUDIT.md`, `EXISTING_METRIC_INVENTORY.tsv`, and `TARGET_BINDING.tsv` close Phase A. `NCU_CAPABILITY_QUERY.txt` and `METRIC_BINDING.tsv` close actual node109 capability. `NATIVE_DOWNSTREAM_PROFILE.tsv`, `STALL_COMPOSITION.tsv`, `SOURCE_PC_ATTRIBUTION.tsv`, and `SOURCE_PC_SUMMARY.json` contain compact factual results. `RUN_RECEIPTS.json`, `RAW_DATA_INDEX.tsv`, and `SHA256SUMS` close provenance. Large NCU reports, raw exports, full metric query, and logs are stored at the node164 path recorded in `RAW_DATA_INDEX.tsv`.

Accepted L512 payload SHA256: `1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234`. Accepted HiMuon source commit: `af89eda9a0176effed99e1fe19cc1f8a1a2c9588`. The accepted R101 NCU receipt did not preserve an exact cubin SHA; the new reports close actual native kernel name/grid/block/occurrence and their report hashes, without retroactively inventing that historical cubin binding.
