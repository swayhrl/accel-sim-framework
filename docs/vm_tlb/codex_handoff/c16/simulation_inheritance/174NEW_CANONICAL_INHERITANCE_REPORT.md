# 174-new canonical C12–C15 inheritance report

Status: `C12_C15_174NEW_INHERITANCE_PASS_REPLAY_ENVIRONMENT_BLOCKED`.

Branch: `hrl/c12-c15-174new-canonical-inheritance-v2`, based on coordination HEAD `4ca4ef4ab3f25319430b76f14ff69c1d69b158a4`.

Consumed destination inventory `0cc24b1d0d7829a95f9122937bf88dde8d403992` and old174 private closeout `3c62c749e3c5251f6bb8e1383cb1886521008d8e` (archaeology authority `872423194e393fac9ca85171c77bafa87bde389e`). Independently verified the exchange control-plane hashes supplied by old174, including `PRIVATE_EXPORT_READY.json` SHA `32dff617...`, manifest SHA `62564e06...`, tree-manifest SHA `e03b1e3f...`, and `PRIVATE_EXPORT_SHA256SUMS` SHA `f2ae361e...`.

Created canonical node164 historical namespaces and copied three selected shared historical trees (M4C controls, M4B replay logs, EP-L2/cache experiments) with source/destination manifest equality. Copied all five verified private-only export assets to `private_export/` without source deletion. Destination file hashes are recorded in the canonical receipts directory. M4A's 10-GB formal archive source and current M4I staging were referenced in place rather than duplicated.

Produced normalized C12/C13/C14/C15 lineage, baseline, status, asset-catalog, and Git-authority tables under node164 `derived/datasets/historical_simulation/`. Scientific labels remain conservative: C12 F0 formal baseline; C13/C14 diagnostic; C15 static/diagnostic; PRE_FIX retained as PRE_FIX.

Runtime reconstruction was attempted actively. Framework `d64408a...` plus fetched Core `hrl/vm-core-v0` failed to build because `nvcc` is absent; exact historical Core object `57bb71...` and binary SHA `2351f67...` were not found. A non-matching EP-L2 binary was bounded-tested on one real traceg anchor: VM overlay rejected as unknown, stripped-base retry timed out at 30 seconds (`RC=124`) after telemetry output. This is not a reproduction claim.

Current C16 MREF-sharded/JSONL artifacts remain `NOT_PROVEN_LOSSLESS` for Accel-Sim `traceg` conversion. No fabricated traceg converter was created; the future capture contract freezes required ordering, opcode, width, mask, warp/CTA, synchronization, and SHA-bound sidecars.
