# AWMA R101R3 bounded service / handoff screen - 174 V1

Status: `R101R3_S1_BELOW_5_PERCENT_H1_NOT_TRIGGERED`.

Primary result:

- accepted B0 ROI: 2,985,319 cycles;
- accepted O2 ROI: 1,130,670 cycles;
- finite partition-side S1 ROI: 2,963,656 cycles;
- S1 improvement versus B0: 0.7256510946%;
- preregistered survivor gate: at least 5%;
- H1 and L3: not triggered and not run.

S1 preserves normal VM, L1, request ICNT, the existing L2 hit data/return
resources and normal completion paths. It serves all 29,937,568 legal measured
transient transactions and reduces measured L2 misses/DRAM reads to 3,209, but
the cycle response remains below the gate.

This establishes that the large pre-L1 O2 response does not survive the
bounded partition-side placement strongly enough in this CONTEXT2. It does not
measure additive L1/ICNT/cache time and does not establish hardware speedup.

Recommended reading order:

1. `FINAL_DECISION.md`
2. `STAGE_A_ANALYSIS.md`
3. `STAGE_A_EXISTING_EVIDENCE.tsv`
4. `REGION_OPCODE_COMPOSITION.tsv`
5. `PRODUCER_CONSUMER_AVAILABILITY.tsv`
6. `S1_DESIGN_AND_COST.md`
7. `S1_DIRECTED_TESTS.tsv`
8. `S1_CONTEXT2_RESULTS.tsv`
9. `RUN_RECEIPTS.json`
10. `RAW_DATA_INDEX.tsv` and `SHA256SUMS`

Large raw and the per-line/sector ledger remain on node164:

`/root/share/mnt164/huangrulin/awma_r101r3_bounded_service_handoff_174_v1/`.
