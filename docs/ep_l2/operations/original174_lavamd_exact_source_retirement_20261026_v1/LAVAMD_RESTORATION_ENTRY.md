# lavaMD exact restoration entry

Status for this Goal: **Source trace retired after explicit user capacity-gate override.**

The genuine164 recovery bundle is:

`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets/TRACE_90174dcf58988a5d`

The dedicated recovery program is:

`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/control/lavamd_exact_source_retirement_v1/LAVAMD_RESTORE_TO_OLD174.py`

Run it on `hrl-174-new`, where `/root/share/mnt164` is the verified SSHFS mount for `admin-wcx@10.208.130.164:/home/shared`:

```bash
python3 -B /root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/control/lavamd_exact_source_retirement_v1/LAVAMD_RESTORE_TO_OLD174.py --self-check
python3 -B /root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/control/lavamd_exact_source_retirement_v1/LAVAMD_RESTORE_TO_OLD174.py --preflight
python3 -B /root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/control/lavamd_exact_source_retirement_v1/LAVAMD_RESTORE_TO_OLD174.py --execute
```

Run `--execute` only after a fresh `--preflight` reports `PREFLIGHT_PASS`. The user's capacity override applied to retirement only; it did not lower the resource contract for a future restore. The last pre-retirement preflight reported insufficient capacity, so restoration must wait until the then-current contract admits the payload.

The program pins both server mount namespaces, the genuine164 SSHFS identity, Asset ID, Manifest and COMMIT hashes. It accepts only `kernel-1.traceg`, streams through 1 MiB buffers at 15 MiB/s without a full new174 staging copy, creates an exclusive temporary destination, fsyncs it, closes and fully rehashes it, restores numeric uid/gid/mode/mtime, and publishes through a no-overwrite hard link. Ctime is not restorable.

The four retained control files are verified and never overwritten. Unsafe paths, unknown members, active readers/writers, temporary-file collisions, insufficient capacity and content mismatches fail closed.

The complete 20.776 GB native restore was not executed in this Goal. The old174 `/root/share/mnt164` MD127 shadow is never accepted as genuine164.
