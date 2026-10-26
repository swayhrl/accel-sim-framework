# ORIGINAL174 lavaMD exact Source retirement ? final status

Status: **DONE_AFTER_USER_CAPACITY_OVERRIDE**

Asset: `TRACE_90174dcf58988a5d`

The exact retirement completed on 2026-10-26 after the user explicitly waived immediate restoration-capacity admission for this Source unlink. The earlier `HOLD_RESTORE_CAPACITY_BEFORE_INTENT` remains immutable history; it was not rewritten as a pass. A new authorization and transaction identity were persisted before unlink.

## Result

- Files unlinked: `1` ? `kernel-1.traceg`
- Logical bytes unlinked: `20,776,255,925` (`19.3494 GiB`)
- Source allocated bytes unlinked: `20,776,263,680` (`19.3494 GiB`)
- `/root/data` available bytes before unlink: `17,488,400,384`
- `/root/data` available bytes after unlink: `38,264,659,968`
- Observed available-byte increase: `20,776,259,584` (`19.3494 GiB`)
- Available bytes at independent post-audit: `38,262,300,672` (`35.6345 GiB`)

Logical size, unlinked allocation and `df` change are separate measurements and are not added. The interval can include concurrent filesystem activity.

## Verification and transaction chain

Before retirement, Source and genuine164 full SHA checks passed for all five members. The exact trace SHA256 was `ccbd8ff9ff00c6b5a2fc49e982c652e12259b59378f2853593f36df8ae24701f`. A read-only ext4 `debugfs` lookup proved that merged Source inode `49300667` was the same one-link allocated object at the current overlay upperdir path.

After the user's override, the controller rechecked Source identity, readers, both science registries, I/O pressure, genuine164 identities, the physical-layer receipt, HybridSort and SRAD. It then persisted:

1. `CONTINUE_QUALIFIED_WHITELIST.json`
2. `CONTINUE_INTENT_AFTER_CAPACITY_OVERRIDE.json`
3. `CONTINUE_FILE_INTENT.json`
4. the single non-recursive unlink
5. `CONTINUE_SOURCE_DONE.json`
6. `CONTINUE_DONE_CONTROLLER.json`
7. `POST_OVERRIDE_INDEPENDENT_AUDIT.json`

The Source directory now contains exactly `commandlist`, `kernelslist`, `kernelslist.g`, and `stats.csv`. All four retain their frozen SHA and numeric metadata. Directory uid/gid/mode/mtime were restored; directory ctime changed because it cannot be restored after unlink.

The two completed historical Baseline/Decoupled symlinks remain and now resolve to the control-only directory. Restore `kernel-1.traceg` before any future replay.

## Genuine164 and recovery

The genuine164 bundle remains unchanged:

`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/assets/TRACE_90174dcf58988a5d`

- Members: `5`
- Archived bytes: `20,776,256,536`
- Manifest SHA256: `75810b00842cb095dcb837ad5a7a888c192b4db5a06f0b1d23c17cf04ba3ce08`
- COMMIT SHA256: `a39062e9d39d483f9d517fc496683e8be838c5a8b78047ab51a0ddee1cf61686`
- Pre-retirement full SHA: PASS
- Post-retirement frozen-identity readback: PASS

Recovery commands and limitations are in `LAVAMD_RESTORATION_ENTRY.md`. No full native restore was run. A future restore must pass a fresh capacity preflight; the user override did not waive restore-write admission.

## Protected assets

HybridSort `TRACE_2f6210166d43b19e` Source members, Manifest, genuine164 members, COMMIT and recovery entry matched their before snapshot after retirement. The completed SRAD terminal state also matched exactly. No other Source, archive, scientific program/result, controller, budget, registry or Git object was modified.

## Durable evidence

The complete history, including the original HOLD, capacity override, exact INTENT/DONE chain, full SHA receipts and post-audit, is stored in `checkpoint/` and on genuine164 under:

`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1/control/lavamd_exact_source_retirement_v1`
