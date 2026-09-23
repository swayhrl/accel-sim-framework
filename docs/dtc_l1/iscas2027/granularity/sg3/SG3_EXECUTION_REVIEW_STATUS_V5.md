# SG3 execution review status (V5)

Snapshot time: `2026-09-23T12:55:12Z`.

`SG3_EXECUTION_DATA_SNAPSHOT_V5.tsv` indexes eight new strict-PASS receipts:
the four bounded Btree/2DConvolution cap=512 positive controls, the fresh
GESUMMV/OO baseline, and the currently terminal GESUMMV V4 cap validation
rows.  The two active GESUMMV/IO rows (baseline and cap=2048) are deliberately
absent: neither has a terminal receipt or an inferred result.

BICG remains the only workload with the recorded interim classification.
These receipts do not generalize it to GESUMMV.  The Btree/OO 54 merge-tag
identity-guard retries in the cap=512 receipt are non-resource diagnostic
telemetry and are excluded from resource-bottleneck attribution, consistent
with the pre-existing 319-retry guard rule.  V3 remains preserved; V4 still
permits only the listed GESUMMV cap cells, not automatic capacity/MSHR sweep.
