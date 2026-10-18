# Storage-Ops V9: further cold migration and durable recovery

**Execution contract, 2026-10-18.** Two NEW bounded tasks for the existing OLD174 (2233) and 174-new (2239) Storage-Ops Codex windows. Completed R13/V8 Goals remain closed. This commit does not execute any filesystem operation and does not grant wider deletion permission. Lane1 MQ2 and Lane5 Parallel experiments have resource priority.

## 0. Pinned evidence; never double-count

- Source OLD174 repo swayhrl/gpu-l2-cache-verilog, branch hrl/ops-174-source-audit-exec-v1, last verified HEAD b7994431e6b052bccd7571802a6c1b60ec1fadfc. V8 source receipts under docs/ep_l2/operations/174new_to_164_archive_v1/source_receipts/20261018_fast_reclaim_v8/.
- Target 174-new repo swayhrl/accel-sim-framework, branch hrl/ops-174new-164-archive-exec-v1, last verified HEAD 7ed8a3d6f0af7a081d3a7a8d5755a448b7e312ad. V8 target receipt root docs/ep_l2/operations/174new_to_164_archive_v1/receipts/20261018_storageops_v8_target_01/.
- Historical V8 isolated release-by-release real OLD174 workspace gains summed 9,446,871,040B (8.80GiB); its across-window endpoint free change was 8,450,060,288B (7.87GiB). Earlier R13 gained another 66,329,825,280B. All historical releases are CLOSED and must not be copied, rerun or counted as new.
- Lane5 post-V8 read-only measurement at Framework commit 413d7300821f2d623ce8f638b866dd85fc6d729d was workspace device156 free 60,287,987,712B (56.14756GiB), Share device2431 free 41.30424GiB, adequate memory. These were point-in-time values, not live authorization. Old174 and Lane5 are in the same source filesystem; 174-new and OLD174 have different mount namespaces.
- Real 164 archive was separately verified by 174-new as admin-wcx@10.208.130.164:/home/shared mounted at /root/share/mnt164. OLD174 has a misleading similarly named directory that is NOT the genuine164 SSHFS mount. Recheck genuine164 mount identity and close/reopen SHA rather than infer from its pathname.
- Existing guardrails unchanged: physical OLD174 workspace >=48GiB, Share>=40GiB, available RAM>=64GiB; real aggregate result budget20GiB, Lane2 own12GiB, central sim/CPU/RAM quotas. No Lane budget, deadlines, source config, binary, registry, process or run-key changes. No 2nd transfer stream, active Lane process signal or persistent watcher.

## 1. Priority P0: remaining R2 191 historical .vvp, exact previously approved selector

R2 has a user CONDITIONAL approval already explicitly recorded in OLD174 V8 file VVP_USER_CONDITIONAL_APPROVAL_V8.json, applying to R1(197), R1R(127), R2(191). R1/R1R already released; R2 remains SOURCE_KEEP at the last V8 snapshot. The authorization is NOT for any other R2 build file.

- Root: /workspace/repos/gpu-l2-cache-verilog-v3r2-clean/build. Exact source selector R2_VVP_EXACT_APPROVAL_V8.tsv, SHA256 b957dae3fe14560b268319301ee22441094a5daa8355f929e648553f17debaad, allocated upper bound 2,690,052,096B (~2.505GiB). Combined exact V8 selector SHA 2592a8cac6536b12b3250e9c7db4f374b52e530367a6c82830a9488b5f82d0c7.
- 174-new V8 already proved all R2 191 current SHA values on genuine164 primary archive AND an independently materialized restored tree, including numeric source metadata. Receipt R2_EXACT_SELECTOR_RESTORE_VERIFIED_V8.json in V8 target root, status DEST_VERIFIED_AND_RESTORE_READY. No new upload is needed to prove this same object exists.
- OLD174 V8 has ALREADY executed one native R2 reverse-restore sample with different device156 inode, full SHA and UID/GID/mode/mtime PASS (R2_NATIVE_SAMPLE_RECHECK_V8.json, VVP_NATIVE_DRILL_B001_SOURCE_ACK_V8.json). It also has R2_NO_OVERWRITE_PROCEDURE_RECHECK_V8.json covering a six-batch bounded full191 no-overwrite recovery plan. Do not claim it restored all191 natively on OLD174 or redo the old B001 sample without need.
- Target independently refreshes genuine164 identity and exact R2 archive/restore digest/readback. Source rechecks ALL current191 original full-content SHA and dev/inode/nlink/size/allocated/UID/GID/mode/mtime_ns/ctime_ns, present process FD/cwd/argv and run registry/known scheduled readers, actual protection floors, and that all nonselected R2 build artifacts remain KEEP. Check whether the old conditional authorization and immutable manifest still exactly match current content. Drift or uncertain future consumer -> HOLD.
- With fresh target V8 receipt/bridge/Git SHA and matching old source native/procedure proofs, generate the exact R2 release gate accepted by OLD174's EXISTING release_v8_vvp_group.py (inspect its validate_gate contract). Run exact dry-run and --group R2 --check-gate with the gate file. ONLY when all tests pass, source owner may run its already qualified --group R2 --release once, preserving per-file source journal. If partially interrupted, DO NOT blindly rerun or manually unlink; reconcile first, see protocol file. Record released exact191 paths, unchanged nonselected siblings and actual before/after OLD174 df -B1 -P /workspace. Send only a signed result/space notice to Lane5; Ops does not grant experiments.

## 2. Priority P1: archive three C2P/M2D build roots; NO SOURCE DELETION

OLD174 V8 bounded census listed three candidates on source device156:
- /tmp/c2p-gpgpu-pre-attribution-20260822/build (424,570,880 allocated B historically)
- /tmp/c2p-gpgpu-build-20260821/build (424,419,328 allocated B historically)
- /tmp/m2d-core-g21/build (410,275,840 allocated B historically)
Combined historical upper-bound allocated 1,259,266,048 B (~1.173GiB), not a promise of actual release. V8 target SOURCE_TO_164_RESTORE_INDEX_V8_R3 explicitly classified C2P/M2D as NO_EXACT_TARGET_MANIFEST_ESTABLISHED. Do not fabricate archive coverage.

OLD174 makes a fresh path-local exact file+directory manifest, checks current ownership/active/future consumers and source SHA, types, metadata, hardlinks and project-specific nonreproducible products. Only if safe produce COPY_READY. 174-new transfers using one low-pressure bounded stream to new ABSENT genuine164 directory; verify actual full-file SHA, numeric metadata sidecar, no-overwrite fresh-root restoration and current target bytes. Source originals are SOURCE_KEEP regardless of archival success. Publish next-user-approval exact per-file manifest (possibly less than three full directories), allocated space and restore command. Do not treat the present user request for migration as blanket original deletion authority.

P2 read-only: rank up to 3 additional precisely identified >=0.5GiB cold-scratch candidates from existing indices, with no whole-workspace scan. R1/R1R/R2 remaining builds contain potentially unique verification/raw/signoff data, so KEEP. Historical Git/tmp_pack offload had a noncompliant route; do NOT copy, delete, gc, prune, overwrite or attempt to normalize any Git objects in V9. Legacy PolyBench/M5 already released items must not reappear as candidates.

## 3. OLD174 task OPS_OLD174_V9_R2_AND_COLD_SOURCE

Use the ORIGINAL OLD174 Ops Codex window and existing source Ops branch in an isolated V9 review pack; this is a NEW task, not restart of V8/R13. Source is the SOLE release owner.

- Within15min: re-fetch latest Git heads and all old V8 receipts, measure actual source namespace/dev/statvfs for /workspace and Share and active Lane1/Lane5 process+lease, check R2 manifest source and script. First report current free bytes and source scan viability.
- Within45min: secure fresh target R2 receipt/Git+bridge hash; establish R2 exact release gate and run read-only/dry-run/full191 validation with affected negative tests. If ALL gates PASS, perform only source-owned exact191 R2 release, under current central safety checks; log before/after per-file and per-phase df. If any issue or active consumer, STOP R2 and publish reason, do not work around old SHA or inode mismatch.
- In parallel with target preparation, write P1 C2P/M2D full exact COPY_READY inventory or precise failure reasons, preserving originals. Rank up to3 P2 cold candidates for future consent.
- Send Lane5 a single immutable measured-space notice if source bytes freed. Do not wait indefinitely for Lane5 independent admission; that is another owner. Source V9 Goal can finish its own data scope.
- Checkpoint at30min, source phase cap3hours, only1CPU/low IO with central leases and no simulator/build interruption. On resource conflict, deliver read-only receipts and STOP safely. Nonforce push only own original source Ops branch and hash-verify remote files.

## 4. 174-new task OPS_174NEW_V9_ARCHIVE_AND_RESTORE_PROTOCOL

Use ORIGINAL 174-new Ops Codex window and original target Ops branch, isolated V9 review pack. Target is SOLE genuine164 archiver/restorer. Target NEVER releases an OLD174 file.

- Within15min: prove fresh genuine164 mount/source/namespace/capacity + small write/close/reopen/hash probe, remove ONLY its new probe. Read full R2 V8 archive/restore receipt and source R2 exact consent; compare full191 current archive+restored SHA/metadata against immutable selector in bounded low-priority IO. Reuse old archive instead of retransferring anything. Deliver revalidated R2 DEST_VERIFIED/RESTORE_READY ack with Git+bridge exact hash to source.
- Upon OLD174 COPY_READY, archive P1 exact roots only under new empty transaction path. At most one bridge batch <=256MiB and <=30MiB/s; if larger file use bounded verified chunks without unlimited staging. Confirm target actual file SHA after close/reopen and an independent representative complete selection native metadata restore; if only sidecar metadata available, label metadata UNVERIFIED and block release approval (source retains files regardless).
- Add minimal reusable migration/checkpoint/resume and fault-injection validation described in STORAGE_OPS_V9_TRANSACTION_AND_RECOVERY_PROTOCOL.md. Reuse proven V8 scripts: no general migration daemon or speculative whole-root refactor. New release executor remains fixture-only unless user explicitly approves that specific real selector.
- Finish with V9_R2_TARGET_READBACK, V9_COLD_ARCHIVE_AND_RESTORE_INDEX, V9_PROTOCOL_TEST_RECEIPT, and per-candidate missing gates. Archive data Goal may close after its own proofs even if Lane5 resource confirmation is pending (not a failure of archival work).
- First Git+bridge ack <=30min; complete within3hours if resources permit; 1CPU/low IO, single stream, Share40GiB and other central floors unchanged. Never duplicate earlier36pack/35PolyBench transfer. Push only own target Ops branch and verify remote commit/receipt bytes.

## 5. Coordination and STOP contracts

Read companion STORAGE_OPS_V9_TRANSACTION_AND_RECOVERY_PROTOCOL.md. Existing OLD174 release_v8_vvp_group.py is fail-closed and does not automatically resume after mid-release failure; no new unqualified script may touch real R2. A source crash after partial unlink requires exact source-journal reconciliation with no blind retry or extra unlink. If current source no longer matches V8 group authority, request new exact user approval, do NOT silently adjust the approved manifest.

Two windows may inventory/verify in parallel; only one target data stream and source-only exact release. All 164 transport receipts and independent Old174 source release receipts have distinct immutable status/provenance. Preservation of other projects, backups, trace assets and Git objects is mandatory. C2P/M2D release remains an explicit future approval decision. No extra Lane1/Lane5/Lane2/3 Goal is created by this migration.
