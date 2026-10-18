# C2P/M2D future-approval proposal: V2 destination/transaction correction

This amends only the destination/transaction binding in `C2P_M2D_FUTURE_EXACT_RELEASE_APPROVAL_PROPOSAL_V9.md`. Its exact 615-file SHA inventory, 42-directory metadata inventory, source roots, allocated bytes, nonreproducibility warning and **SOURCE_KEEP / no deletion permission** remain unchanged.

The first `C2P_M2D_COPY_READY_INDEX_V9.json` computed transaction IDs from newline-joined fields. Target's pinned `v9_transaction.py` instead requires SHA256 of canonical sorted compact JSON plus newline over the five fields `source_filesystem_identity`, `source_root`, `selector_sha256`, `source_frozen_commit`, and `genuine164_destination_root`. The first transaction IDs are permanently **HOLD**, and target's V1 batch plan/sole-window READY cannot be used to stage data.

The corrected [V2 transaction binding](C2P_M2D_COPY_READY_V2_TARGET_BINDINGS_V9.json) has SHA256 `2ab9ff91a31f3edc5dc5909de2bc7609b46d7459314c1bc1036324b46dbef0d1` at source commit `6a76cda7`; all three exact per-project target manifests and the V2 index were independently read back from GitHub. The source ran the pinned target module's pure `validate_manifest` and `transaction_id` on all three, with [test receipt](C2P_M2D_V2_TARGET_COMPATIBILITY_TEST_V9.json) SHA256 `45b548985b03e3619d7d3d0197bcc015b5c013b38836bc29c0bd048dd06e2c90`.

| Group | Correct canonical txid | Correct genuine164 *final* archive path |
|---|---|---|
| C2P1 | `d07ad19814f68aeb53eecbc76a4896898ed2af30bf2196348117a8680c195048` | `/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_v9_cold_source_01/C2P1/old174/tmp/c2p-gpgpu-pre-attribution-20260822/build/d07ad19814f68aeb53eecbc76a4896898ed2af30bf2196348117a8680c195048` |
| C2P2 | `cd1ea5b35dd161ea42981d8d7d2864b6e1a6b7a0cf848ecaa396b5395ed3806d` | `/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_v9_cold_source_01/C2P2/old174/tmp/c2p-gpgpu-build-20260821/build/cd1ea5b35dd161ea42981d8d7d2864b6e1a6b7a0cf848ecaa396b5395ed3806d` |
| M2D | `9b7971a8bd636476465d5d92fb8330d8502e1c5e775fb7bb8c29cab47ed06779` | `/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_v9_cold_source_01/M2D/old174/tmp/m2d-core-g21/build/9b7971a8bd636476465d5d92fb8330d8502e1c5e775fb7bb8c29cab47ed06779` |

These are **proposed** final paths, not claims that archives exist. Target must independently prove the real164 mount, new absent transaction base and final, one compliant ≤256 MiB bridge batch at a time, closed/reopened archive SHA, numeric native restoration and recovery procedure. Until a new target V2-compatible plan/READY appears, OLD174 publishes no C2P/M2D payload. No source file or directory is to be released under V9.
