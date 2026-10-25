# Lane T2 archive report — DRAFT_IN_PROGRESS_NOT_GOAL_COMPLETION

Evidence snapshot: 2026-10-25T11:36:40.594649+08:00. Original queue SHA256 `718f30ec3bc8e5ece20df02cd472ebee17eac320f7b5a9e5b5e69841cc63cc04`.

The original 115 scopes remain unchanged. **36 committed, 0 current HOLD, 79 pending/in-progress**. Content archived in this execution: 144,728,004,881 bytes. T2 adds 22 assets / 33,941,033,794 bytes after the 14-asset takeover baseline.

| Group | Frozen | Committed | HOLD | Pending | Committed logical bytes |
|---|---:|---:|---:|---:|---:|
| TRACE | 51 | 35 | 0 | 16 | 144,727,828,792 |
| DTC_RAW | 63 | 1 | 0 | 62 | 176,089 |
| Q05_FIXED10000 | 1 | 0 | 0 | 1 | 0 |

The complete 115-row state table is `FROZEN115_FINAL_STATE_TABLE.csv`; new asset IDs and COMMITs are `NEW_T2_COMMITTED_ASSETS.csv`. `MEMBER_SHA_INDEX.csv.gz` and its lossless hash receipt retain every audited committed member SHA, numeric metadata and genuine164 path. `CONTENT_AND_RESTORE_CLOSURE.json` contains the COMMIT → manifest/ranges/tree and Source EOF proof checks. This review does not claim to have repeated all large payload hashes.

Prior 20 trace selectors: 20/20 metadata/COMMIT readbacks PASS; their 22,507,635,190 bytes are reused, never added to T2 new bytes. The already archived R13 package is 17,943,970,556 bytes and remains separately accounted. `TRACE51_COVERAGE.csv` identifies metadata supplements and reused input bodies; `.trace`, `.traceg`, full/fraction/trim and packages/expanded members are not equated.

`POLYBENCH_VARIANT_COVERAGE.csv` carries the 28 mandatory historical variants and four supplemental rows. Historical out-of-queue content or scientific HOLDs remain explicit and do not become new tasks or successful frozen-copy claims. `Q05_EXACT_SCOPE.json` binds fixed10000 run.log to SHA256 `06822c9fb9d2de0208eb51fb61c82f21150f509b8320662fd935efbac283843f`; natural R0 is a different object.

Complete native Target recovery is verified for 19 scopes of this frozen115 execution / 30,037,416 bytes. These are not necessarily new T2 restorations. Other restoration states: `{"FULL_NATIVE_RESTORE_NOT_PERFORMED_EXCEEDS_BOUND": 17, "RESTORE_VERIFIED_NATIVE_TARGET": 19}`. Full native restores above the qualified 240 MiB window were not performed. Their immutable raw trees, complete file SHA, original numeric metadata and bounded recovery helpers are retained; unrestricted full native recovery and scientific runtime acceptance are not claimed.

Historical exact retirement: 8,423 T-owned test-copy files, 4 approved Source kernel files, plus the one cold polybench package. Allocated bytes unlinked: Target test copies 527,740,928; Source kernel files 476,585,984; Source package 17,944,014,848. Independently observed operation-interval SSD free-space deltas: pool 18,936,295,424; Source unlink intervals 18,420,580,352. These are distinct measures and are not added to archive volume. T2 has not replayed any retirement or performed a new Source retirement.

Current shared SSD free: 23,695,081,472 bytes; Share/MD127 free: 36,581,097,472; genuine164 free: 48,599,070,375,936. Current free-space changes include other projects and are not attributed to this archiver.

All per-asset genuine164 bundle and recovery entries are in `CONTENT_AND_RESTORE_CLOSURE.json`; prior 20 reuse links are in the same file. The existing five-minute publication receipts remain `../checkpoint/recovery_20261025/PUBLICATION_RECEIPTS.jsonl`. Final process shutdown, partial-transaction accounting and GitHub remote readback must be independently closed before Goal completion.

Additional user-authorized 174-new cold compiler-copy retirement: 2,341 exact files; logical bytes 1,834,022,818; allocated file bytes unlinked 1,838,903,296; independently observed SSD free-space interval delta 1,816,342,528. Concurrent project writes prevent exclusive causal attribution of that interval delta. These measures are separate from each other, the historical releases and frozen115 archive bytes. Exact whitelist, SHA/metadata, COMMIT, INTENT/DONE, recovery test and restore entry are under `reclaim_174new/`. No old174 Source files were deleted by this additional retirement.

Recorded execution-admission error: the one 84,346,374-byte native restore test used a base-only SSD check instead of all declared reservations and the active-science gate. It passed SHA/metadata verification and its 84,353,024 allocated bytes were removed, without counting them as original-copy reclaim. `reclaim_174new/RESTORE_TEST_ADMISSION_DEVIATION.json` preserves the executed version and correction. Future test allocations now require the original full admission plus complete test-file capacity; directed checks include reservation shortfall and active-science I/O rejection. Content/receipt closure PASS does not erase this admission deviation.

The subsequent explicit user authorization in `ACTIVE_SCIENCE_IO_GATE_USER_AUTHORIZATION.json` changes only the active-science avg10 I/O check to monitor-only. It does not retroactively authorize the earlier restore-test admission error. Sustained severe host-I/O protection, SSD/RAM reservations, locks, rate/staging limits and scientific identity checks remain unchanged. `io_policy_transition/` retains directed qualification, the exact old/new supervisor identities and proof that the original deadline and cumulative counters were preserved during the single policy reload; the Publisher was not restarted.

Published restore-entry dependency audit: 35/35 scopes passed shell syntax, standalone module loading, co-located resource-module checks and pinned existing-controller V9 dependency loading. `RESTORE_IMPORT_DEPENDENCY_AUDIT.json` retains exact helper/resource hashes and external controller paths. This is not a native payload-restoration test, independent-host portability proof or an override of frozen helper resource checks.

No current classified terminal HOLD has been established in this snapshot. Remaining pending work is not counted as successful completion.

This is an in-progress report. Execution and bounded supervision continue; no user decision is currently requested by this draft.
