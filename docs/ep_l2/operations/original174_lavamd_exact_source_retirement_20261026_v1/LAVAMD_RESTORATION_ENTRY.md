# lavaMD exact restoration entry

Status for this Goal: **Source retained; restoration capacity HOLD occurred before INTENT.**

The genuine164 recovery bundle is:

`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets/TRACE_90174dcf58988a5d`

The dedicated recovery program is stored beside its evidence on genuine164:

`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/control/lavamd_exact_source_retirement_v1/LAVAMD_RESTORE_TO_OLD174.py`

Run it on `hrl-174-new`, where `/root/share/mnt164` is the verified SSHFS mount for `admin-wcx@10.208.130.164:/home/shared`:

```bash
python3 -B /root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/control/lavamd_exact_source_retirement_v1/LAVAMD_RESTORE_TO_OLD174.py --self-check
python3 -B /root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/control/lavamd_exact_source_retirement_v1/LAVAMD_RESTORE_TO_OLD174.py --preflight
python3 -B /root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/control/lavamd_exact_source_retirement_v1/LAVAMD_RESTORE_TO_OLD174.py --execute
```

`--execute` is appropriate only after a separately admitted retirement has removed the trace and a fresh `--preflight` reports `PREFLIGHT_PASS`. It currently fails closed because the original trace is present and the resource contract cannot admit a full restore.

The program pins both server mount namespaces, the genuine164 SSHFS identity, Asset ID, Manifest and COMMIT hashes. It accepts only `kernel-1.traceg`, streams through 1 MiB buffers at 15 MiB/s without a full new174 staging copy, creates an exclusive temporary destination, fsyncs it, closes and fully rehashes it, restores numeric uid/gid/mode/mtime, and publishes through a no-overwrite hard link. Ctime is not restorable.

The four control files are verified and never overwritten. Unsafe relative paths, unknown members, active readers/writers, temporary-file collisions, insufficient capacity and any content mismatch fail closed.

The complete 20.776 GB native restore was not executed. The Source remains complete, so restoration is not currently needed. The old174 `/root/share/mnt164` MD127 shadow is never accepted as genuine164.
