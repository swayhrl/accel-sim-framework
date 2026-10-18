# Storage-Ops V9: crash and authority controls

This is a SMALL reusable protocol on top of already-verified V8 mechanisms, not a new migration platform. V8 already had SHA-pinned source identities, complete164 restored-tree checks, bounded sole-bridge batches, native restore samples, exact per-file compare-and-unlink, and df receipts. Preserve these. V9 closes four specific gaps: crash/restart reconciliation, strict source/target transaction identity, robust sidecar metadata+genuine164 path typing, and independent Ops/Lane5 completion states.

## 1. Immutable transaction/state machine

txid = SHA256(source filesystem identity + exact canonical source root + immutable selector manifest SHA256 + source frozen commit + genuine164 destination root). Do not use project name/date alone. Only an explicitly approved selector may enter RELEASE_ELIGIBLE. Records are immutable after publication; status transition must reference old receipt sha.

DISCOVERED -> SOURCE_FROZEN -> COPY_READY -> ARCHIVE_STAGED -> ARCHIVE_VERIFIED -> RESTORE_VERIFIED -> RELEASE_ELIGIBLE -> SOURCE_RELEASED.

Failed steps = HOLD(reason, previous_receipt SHA), never silently PASS. Lane5 remeasurement is a DIFFERENT chain (NOT a prerequisite to archive task DONE). Source may close as ARCHIVED_SOURCE_KEEP for new C2P/M2D data without any unlink; target may close DONE after verified archival and reporting.

Manifest must specify normalized source relative paths (no leading /, dotdot, symlink traversal), UID/GID/mode/mtime/ctime and dev/inode/nlink/size/st_blocks*512, file type, full SHA256, source commit, current readers, exact target and archive identity; separately retain directory metadata and symlink/hardlink policy. Current SSHFS st_ino/uid projection is not source native metadata proof. Numeric original metadata stays in sidecar and is verified on a real native restore target.

## 2. Copy, verify and resume

At most one target stream <=30MiB/s and bridge staging <=256MiB under current Share headroom. New genuine164 destination must be ABSENT. Chunk a single larger file by byte offset and per-chunk SHA; write an isolated .partial transaction and durable offsets; close/reopen and hash actual bytes before publishing a chunk receipt. On resume use pinned txid+manifest and re-hash existing chunks, no overwrite/truncate of final verified archive. Atomic finalize only after full-file+full-manifest hash checks and same-filesystem no-overwrite finalization. If rename without replacement cannot be guaranteed on the actual filesystem, stop and use a proven exclusive-create strategy, never replace.

Never delete a source file just because its bytes were copied. Actual restoration must use a new absent path, independent SHA and numeric metadata comparison (UID/GID/mode/mtime, directory metadata). ctime cannot be restored; preserve it as provenance only. No unsafe tar path extraction or direct writes to source directory.

## 3. Source release: crash recovery and no double-unlink

Release is OLD174-only. Exact prior user permission, current original full SHA+fstat/lstat and parent device/inode, no symlink/hardlink surprise, live FD/PID/cwd/argv/registry+scheduled reader exclusion, genuine164+restore proofs and remaining48GiB/40GiB/64GiB floors required. If any identity changes during hashing, STOP.

Before each exact unlink, append and fsync INTENT(txid,path,source_identity,source_sha,target_proof). Reopen original with O_NOFOLLOW / directory FD, verify source inode/nlink and hash; perform only exact path unlink. fsync parent directory if supported, then append+fsync DONE. Interruption leaves INTENT and/or DONE as evidence. Resume logic does not blindly issue unlink again: inspect actual path, prior journal state and target proof; missing file with incomplete journal is UNCERTAIN requiring manual readback/approval if proof cannot resolve it. Never infer safety from mtime alone or use rm -rf. The V8 R2 production script is tested for its own exact full-group gate, but its partially interrupted release is NOT automatically resume-safe. Use it unchanged when safe; treat a partial V8 attempt as HOLD until separately reconciled. New V9 source release implementation stays synthetic-fixture-only until independently qualified.

Report source df immediately before/after each batch and long-window endpoint separately; time-varying external writes can make these values differ. Never add Share/164 archive bytes to source free-space gain. Hardlinks/shared extents may prevent allocated counts from corresponding to net df.

## 4. Required little tests, not huge system build

Use synthetic local fixtures, original scientific assets never touched:
- Interrupted upload before/after durable chunk record, duplicate resume and mismatched txid: exact digest and no extra destination.
- Corrupt target chunk/manifest/source inode/mtime/ctime, wrong mount or SSHFS projection, symlink, '..', and already-existing destination: fail before archive acceptance.
- Crash after release INTENT, after unlink but before DONE, after DONE: source reconcile reports accurate state without second blind delete.
- Active reader FD/PID/registry; withheld exact user permission; current SHA differs; insufficient workspace/Share/RAM; bridge batch >256MiB: HOLD.
- Native restore to missing destination matches byte+numeric metadata; populated destination refuses overwrite.
- Simulated concurrent writer changes df: batch gain and endpoint change not conflated.

Minimum deliverables: V9_TRANSACTION_SCHEMA.json, V9_ARCHIVE_RECEIPT.json, V9_RESTORE_RECEIPT.json, V9_FAULT_INJECTION_TESTS.json, SOURCE_TO_164_INDEX_V9.json, V9_OPERATOR_RECOVERY.md and an exact per-file approval proposal. Do not write credentials or raw science into Git. Make tooling idempotent for verified states, not for unauthorized deletions. No resident daemon, no mass rehash of unrelated projects, no Git gc/prune, no change to central Lane registry.
