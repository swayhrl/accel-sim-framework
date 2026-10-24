# AWMA / C16 evidence gap closure

## Six alleged digest mismatches: resolved, no corrupt-data inference

All six exact `RUN_MANIFEST.json` files now hash to the catalog-expected SHA256. The previous audit's `catalog_crosscheck.py` tested only files at most131,072B; these six were134,010–1,780,506B and were **skipped**, not hash mismatches. Four were only slightly above the limit. The exact Root/namespace remains174-new `mnt:[4026535153]` → `admin-wcx@10.208.130.164:/home/shared` SSHFS. Original174's same-named MD127 shadow was never used.

|Run|Manifest bytes|Current exact SHA256|Artifacts stat-checked|Missing/size mismatches|
|---|---:|---|---:|---:|
|C16R_qwen25-7b-raw_s2-text_decode_nvbit-warp-mref-shard_v10-semantic-downproj-r2_20260916T005000Z_cc10cc10cc10|134010|6536b6d094b968d7eeaa86a0cc7dea9f26487477a8484a4f869faf0a4c42f47c|732|0|
|C16R_olmoe-1b-7b-0125-instruct_s2-t2048-d32_decode32_nvbit1771-c16warp1_expert58-down-proj-actual-a_20260922T100810Z_fc0f3cf67edf|360757|8f3e5e338166a2ebc4da6b9a55986980d31227f3d0e383ca5a1f24d0d924f31b|1958|0|
|C16R_qwen3-30b-a3b_s2-text_decode_nvbit-warp-mref-shard_s2-dec3-natural-expert21-down_20260917T034400Z_e210c0de5678|177362|259b34c75ed8adbd8132d56e23a41fc02da97338f8510027f7da77ccb52dcd83|981|0|
|C16R_qwen2p5-7b-instruct-awq_s2-text-d1-d3_decode3_nvbit1771-sim-native-full-sass_bounded-context_20260925T120107Z_2b41b26fdb03|1780506|db3bdbb0295a47a6aa4644508ea1895779c987f2f77cd96f184c67b8a10ab389|9062|0|
|C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v14-layer0-downproj_20260916T020000Z_dd14dd14dd14|133436|2784c8c23fe4e2173a4d5dd3d8595d4fadd8fc66fb1ffa50b883052ece6c540d|732|0|
|C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v23r1-moe-e4-down_20260917T024000Z_b23b23b23b23|134005|d98b4a077afe9e7f2ce32479484e9c1148548b1ef1802c9b002dd70250b7b638|735|0|

Read 2,720,076 small metadata bytes at server side. All14,200 declared artifacts currently exist as regular files at the declared size; each manifest identity is stable before/after. The90 prior exact manifest proofs remain reused. This closes96/96 **manifest** digest bindings, not a fresh122,592,246,070B raw payload rehash or full independent native recovery. LOCAL_CLOSE_RECEIPT file counts/manifest SHA bind the same six runs. Prior TRANSFER_ACKED is historical transfer evidence; raw payload full-current integrity/recovery qualifiers remain explicit.

No checksum algorithm or scientific identity was changed. The old audit is preserved as history; the corrected reason is `PREVIOUS_READ_BOUND_EXCLUSION`, not a new digest convention, detected corruption or repair upload.

## Q05: separate two scientific identities

`SIM_EVIDENCE_c8b4175d33f8bed7def2984489eadbdbcdfaffbfcb6a7daef33c8beb18e80959` / `SIM_RUN_92a553b0d69a9f41c5e20a8650366c53f7fed31c29c7462947d3af03c6f136f1` is **FORMAL_FIXED_WINDOW10000**, per6415d3f1 owner `SIM_EVIDENCE_RECORD.json` and `SIM_RUN_RECORD.json`. It is not the885,681-cycle natural completion. The old storage catalog's natural-completion description mixed these scopes; no accepted scientific result is altered here.

Its exact replay1 raw is still present on174-new at:

`/root/workspace/accel-sim-framework-awma-first-current-model-replay-174new-v1/docs/vm_tlb/review_packs/AWMA_FIRST_CURRENT_MODEL_BASELINE_SIM_174NEW_V1/raw/replay_1/run.log`

223,499B, current full SHA `06822c9fb9d2de0208eb51fb61c82f21150f509b8320662fd935efbac283843f` equals accepted owner evidence. Exact immutable Git recovery entry exists at6415d3f1's same review-pack path. Server direct public-Git DNS was unavailable; the already-local owner worktree resolved this ordinary read problem without new access or data upload. Its exact164 raw locator remains HOLD; don't substitute the separate natural log. Replay2 has its own run/normalization evidence and is not required to equal replay1 raw hash.

The **separate natural R0** has existing owner RAW_DATA_INDEX and RUN_RECEIPTS locator:

`/home/shared/huangrulin/awma_q05_full_kernel_translation_analysis_v1/r0_natural_completion_interrupted_transport/run.log`

166,223B, current full SHA `cc11bdb051ce3b8d4207bba8e9587adbd2dda65b13421f7699986652631d83af`. Existing885,681 cycles /368,696,302 instructions /224 CTA owner scope was checked. A new ABSENT174-new native ext4 sample directory contains an independently closed/reopened byte-identical copy: `/root/data/original174_trace_evidence_closure_20261024_v1/q05_natural_r0_sample/run.log`. Status is **NATIVE_TARGET_CONTENT_SAMPLE_RESTORE_VERIFIED**, not native164 restoration or a complete project recovery. Original native numeric metadata is unavailable in this locator chain; SSHFS projected owner/mode is not substituted. Resource gate7GiB+other current reservations+2MiB and MemAvailable≥64GiB passed. Actual own native write166,223B;0Share payload writes; no receiver/controller was installed or taken over. Sample remains for audit, no Source cleanup.

V4 matrix partial runs retain PARTIAL; producer canary/109 ACK gaps retain their original scope. No new109/GPU task was started.

## Previously unexpanded legacy raw authority: existing164 content located

Canonical root: `/home/shared/huangrulin/c16_ai_workload/provenance/historical_snapshots/old174_c12_c15_simulation/`.

Existing owner46de0c35e2c26fdabd9fc691370bedf0cc5974f5 supplies NODE164_ARCHIVE_MANIFEST/RECEIPTS, exact PRIVATE_EXPORT_READY and private tree/full-file SHA closure. Current immutable READY SHA `32dff6170ccf6172c0ebac2c8af0a0131c962d1dabe7349993f510742e046c0d` and export-manifest SHA `62564e06565be02ca63bf6fc3ce36c2df2a3adc2d23c619d73885c448bc1b6d4` match.494/494 regular-file stat/size locators match the historical complete destination SHA list. Five groups preserve C12 FORMAL, C13 DIAGNOSTIC, C14 microdiagnostic, C3 provenance and PRE_FIX status separately.

Actual regular-file bytes **5,330,959,289**, whereas old source/export tree logical count5,338,159,166B includes additional namespace/link/directory accounting. Do not call15,906 or14,286 trace-link entries raw files or count them as new independent payload. Configs, raw stdout and manifest identities are preserved, not just published performance numbers. No5GB blanket reread or complete native recovery was done.

C3/M4I input-trace symlinks and historical runtime qualifications remain dependencies; a regular raw-log archive does not establish whole scientific replay. The same owner's MIGRATION_SUMMARY explicitly left M4A's shared source archive unduplicated. M4A MD127 input in Top30 therefore cannot inherit a164 copy claim. Existing shared M4C/M4B/EP-streaming-reuse copy receipts are retained as diagnostic/UNKNOWN evidence, not promoted to complete C12 F0 raw.

## C16 six models

Historical true164 six full SHA proof `ab95e0aa46c73f6297315ecbbae09de10b09ce87` remains6/6; no model content reread. Current Source canonical six and true164 paths/sizes/mtime were checked metadata-only. RAW revision `a09a35458c702b33eeacc393d103063234e8bc28`, AWQ revision `b25037543e9394b818fdfca67ab2a00ecc7dd641`. Original canonical models remain ACTIVE_KEEP. Already-retired P2/P3 outbound paths are historical, not new reclaim.

SSHFS inode projection changes do not establish content changes. Source original metadata and exact two outbound layouts remain in baseline's SIX_ROW_TRUE164_AUTHORITY_PROOF.tsv / CURRENT_RESTORE_INDEX.tsv; native metadata cannot be read off SSHFS projections. Full large native model restore was not performed. No retirement, model transfer,109 operation, supervisor edit or C16 scientific qualification change occurred.

## TLS

P9 original txid remains `574747b05622a2a0f3ef1a58c11044ee724e5e585d0edd5f0fc32937eda12e6b`; latest Target branch09a6b4e4d closes B0028/130ranges/2,505,862,788B.391,334,023B remain formally missing and full141-file/4-directory restoration is unclosed. All25 planned group COMMIT locators were read without mutation; no complete group COMMIT was found at the frozen proposed transaction roots. Planned paths and reservations are not archives. Old B0010/B0029 requests, locks, payloads and controllers were not resumed or cleaned.
