# Exact original-path recovery

The map preserves original174 paths, SHA256, sizes, uid/gid0:0, mode0600 and each original nanosecond mtime. Historical inode/ctime are provenance only. Retain the126 control/manifest files and their directories. Model originals remain ACTIVE_KEEP.

Default commands only print plans:

```bash
bash ../RESTORE.sh --package P3
bash ../RESTORE.sh --package P2
```

The present original174 same-name `/root/share/mnt164` is local ext4, so direct mount mode rejects it. The existing true164 SSHFS is in174-new namespace `mnt:[4026535153]`, with source `admin-wcx@10.208.130.164:/home/shared`. The commonShare route is independently acknowledged in `TARGET_ROUTE_ACK.json`; both namespaces see the same430-byte source probe, dev2431/inode30408706, with matching SHA and nonce.

For a future explicit restore, use one foreground producer and one foreground consumer. No daemon, task-config change, new SSH credential, full Share staging copy or native164 shell is needed. First print the exact producer command:

```bash
bash ../RESTORE.sh --package P3 --shared-pipe /root/share/c16_storage_audit_restore_20261020_v1/restore-P3.fifo --print-producer
```

On original174, start the bounded consumer using the actual absolute script path:

```bash
timeout 7200 bash /workspace/worktrees/framework-c16-storage-audit-20261020-v1/docs/ep_l2/operations/c16_storage_audit_20261020/RESTORE.sh --package P3 --shared-pipe /root/share/c16_storage_audit_restore_20261020_v1/restore-P3.fifo --execute
```

After `FIFO_READY`, execute the command printed after `RUN_ON_174NEW:` in the existing174-new command environment. It verifies174-new hostname/namespace and true164 SSHFS identity before emitting only the selected exact files. The producer blocks on the same FIFO; no disk payload is staged inShare. Repeat withP2 only ifP2 recovery is needed. An alternate existing genuine164 mount on original174 can use `--mount` instead; the same identity check applies.

The consumer refuses any existing destination, redirected parent, wrong archive member/type/size or wrong namespace. It verifies the streamed SHA, verifies the newly written file independently, restores numeric ownership/permissions/mtime, then publishes without overwrite. Source file content and attributes on164 are never changed. The latest userIO exception allows contention above10; physical lease, capacity and other data checks remain. The script retains the existing48GiB post-write free-space reserve; actual capacity must be admitted when future recovery is requested. No full-weight recovery or large native proof tree was executed during retirement. Tiny isolated tests cover both transport modes, exact bytes/attributes and overwrite refusal; the cross-namespace route probe covers real existing bridge visibility.

On a failed restore, preserve the uniquely named `.restore-<pid>.partial` for review. Existing destinations are never overwritten on retry. Publish package readiness only after its complete selected file set succeeds. Data-space admission at future recovery time remains a resource check, independent of permanent164 content retention.
