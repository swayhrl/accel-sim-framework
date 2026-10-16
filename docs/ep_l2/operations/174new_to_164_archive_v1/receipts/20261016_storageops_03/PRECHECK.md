# Authorized incremental execution

The explicit user approval resolves V2's archive-root gate, limited to `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02`. It authorizes creating subdirectories, tiny probes and receipt of verified historical data; original parent contents such as `git_packs_20260928` stay untouched. Shared staging is permitted after the successful cross-container probe, with batches no larger than 512 MiB.

REMOTE_164_AUDIT, SHARED_PROBE and SOURCE_FS_MAP document identity and route gates. The independent storage directory and source namespace were verified, not inferred from free-space similarity. Target verification closes rsync before reopening the file via SSHFS for full SHA256. No new 164 SSH authentication or fingerprint relaxation occurred.

Files are selected from a previously enumerated exact temporary-pack list, older than 14 days with no recorded fd/map/cmdline reference at the planning snapshot, single link, regular file, stable device/inode/size/mtime and PACK header. Age/name is only a candidate filter. Each source is hashed before transfer; file descriptors and identity are checked again, stage and target get complete hashes, and source identity is checked after copying. No candidate is declared disposable.

Source fsck --full --no-dangling is timeout-limited and low priority; its exit 124 means full health remains unverified. It did not write lost-found, repack, prune, or gc. Index-pack runs only on task-owned stage duplicates under a 35-second cap; incomplete pack errors and unknown object uniqueness are recorded. Full byte-for-byte backup does not itself authorize deletion.

Only one rsync leg runs at a time, nice 19 / ionice idle / 30 MiB/s, using -aH --no-owner --no-group --partial --fsync. Dry-runs precede both actual legs. No --delete, --remove-source-files, inplace overwrite of source, wildcard deletion, or source-tree write occurs. Exact task-owned stage paths are unlinked only after all completed-batch hashes match and source remains stable. No raw historical dataset is hashed globally.

Six-lane CPU/memory/simulation limits and 48 GiB floor remain in force. Temporary build-directory sizing is bounded to specific historical candidate names; unique/reproducible/inactive safety has not been established for those directories, so no source cleanup is attempted there.
