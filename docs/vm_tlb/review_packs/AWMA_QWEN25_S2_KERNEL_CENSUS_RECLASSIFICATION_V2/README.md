# AWMA Qwen2.5 S2 kernel-census reclassification V2 review pack

This pack is the compact review surface for
`AWMA_QWEN25_S2_KERNEL_CENSUS_RECLASSIFICATION_V2`.

Start with the [V2 report](../../codex_handoff/awma/QWEN25_S2_KERNEL_CENSUS_RECLASSIFICATION_V2_REPORT.md), then inspect:

1. `RUN_RECEIPT_V2.json` — machine-readable method, source hashes, phase
   ranges, totals, and invariants.
2. `V2_PHASE_SUMMARY.tsv` — Prefill, Decode step, and auxiliary totals.
3. `V1_TO_V2_ATTRIBUTION_DELTA.tsv` and `V1_UNKNOWN_RECLASSIFIED_V2.tsv` —
   every attribution change and the legitimate former-UNKNOWN subset.
4. `V2_TOP_200_CLASSIFICATIONS.tsv` — compact family/exact-function/grid/block
   review slice.
5. `DURABLE_ARTIFACT_INDEX_V2.json` and `SHA256SUMS` — node164 closure.

The full V2 launch inventory and full classification table remain on node164;
their paths, sizes, and SHA-256 values are recorded in the durable index. V1
remains read-only historical evidence. This work performs no capture and makes
no semantic mapping from kernel names or launch order.
