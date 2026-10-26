# HybridSort exact Source retirement ? final status

Status: **DONE**

- Asset: `TRACE_2f6210166d43b19e`
- Deleted: `68` exact `kernel-*.traceg` files
- Logical bytes: `16,091,909,083` (`14.9868 GiB`)
- Allocated bytes: `16,092,147,712` (`14.9870 GiB`)
- Observed `df` increase: `16,091,574,272` bytes (`14.9864 GiB`)
- SSD available after independent audit: `53,861,294,080` bytes (`50.1622 GiB`)

The Source directory remains and contains exactly `commandlist`, `kernelslist`, `kernelslist.g`, and `stats.csv`. All four retain their frozen SHA and numeric metadata. The directory's uid/gid/mode/mtime were restored; ctime is not restorable after unlink.

All 68 files had an immutable per-file INTENT before non-recursive unlink and a DONE receipt afterward. Current FD/mmap/cwd/writer and registry checks were clear. Read-only ext4 `debugfs` confirmed all 68 Source inodes were allocated in the current overlay upperdir.

The genuine164 bundle remains at:

`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets/TRACE_2f6210166d43b19e`

Manifest SHA256: `b526b722d71bd08d742641ca9a2548723480cbae2e7a1b25bf6eed4e7d106a9b`  
COMMIT SHA256: `f013c10db2df7e94ea5919819e791161a7a7a2a0d11bbeea1f9507b3b2356916`

The prior `ARCHIVED_CONTENT_VERIFIED` full-SHA/COMMIT receipt was reused; no 16 GB full-body rescan or native restore was performed. Current Manifest, COMMIT, range/tree selectors, member sizes, metadata and headers passed the quick readback. SSHFS inode numbers changed uniformly since the earlier snapshot, so content-stable fields and cryptographic receipts were used instead of treating remote inode numbers as persistent identifiers.

SRAD and lavaMD terminal states are exactly unchanged. No other Source, archive, scientific task/result, registry, controller, budget or Git object was modified.
