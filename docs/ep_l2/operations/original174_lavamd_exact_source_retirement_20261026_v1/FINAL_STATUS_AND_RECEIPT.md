# ORIGINAL174 lavaMD exact Source retirement — final status

Status: **HOLD_RESTORE_CAPACITY_BEFORE_INTENT**

Asset: `TRACE_90174dcf58988a5d`

No deletion occurred. The authorized `kernel-1.traceg` remains at the original old174 Source with its frozen inode, one hard link, `20,776,255,925` logical bytes, `20,776,263,680` allocated bytes, metadata and SHA256 `ccbd8ff9ff00c6b5a2fc49e982c652e12259b59378f2853593f36df8ae24701f`.

## Passed gates

- Source membership, current identity and full SHA: PASS for all five members.
- Genuine164 membership, Manifest, COMMIT, range receipt, tree receipt and current full SHA: PASS for all five members.
- Genuine164 Manifest SHA256: `75810b00842cb095dcb837ad5a7a888c192b4db5a06f0b1d23c17cf04ba3ce08`.
- Genuine164 COMMIT SHA256: `a39062e9d39d483f9d517fc496683e8be838c5a8b78047ab51a0ddee1cf61686`.
- Current FD, mmap, cwd, executable, command-line reader/writer and process visibility audit: PASS; no reader/writer and no unreadable process.
- Authoritative Source and native registries: no old lavaMD Source-path match.
- Historical Baseline and Decoupled consumers: completed successfully on 2026-08-14; both symlinks are preserved.
- Physical storage layer: PASS. Read-only ext4 `debugfs` resolved the exact current overlay upperdir pathname to inode `49300667`, size `20,776,255,925`, one link and `40,578,640` 512-byte blocks. The file is an allocated upper-layer object rather than a lower-only whiteout candidate.
- Dedicated restoration program syntax, endpoint pins, archive identity, safe path rejection, no-overwrite publication and failure behavior: PASS.
- HybridSort Source and genuine164 archive before/after snapshots: exactly unchanged.
- Completed SRAD Source terminal state: exactly unchanged and not replayed.

## Blocking gate

The unchanged Source restoration-capacity contract did not pass:

- Actual SSD available bytes: `17,512,468,480`
- Hypothetical available bytes after complete lavaMD reclaim: `38,288,732,160`
- Existing contract reservation before writing a restore: `52,412,022,784`
- Restore payload allocation estimate: `20,776,259,584`
- Required available bytes before a compliant restore: `73,188,282,368`
- Shortfall after hypothetical reclaim: `34,899,550,208` bytes (`32.50 GiB`)

The native registry currently contributes `43,754,979,328` bytes of declared reservations, including the running `DTC_AE_V100_FULL_SWEEP_20261025_V1` reservation. This Goal did not edit the registry, reduce resource thresholds, stop science, or reclaim another asset.

Because the dedicated restore could not satisfy capacity admission, the controller stopped before a retirement INTENT. `kernel-1.traceg` was not unlinked. Actual lavaMD SSD reclaim is therefore `0` bytes; candidate logical and allocated sizes are not counted as released space.

## Preserved state

The Source directory still contains exactly:

- `kernel-1.traceg`
- `commandlist`
- `kernelslist`
- `kernelslist.g`
- `stats.csv`

All four control files retain their frozen SHA and metadata. The Source directory, historical functional symlinks and scientific results remain unchanged. Any future replay needs the trace to remain present or must restore it first after a later authorized retirement.

HybridSort `TRACE_2f6210166d43b19e` remains completely unchanged. No other archive, Source asset, controller, budget, registry, scientific result or Git object was modified.

## Recovery and future action

The dedicated recovery entry and exact commands are documented in `LAVAMD_RESTORATION_ENTRY.md`. The full 20.776 GB native restoration was not executed because Source remains intact. A future retirement requires a new disposition run and a fresh capacity preflight; this HOLD receipt is not unlink authorization.

Durable evidence is stored in `checkpoint/`, in the required JSON reports, and on genuine164 under:

`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/control/lavamd_exact_source_retirement_v1`
