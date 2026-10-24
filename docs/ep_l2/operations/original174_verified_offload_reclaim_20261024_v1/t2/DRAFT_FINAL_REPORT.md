# Lane T2 archive report — DRAFT_IN_PROGRESS_NOT_GOAL_COMPLETION

Evidence snapshot: 2026-10-25T03:18:16.834512+08:00. Original queue SHA256 `718f30ec3bc8e5ece20df02cd472ebee17eac320f7b5a9e5b5e69841cc63cc04`.

The original 115 scopes remain unchanged. **34 committed, 1 current HOLD, 80 pending/in-progress**. Content archived in this execution: 115,095,478,300 bytes. T2 adds 20 assets / 4,308,507,213 bytes after the 14-asset takeover baseline.

| Group | Frozen | Committed | HOLD | Pending | Committed logical bytes |
|---|---:|---:|---:|---:|---:|
| TRACE | 51 | 33 | 1 | 17 | 115,095,302,211 |
| DTC_RAW | 63 | 1 | 0 | 62 | 176,089 |
| Q05_FIXED10000 | 1 | 0 | 0 | 1 | 0 |

The complete 115-row state table is `FROZEN115_FINAL_STATE_TABLE.csv`; new asset IDs and COMMITs are `NEW_T2_COMMITTED_ASSETS.csv`. `MEMBER_SHA_INDEX.csv.gz` and its lossless hash receipt retain every audited committed member SHA, numeric metadata and genuine164 path. `CONTENT_AND_RESTORE_CLOSURE.json` contains the COMMIT → manifest/ranges/tree and Source EOF proof checks. This review does not claim to have repeated all large payload hashes.

Prior 20 trace selectors: 20/20 metadata/COMMIT readbacks PASS; their 22,507,635,190 bytes are reused, never added to T2 new bytes. The already archived R13 package is 17,943,970,556 bytes and remains separately accounted. `TRACE51_COVERAGE.csv` identifies metadata supplements and reused input bodies; `.trace`, `.traceg`, full/fraction/trim and packages/expanded members are not equated.

`POLYBENCH_VARIANT_COVERAGE.csv` carries the 28 mandatory historical variants and four supplemental rows. Historical out-of-queue content or scientific HOLDs remain explicit and do not become new tasks or successful frozen-copy claims. `Q05_EXACT_SCOPE.json` binds fixed10000 run.log to SHA256 `06822c9fb9d2de0208eb51fb61c82f21150f509b8320662fd935efbac283843f`; natural R0 is a different object.

Complete native Target recovery is verified for 19 scopes of this frozen115 execution / 30,037,416 bytes. These are not necessarily new T2 restorations. Other restoration states: `{"FULL_NATIVE_RESTORE_NOT_PERFORMED_EXCEEDS_BOUND": 15, "RESTORE_VERIFIED_NATIVE_TARGET": 19}`. Full native restores above the qualified 240 MiB window were not performed. Their immutable raw trees, complete file SHA, original numeric metadata and bounded recovery helpers are retained; unrestricted full native recovery and scientific runtime acceptance are not claimed.

Historical exact retirement: 8,423 T-owned test-copy files, 4 approved Source kernel files, plus the one cold polybench package. Allocated bytes unlinked: Target test copies 527,740,928; Source kernel files 476,585,984; Source package 17,944,014,848. Independently observed operation-interval SSD free-space deltas: pool 18,936,295,424; Source unlink intervals 18,420,580,352. These are distinct measures and are not added to archive volume. T2 has not replayed any retirement or performed a new Source retirement.

Current shared SSD free: 20,543,815,680 bytes; Share/MD127 free: 36,582,469,632; genuine164 free: 49,305,340,182,528. Current free-space changes include other projects and are not attributed to this archiver.

All per-asset genuine164 bundle and recovery entries are in `CONTENT_AND_RESTORE_CLOSURE.json`; prior 20 reuse links are in the same file. The existing five-minute publication receipts remain `../checkpoint/recovery_20261025/PUBLICATION_RECEIPTS.jsonl`. Final process shutdown, partial-transaction accounting and GitHub remote readback must be independently closed before Goal completion.

Current explicit HOLDs:
- `TRACE_7a2ceb3a0f9b32b5`: RESOURCE — RESOURCE_HOLD_SSD_ALL_DECLARED_RESERVATIONS

This is an in-progress report. Execution and bounded supervision continue; no user decision is currently requested by this draft.
