# Storage-Ops revision 03: COPY_IN_PROGRESS_SOURCE_KEPT

Snapshot: 2026-10-16T13:09:01.083888+00:00. Continues V2 on the original execution branch; revisions 01 and 02 remain intact. The user explicitly authorized the exact archive root `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02` and the dedicated shared staging route.

- Target probe: write, fsync, close/reopen SHA256 and deletion PASS; no probe residuals.
- Shared `/root/share` probe: both directions match content and inode; probe deleted and absence confirmed from old174.
- Source is the exact Lane5 namespace via trusted alias `hrl`; SSHFS is used only through `hrl-174-new`.
- Completed **4/29** batches, **1420165168 bytes (1.323 GiB)**. Source, stage and reopened SSHFS archive SHA256 match for every completed file, and source identities remain stable.
- One sequential transfer at a time, rsync 30 MiB/s, each batch <=512 MiB. Only each task-owned, verified stage copy is removed after archival; source files remain KEEP.
- **Actual Lane5 bytes released: 0.** Latest source available bytes 41711398912 (38.847 GiB); 48 GiB floor remains unchanged. Stage cleanup occurs on another filesystem and is not counted as recovery.
- Full Git fsck timed out after 90 seconds. Copied partial packs are investigated with index-pack only on the stage duplicate; early EOF does not prove no unique recoverable data. No source pack deletion is authorized or executed.
- Scientific originals/traces/logs/review packs/unique binaries and all six lane worktrees/registries remain untouched. No other process was stopped.

Verification is **SSHFS_READBACK_VERIFIED**, not SERVER_SIDE_NATIVE_VERIFIED. Source UID/GID/mode/mtime/inode are preserved in metadata; FUSE displays synthetic/remote ownership and permissions, so native server permissions are not claimed preserved.

Next: continue the already admitted bounded backup batches and publish the completed list before any deletion approval request.
