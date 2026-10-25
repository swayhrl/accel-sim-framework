# Lane T2 archive report — FINAL_ALL_FROZEN_SCOPES_COMMITTED

Evidence snapshot: 2026-10-25T14:26:41.006322+08:00. Original queue SHA256 `718f30ec3bc8e5ece20df02cd472ebee17eac320f7b5a9e5b5e69841cc63cc04`.

The original 115 scopes remain unchanged. **115 committed, 0 current HOLD, 0 pending/in-progress**. Content archived in this execution: 199,632,736,880 bytes. T2 adds 101 assets / 88,845,765,793 bytes after the 14-asset takeover baseline.

| Group | Frozen | Committed | HOLD | Pending | Committed logical bytes |
|---|---:|---:|---:|---:|---:|
| TRACE | 51 | 51 | 0 | 0 | 199,409,597,483 |
| DTC_RAW | 63 | 63 | 0 | 0 | 222,915,898 |
| Q05_FIXED10000 | 1 | 1 | 0 | 0 | 223,499 |

The complete 115-row state table is `FROZEN115_FINAL_STATE_TABLE.csv`; new asset IDs and COMMITs are `NEW_T2_COMMITTED_ASSETS.csv`. `MEMBER_SHA_INDEX.csv.gz` and its lossless hash receipt retain every audited committed member SHA, numeric metadata and genuine164 path. `CONTENT_AND_RESTORE_CLOSURE.json` contains the COMMIT → manifest/ranges/tree and Source EOF proof checks. This review does not claim to have repeated all large payload hashes.

Prior 20 trace selectors: 20/20 metadata/COMMIT readbacks PASS; their 22,507,635,190 bytes are reused, never added to T2 new bytes. The already archived R13 package is 17,943,970,556 bytes and remains separately accounted. `TRACE51_COVERAGE.csv` identifies metadata supplements and reused input bodies; `.trace`, `.traceg`, full/fraction/trim and packages/expanded members are not equated.

`POLYBENCH_VARIANT_COVERAGE.csv` carries the 28 mandatory historical variants and four supplemental rows. Historical out-of-queue content or scientific HOLDs remain explicit and do not become new tasks or successful frozen-copy claims. `Q05_EXACT_SCOPE.json` binds fixed10000 run.log to SHA256 `06822c9fb9d2de0208eb51fb61c82f21150f509b8320662fd935efbac283843f`; natural R0 is a different object.

Complete native Target recovery is verified for 80 scopes of this frozen115 execution / 123,192,127 bytes. These are not necessarily new T2 restorations. Other restoration states: `{"FULL_NATIVE_RESTORE_HOLD": 5, "FULL_NATIVE_RESTORE_NOT_PERFORMED_EXCEEDS_BOUND": 30, "RESTORE_VERIFIED_NATIVE_TARGET": 80}`. Full native restores above the qualified 240 MiB window were not performed. Their immutable raw trees, complete file SHA, original numeric metadata and bounded recovery helpers are retained; unrestricted full native recovery and scientific runtime acceptance are not claimed.

Historical exact retirement: 8,423 T-owned test-copy files, 4 approved Source kernel files, plus the one cold polybench package. Allocated bytes unlinked: Target test copies 527,740,928; Source kernel files 476,585,984; Source package 17,944,014,848. Independently observed operation-interval SSD free-space deltas: pool 18,936,295,424; Source unlink intervals 18,420,580,352. These are distinct measures and are not added to archive volume. T2 has not replayed any retirement or performed a new Source retirement.

Current shared SSD free: 23,460,798,464 bytes; Share/MD127 free: 36,581,072,896; genuine164 free: 48,301,648,097,280. Current free-space changes include other projects and are not attributed to this archiver.

All per-asset genuine164 bundle and recovery entries are in `CONTENT_AND_RESTORE_CLOSURE.json`; prior 20 reuse links are in the same file. The existing five-minute publication receipts remain `../checkpoint/recovery_20261025/PUBLICATION_RECEIPTS.jsonl`.

Final process shutdown, two-namespace sender/receiver checks, partial-transaction accounting and GitHub remote readback are closed. `FINAL_PROCESS_SHUTDOWN_AUDIT.json`, `REQUIREMENT_CLOSURE_AUDIT.json` and `FINAL_GITHUB_REMOTE_READBACK.json` contain the evidence.

Additional user-authorized 174-new cold compiler-copy retirement: 2,341 exact files; logical bytes 1,834,022,818; allocated file bytes unlinked 1,838,903,296; independently observed SSD free-space interval delta 1,816,342,528. Concurrent project writes prevent exclusive causal attribution of that interval delta. These measures are separate from each other, the historical releases and frozen115 archive bytes. Exact whitelist, SHA/metadata, COMMIT, INTENT/DONE, recovery test and restore entry are under `reclaim_174new/`. No old174 Source files were deleted by this additional retirement.

Recorded execution-admission error: the one 84,346,374-byte native restore test used a base-only SSD check instead of all declared reservations and the active-science gate. It passed SHA/metadata verification and its 84,353,024 allocated bytes were removed, without counting them as original-copy reclaim. `reclaim_174new/RESTORE_TEST_ADMISSION_DEVIATION.json` preserves the executed version and correction. Future test allocations now require the original full admission plus complete test-file capacity; directed checks include reservation shortfall and active-science I/O rejection. Content/receipt closure PASS does not erase this admission deviation.

The subsequent explicit user authorization in `ACTIVE_SCIENCE_IO_GATE_USER_AUTHORIZATION.json` changes only the active-science avg10 I/O check to monitor-only. It does not retroactively authorize the earlier restore-test admission error. At that transition sustained severe host-I/O protection, SSD/RAM reservations, locks, rate/staging limits and scientific identity checks remained unchanged. `io_policy_transition/` retains directed qualification, the exact old/new supervisor identities and proof that the original deadline and cumulative counters were preserved during that policy reload; the Publisher was not restarted.

A later explicit authorization in `TRANSFER_RATE_USER_AUTHORIZATION.json` permits staged Source/aggregate transfer limits up to 60/120 MiB/s, initially 30/60. Cooperative post-COMMIT rate handoff closed: True. Last observed active policy: `{"authorization_sha256": "08a52b3fb8dc865d85fe9f805de96ebb8714eda8a7e95fcac13c02b5de6d060a", "schema": "LANE_T2_ACTIVE_TRANSFER_RATE_TIER_V1", "source_MiB_per_second": 60, "tier_receipt": "/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/control/staged_transfer_rates_v1/TIER_60_120_INTENT_1792901803619400203.json", "total_MiB_per_second": 120}`. `rate_transition/` retains qualification, normal lock-release and Driver-exit evidence, original Supervisor identity and cumulative budgets, and rate observations. Single-stream, SHA, staging, space/RAM, severe pressure and scientific identity requirements remain in force. Existing immutable bundle helpers retain their published versions.

Published restore-entry dependency audit: 115/115 scopes passed shell syntax, standalone module loading, co-located resource-module checks and pinned existing-controller V9 dependency loading. `RESTORE_IMPORT_DEPENDENCY_AUDIT.json` retains exact helper/resource hashes and external controller paths. This is not a native payload-restoration test, independent-host portability proof or an override of frozen helper resource checks.

The closure publication at GitHub commit `7125a94521428d6520451326127fc5749d3585c8` was independently fetched over HTTPS. All 5 selected final control/report files matched the local bytes and recorded SHA256 values. The following publication adds this readback receipt; its remote ref and receipt bytes are verified separately and persisted on genuine164.

No terminal HOLD remains. All 115 frozen scopes are committed.
