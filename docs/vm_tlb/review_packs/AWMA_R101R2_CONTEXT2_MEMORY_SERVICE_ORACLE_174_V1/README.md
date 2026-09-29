# AWMA R101R2 CONTEXT2 memory-service oracle - 174 V1

Status: `R101R2_O2_MEMORY_SERVICE_HEADROOM_PRESENT`.

Stage: `AWMA_R101R2_CONTEXT2_MEMORY_SERVICE_ORACLE_V1`.

Primary result:

- B0 measured ROI: 2,985,319 cycles;
- O2 measured ROI: 1,130,670 cycles;
- O2 improvement: 62.1256555832%;
- context state/counters: exact match;
- O2 qualified transactions: 29,937,568;
- scheduled = one-cycle-ready = retired; all violation/outstanding counters 0;
- 6/6 coverage and full correctness/terminal gates PASS.

O2 is `ORACLE_ONE_CYCLE_UNBOUNDED_SERVICE`, an upper-bound localization
diagnostic, not a hardware mechanism. The result exceeds the preregistered 5%
gate and is outside the 3%-7% repeat band, so no repeat was run.

No FULL5, O3, holdout, new 109 capture, scratchpad/DSMEM mechanism or parameter
sweep was run.

Recommended reading order:

1. `R101_INHERITANCE.md`
2. `CONTEXT2_DERIVATION_RECEIPT.json`
3. `O2_DESIGN_AND_SCOPE.md`
4. `OFF_EQUIVALENCE.tsv` and `O2_DIRECTED_TESTS.tsv`
5. `B0_CONTEXT2_RESULTS.tsv` and `O2_CONTEXT2_RESULTS.tsv`
6. `ROI_COMPARISON.tsv`
7. `FINAL_DECISION.md`
8. `RUN_RECEIPTS.json`, `RAW_DATA_INDEX.tsv`, `SHA256SUMS`

The formal simulator logs completed successfully. Their initial summarization
failure was an orchestration-only in-flight-directory arm parsing bug; recovery
receipts prove the raw bytes remained unchanged and no simulator rerun occurred.
