# PolyBench recovery pointer — r13

Contract: Framework coordination commit `31251186feccffec192cc1fef8fc7d8164d12d9f`.
This pointer covers exactly the two historical closeout stages below. Source release is owned by old174 Storage-Ops, after its independent r13 preflight. The target never deletes source files. Original polybench.tgz, default polybench.stage, Git, M5 and R1/R1R/R2 originals remain SOURCE_KEEP.

## Find the preserved archive

174-new validated mount: `/root/share/mnt164` = `admin-wcx@10.208.130.164:/home/shared`, `fuse.sshfs`. The similarly named directory in old174 is NOT this remote mount.

Archive on this mount:
`/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/Decoupled-L2/old174/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/polybench.tgz`

Native 164 location:
`/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/Decoupled-L2/old174/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/polybench.tgz`

Size: **17,943,970,556 bytes**. SHA256:
`9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca`

Recovery bundle: `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/POLYBENCH_RECOVERY_R13`.
Root machine-readable map: `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/POLYBENCH_RECOVERY_MAP_R13.json`.
The bundle includes the exact 13-file SHA256 TSV, file metadata JSONL, 14-directory metadata JSONL, original frozen map, two empty completion markers, recovery tool and independent integrity receipts. `SHA256SUMS` covers each bundle file except itself.

## Original paths and exact scope

Original extraction parent: `/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-extract`.

1. `polybench.correlation.closeout.stage`: 7 files including one empty marker; 33,273,281,470 content bytes. Source phase A, first.
2. `polybench.covariance.closeout.stage`: 6 files including one empty marker; 33,057,933,779 content bytes. Source phase B only if still needed after actual A df measurement and fresh safety checks.

All original absolute paths, tar member names, sizes, SHA256, numeric UID/GID, mode and nanosecond mtime are in `POLYBENCH_RECOVERY_MAP_R13.json`. All 14 directory paths and metadata are in its `directory_metadata` array. The two marker bytes are stored separately in `markers/correlation.complete` and `markers/covariance.complete` (both empty, SHA256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855).

Frozen manifest SHA256: `bca6dfc2b43f4715ce0c6e55d4faa8ae11f3f4c7be7b96279e5671489004f274`.
File metadata SHA256: `50c22e05d5550a5f3a8d80e45baf9b13e34beadfa01f5d6a333e914894753a80`.
Directory metadata SHA256: `d0f8ea5d069e370a045f9834cb21799d8fffa341c62285a39b00bec33ddbb3e9`.

## Usable recovery procedure

Run on a host with verified read access to the real 164 archive and a native destination filesystem. If running directly on 164, substitute `/home/shared` for `/root/share/mnt164` in A. To recover on old174, establish authenticated access to this real archive first; do not use old174's unrelated local mnt164 directory. Any new transfer remains subject to the single-stream, <=512MiB batch, 30MiB/s and Share >=40GiB contract.

Choose a **new absent destination** below an existing owned parent, with capacity for the selected stage plus the applicable resource reserve. These commands recover into an independent path; owner review is required before later promoting it to an original project path.

```sh
A='/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02'
BUNDLE="$A/POLYBENCH_RECOVERY_R13"
ARCHIVE="$A/Decoupled-L2/old174/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/polybench.tgz"
cd "$BUNDLE"
sha256sum -c SHA256SUMS
printf '%s  %s\n' '9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca' "$ARCHIVE" | sha256sum -c -
# Create an owned parent on a native filesystem; DEST itself must not exist.
DEST=/absolute/existing/owned/parent/polybench-recovered-new
sudo python3 "$BUNDLE/restore_polybench_r13.py" \
  --bundle "$BUNDLE" --archive "$ARCHIVE" --destination "$DEST" \
  --stage both --apply-native-metadata --min-free-after-bytes 53687091200
```

Use `--stage correlation` or `--stage covariance` for selective recovery. Keep the original floor and applicable owner-approved reserve; 53,687,091,200 bytes above is 50GiB. The script hashes every selected output during writing and independently after close/reopen, recreates the exact markers, applies numeric file attributes and directory attributes bottom-up, then verifies them. For `both`, require 13 files, 11 nonempty members, 2 markers, 14 directories, 66,331,215,249 content bytes and `RECOVERY_PASS`. It rejects an existing destination, path traversal and original-stage in-place recovery. Writes are rate limited and segmented at <=512MiB; future cross-host transfers require the established batch protocol separately.

The eleven data files are UID 543796 / GID 5000 / mode 0644. The two empty markers are UID 0 / GID 0 / mode 0644; directories are UID 0 / GID 0 / mode 0755. Exact mtimes come from the map. Numeric ownership application needs root/CAP_CHOWN on a native filesystem. SSHFS projected UID/GID/mode is not original native metadata. POSIX ctime is recorded for provenance and cannot be restored to its historical value.

## Integrity and small recovery evidence

Whole archive closed/reopened SHA256 and all 35 ordered ranges: target commit `8624267dcade80948d52ad235298f97002cdbe0c`.
Independent full gzip CRC/EOF plus all 11 member SHA256, markers and frozen metadata: target commit `e7b8ada57598e926bc612c71c8ac4dee65e9f874`.
Source independent whole SHA256: `swayhrl/gpu-l2-cache-verilog` commit `900917936180ed4a0fccd119acfee80323a5d6b0`; source phase acceptance `b0034506b9439f89b621eda2fb12494f62e20c82`.

R13 reuses those full-content proofs, as explicitly allowed by the contract. Fresh r13 evidence separately records current archive locator/size/identity and sidecar hashes, a real main-archive 489-byte stats.csv recovery plus both empty markers, native numeric file/directory permission/mtime validation, and independent 164 close/reopen hashes. No 66GB native rebuild or repeated 35-batch transfer was performed. See `POLYBENCH_R13_TARGET_RECOVERY_RECEIPT.json` and `POLYBENCH_SMALL_RECOVERY_R13.json`. The final publication receipt supplies the exact r13 target commit and fetched remote SHA; no PASS may be inferred before that publication.

## Original directory state and release handoff

At target publication, target has deleted **zero** old174 source files and does not claim actual reclaimed root bytes. User authorization permits only the frozen two-stage scope after source's r13 preflight. Consult the latest source execution branch `swayhrl/gpu-l2-cache-verilog:hrl/ops-174-source-audit-exec-v1`, directory `docs/ep_l2/operations/174new_to_164_archive_v1/source_receipts/20261016_storageops_02`, for `POLYBENCH_R13_PRE_RELEASE_PASS/HOLD`, A_RELEASED/HOLD and optional B_RELEASED/HOLD receipts, exact original-path state and measured df deltas. Old r10 SOURCE_KEEP/no-authorization fields describe their historical evidence time; r13 supersedes them only for the exact two-stage conditional source release.

Source performs A first and immediately obtains independent Lane5/Lane1 admission checks from real /workspace. B requires a new source preflight and may stay KEEP once legal builds have sufficient space. Expected allocation is not a measured df gain. Future manual consumers may require restoring these historical paths; that user-accepted risk is why this independent recovery pointer and frozen metadata are retained.
