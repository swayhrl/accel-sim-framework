# ORIGINAL174 SRAD exact Source retirement — final status

Status: **DONE**

Asset: `TRACE_300274ed6041b087`

The authorized finite retirement completed on 2026-10-25. The old174 Source lost exactly the 502 `.traceg` members in the qualified archive manifest. No recursive deletion was used. Every file has an immutable per-file INTENT followed by DONE, and the compressed journal is retained in `checkpoint/PER_FILE_INTENT_DONE.jsonl.gz` and on genuine164.

## Result

- Files unlinked: `502`
- Logical bytes unlinked: `21,565,127,570` (`20.0841 GiB`)
- Source allocated bytes unlinked: `21,566,582,784` (`20.0854 GiB`)
- `/root/data` available bytes before: `23,149,150,208`
- `/root/data` available bytes after the retirement worker: `44,680,536,064`
- Observed available-byte increase: `21,531,385,856` (`20.0527 GiB`)
- Available bytes at independent post-audit: `44,675,596,288` (`41.6074 GiB`)

The logical size, unlinked allocation and `df` change are separate quantities and are not added. The `df` interval includes possible concurrent filesystem activity. A controlled first-file test increased available space by `344,064` bytes after unlinking a file with `352,256` allocated bytes, and the full operation showed sustained physical-space growth. The Source was therefore on a physically reclaimable layer rather than a whiteout-only layer.

## Preserved Source state

The Source directory remains at:

`/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/srad_v1-rodinia-3.1/100_0_5_502_458/traces`

It contains exactly these four regular files, all with their manifest SHA256 and original numeric metadata:

- `commandlist`
- `kernelslist`
- `kernelslist.g`
- `stats.csv`

The directory's uid, gid, mode and mtime were restored. Directory ctime changed because ctime cannot be restored after unlink operations. The two completed historical `decoupled-l2-functional` baseline/decoupled symlinks remain and now resolve to the retained control-only directory. Any future `archived-large` consumer must restore the 502 traces before running.

## Genuine164 archive and restoration

The recovery bundle remains unchanged on genuine164:

`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets/TRACE_300274ed6041b087`

- Members: `506` total, including `502` `.traceg`
- Total archived bytes: `21,565,199,284`
- Manifest SHA256: `b8007329860a36de022edb70c2a29ea6570502c5f307d47a1d515f73796432b3`
- COMMIT SHA256: `7937f45865f94b07a1634f48fe551ca312f6296d42386e3722f809f6fb4377ce`
- Pre-retirement full SHA check: PASS for all 506 members
- Post-retirement frozen-identity check: PASS for all 506 members
- Genuine164 mount: `admin-wcx@10.208.130.164:/home/shared` at new174 `/root/share/mnt164`

The old174 `/root/share/mnt164` MD127 shadow was rejected as an archive source. Recovery instructions are in `SRAD_RESTORATION_ENTRY.md`; the persistent executable is:

`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/control/srad_exact_source_retirement_v1/SRAD_RESTORE_TO_OLD174.py`

Its endpoint, archive, manifest, streaming protocol and fail-closed checks pass `--self-check`. It restores uid/gid/mode/mtime and verifies every closed file by full SHA before no-overwrite publication. The complete 21.565 GB native restore was not executed in this Goal, so large-input native restoration remains explicitly untested.

## Reader and scientific boundary

Pre-delete and post-delete scans found no current FD, mmap, cwd, executable or command-line reader and no unreadable process. Neither authoritative science registry contained the Source path. Historical baseline and decoupled consumers had already completed successfully. The unregistered opt-in `archived-large` profile remains a future dependency and requires restoration first.

No scientific program, result, registry, budget, controller, Git object or unrelated file was changed.

## Protected assets

`TRACE_90174dcf58988a5d` (lavaMD) and `TRACE_2f6210166d43b19e` (HybridSort) were snapshotted before and after the operation. Their Source member identities and archive COMMIT identities are exactly unchanged. They remain protected future-review candidates; this Goal granted no deletion authority for either.

## Durable evidence

- `SRAD_SOURCE_AND_READER_AUDIT.json`
- `SRAD_TRUE164_ARCHIVE_VERIFICATION.json`
- `SRAD_EXACT_RETIREMENT_INTENT_DONE.json`
- `SRAD_REAL_SSD_RECLAIM_ACCOUNTING.json`
- `SRAD_RESTORATION_ENTRY.md`
- `REMAINING_COLD_TRACE_CANDIDATES.md`
- `checkpoint/` containing the full SHA receipts, qualified whitelist, INTENT, controlled test, Source DONE, controller DONE, post-delete audit and compressed 502-file transaction journal

The controller DONE SHA256 is `9c64fbefcba02226657364944956ae31c4f92bb2b1836b51a923bf1464563770`. The uncompressed per-file journal SHA256 is `6e3a4033485d1f5ae06d2e25a284cc1fa646a914a3b75236fed46c61af3a347f`; its deterministic gzip SHA256 is `f6c1b51e39e295f59fd8821dd195eb0ea5dbfc5df455dc1717136f4df53d1506`.

No HOLD or unresolved partial transaction remains.
