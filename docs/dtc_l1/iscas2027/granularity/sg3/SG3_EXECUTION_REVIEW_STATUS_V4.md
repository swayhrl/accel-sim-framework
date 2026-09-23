# SG3 execution review status (V4)

Snapshot time: `2026-09-23T00:24:32Z`.

`SG3_EXECUTION_DATA_SNAPSHOT_V4.tsv` contains 18 accepted rows: four shared
A1 baselines, the complete BICG IO/OO A2 coarse screen (capacity, MSHR, and
DTC-cap), and the named Btree/OO V3 reconciliation receipt.

The Btree/OO aggregate has 319 inferred merge-tag identity-guard retries.
They are non-resource diagnostic telemetry only and are excluded from every
L2 resource-bottleneck total, ranking, trigger, and paper attribution.

The GESUMMV IO and OO A1 baseline attempts exited `-9`; their strict receipts
are preserved as FAIL and no result is included. Because their A1 gates did
not pass, no GESUMMV A2 row was launched. Historical unvalidated GESUMMV
attempts and prior plans remain preserved; they are not silently promoted.
