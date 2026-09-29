# AWMA R101R4 local-service path localization - 174 V1

Status: `R101R4_P0_AND_P1_MATERIAL_POST_L1_DOWNSTREAM_LOCALIZED`.

Primary result:

- accepted B0 ROI: 2,985,319 cycles;
- accepted O2 ROI: 1,130,670 cycles (62.1256555832% improvement);
- finite pre-L1 P0 ROI: 1,130,670 cycles (62.1256555832% improvement);
- post-L1 P1 ROI: 2,737,282 cycles (8.3085593198% improvement);
- accepted partition-side S1 ROI: 2,963,656 cycles (0.7256510946% improvement).

P0 exactly retains O2's ROI under the frozen finite 1/16 queue envelope, so
unbounded queue capacity is not required for the accepted O2 response.  P1
retains normal L1 lookup, reservation/merge, miss and fill behavior and remains
above the preregistered 5% gate.  The accepted S1 response is below 5%.

The allowed localization is therefore that material response remains after the
L1 miss decision but disappears at S1's partition-side placement.  It does not
identify request ICNT, return ICNT, ingress, L2 or any one downstream component
as an additive runtime fraction.

Required Native recommendation:

`NATIVE_CHECK_WARRANTED_POST_L1_DOWNSTREAM`

Recommended reading order:

1. `FINAL_DECISION.md`
2. `SOURCE_PATH_MAP.md`
3. `P0_DESIGN_AND_COST.md` and `P0_CONTEXT2_RESULTS.tsv`
4. `P1_DESIGN_AND_COST.md` and `P1_CONTEXT2_RESULTS.tsv`
5. `VALIDATION_SUMMARY.md` and `P1_DIRECTED_TESTS.tsv`
6. `RUN_RECEIPTS.json`
7. `RAW_DATA_INDEX.tsv` and `SHA256SUMS`

Large raw and frozen runtimes remain on node164:

`/root/share/mnt164/huangrulin/awma_r101r4_local_service_path_localization_174_v1/`.
