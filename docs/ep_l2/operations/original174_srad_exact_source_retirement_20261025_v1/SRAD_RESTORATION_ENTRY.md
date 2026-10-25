# SRAD exact restoration entry

The recovery source is genuine164 bundle `TRACE_300274ed6041b087`:

`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets/TRACE_300274ed6041b087`

Run the recovery program on `hrl-174-new`, where `/root/share/mnt164` is the verified SSHFS mount for `admin-wcx@10.208.130.164:/home/shared`:

```bash
python3 -B /root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/control/srad_exact_source_retirement_v1/SRAD_RESTORE_TO_OLD174.py --self-check
python3 -B /root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/control/srad_exact_source_retirement_v1/SRAD_RESTORE_TO_OLD174.py --execute
```

The program streams the exact 502 `.traceg` members from genuine164 to the original old174 directory through the pinned old174 SSH identity. It uses 1 MiB buffers, does not create a full 174-new staging copy, never overwrites a differing destination, and requires the original Source resource admission plus capacity for every missing file. Each restored file is written to an exclusive `.SRAD_restore.writing` path, fsynced, closed and fully rehashed before no-overwrite publication. It restores numeric uid/gid/mode/mtime; ctime is not restorable.

The four retained control files are verified and never restored over. Exact pre-existing trace files are accepted only after full SHA and numeric metadata verification. A wrong or unexpected trace file fails closed.

The complete 21.565 GB native restoration is **not performed in this retirement Goal**. The entry is syntax/self-check qualified and the original archive tree is independently full-SHA reverified. A future full restore remains subject to the then-current SSD reservations, active readers/writers, locks, I/O guard, and old174 endpoint identity.

The old174 path `/root/share/mnt164` is an MD127-local shadow and must never be used as the genuine164 source.

After this retirement, the Source directory and its four control files remain, while all 502 `.traceg` paths are absent. The two historical functional symlinks still resolve to this directory. Run `--execute` successfully before any future consumer uses the archived-large input; a control-only directory is not a complete trace input.
