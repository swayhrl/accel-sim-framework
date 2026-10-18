# TLS-Cache Cold Asset Migration V10 — master contract (2026-10-18)

## Authority and objective

User direction: migrate the TLS two-level L1-interconnect project's cold **non-code** artifacts from the original 174 workspace to real 164 storage in one coordinated wave. **Source code must stay on original 174**. This is a new, independent TLS-V10 job, **not** a restart/extension of V9, R19, Lane1 or Lane5.

Official V9 closed:
- target 174-new Framework `hrl/ops-174new-164-archive-exec-v1` HEAD `c870ca77456d4d4d70a110411fa5c60934976666`;
- source old174 `swayhrl/gpu-l2-cache-verilog`, `hrl/ops-174-source-audit-exec-v1` HEAD `3891fcd93a7ac5c3361d8f476d3c41036104b151`;
- 615 C2P/M2D files archived+restored, source KEEP. R2's original, exactly 191-file release measured 2,689,970,176 B immediately. Do not redo V9 or release C2P/M2D.
- genuine-164 V9 recovery entry: `docs/ep_l2/operations/174new_to_164_archive_v1/receipts/20261018_storageops_v9_target_01/V9_RECOVERY_POINTER.md` at target HEAD above. Reuse verified V9 transaction/recovery tooling without changing V9 receipts.

## Scope (initial figures are inventory estimates, NOT exact frozen counts)

1. TLS-exclusive source worktree `/workspace/worktrees/accel-sim-tls-cache` (~10.0 GiB gross, including subdirectories below). Inspect all **cold, generated** non-code assets and preserve the worktree itself.
   - `hw_run/tls-cache-p9-public-v1` (~2.7 GiB);
   - P9 historical `hw_run/tls-cache-p9` matrix-v3 and matrix-v4 (~1.3 GiB each).
   - The poller updates **matrix-v2** and polls staging every minute: protect matrix-v2/staging, its inputs, and any open or scheduled writer/reader. Never infer v3/v4 are cold just from their names.
2. TLS V5 observe `/workspace/worktrees/accel-sim-tls-cache-v5-observe` (~1.0 GiB gross; ~717 MiB build, ~318 MiB results): protect uncommitted scripts/configs/plots, archive only independently frozen outputs or generated build artifacts.
3. Two Dynamic-way worktrees (~0.8 GiB gross together): discover exact canonical paths and preserve source/Git/modified files, archive cold generated assets.
4. Every other **TLS-exclusive** cold non-code asset under these TLS worktrees found by a bounded inventory; avoid counting descendants twice. Rough exclusive-TLS total ~11.8 GiB **includes** P9, V5 and Dynamic-way, not their sum.
5. Cross-project mixed `/workspace/worktrees/accel-sim-decoupled-l2/hw_run/tls-c2p-v100-20260822` (~1.4 GiB gross) is **not TLS-exclusive**. An offload script was alive, paused by an 80 GiB gate. Do not stop it, change its threshold, migrate its active files, or release any mixed file without separately proving sole TLS ownership and the existing script has reached a safe closed state; otherwise HOLD/KEEP with a manifest.
6. ~6.8 GiB shared trace inputs live in other projects: dependency-index only, **no copy/release charged to TLS** absent separately authorized shared-owner protocol. Do not touch Git packs/objects, scientific inputs, active experiments or other projects.

## Classification

- `CODE_KEEP`: tracked/untracked/modified source code, Git trees and objects, scripts, notebooks, TeX/Bib, editable configuration, source manifests, human-curated data, any file whose provenance or consumers make it source-like. No worktree/root deletion, no git reset/clean/gc/prune; leave uncommitted changes exactly intact.
- `COLD_TRANSFER_CANDIDATE`: generated text output, logs, tables, images, PDFs, run result directories, temporary build binaries/objects, test-wave dumps with frozen original scientific provenance. Include untracked/ignored files, but inspect origin/activeness individually; never classify solely by suffix.
- `ACTIVE_OR_SHARED_KEEP`: PID/open FD/cwd/argv, scheduled job, live writer/poller, registry participant, shared trace, mixed C2P, unresolved link/dependency, or any identity churn.
- `HOLD`: ambiguous ownership, missing identity, symlink/hardlink surprise, broken archive/restore, changing file, insufficient resources or unclear destruction authority.

V10 scope authorizes **archiving TLS-exclusive non-code material**, not a blanket deletion. For old174 destructive cleanup, produce a fully **exact** per-file release selector plus GitHub-backed restored proof and ask for exact selector approval unless a valid prior approval already binds that exact selector. A generic instruction to "move TLS outputs" must not be promoted into deletion authority over an unreviewed list. Mark successful copies `ARCHIVED_SOURCE_KEEP` until released under that gate.

## Timing/resource gates

At 2026-10-18 18:53 CST, Lane5 reported two live central sims and a final new-launch deadline of **19:30:14.500719 CST**, 49/72 starts, 37 accepted results at snapshot. **No bulk copy/hash/compression/cleanup before this deadline or while competing active jobs/leases lack an independent resource PASS.** Read-only bounded inventory may proceed now. The deadline alone is not proof all sims have stopped.

Carry V9 conservative floors: source workspace >=48 GiB, Share >=40 GiB, free RAM >=64 GiB, plus active Lane reservations and result caps. One transfer sender, no second uploader/watcher; staging bridge <=256 MiB at any time; rate <=30 MiB/s. Use native old174 source ownership and separate 174-new genuine-164 mounted via verified `admin-wcx@10.208.130.164:/home/shared`. Never interpret same-named mounts as identical FS. Watch current disk/RAM and yield to ongoing science. Recheck per batch.

## Transaction model and acceptance

Freeze exact canonical paths, relative paths, file types, SOURCE statx/lstat identity (dev/inode/nlink, UID/GID/mode/mtime_ns/ctime_ns, size, st_blocks), directory metadata, SHA256, link and Git/uncommitted status, owner/readers, source snapshot/commit, target native absent root, selector SHA256 and txid. Keep source scientific provenance attached. Prevent relative-path traversal/symlink following; special files HOLD.

Old174 sole SOURCE owner; 174-new sole real164 sender/restorer. Publish GitHub-reviewed manifest and bridge READY; 174-new stage to **new absent** real164 destination with fsync, reopen and exact content digests; independently restore to another absent native path and verify all file bytes and numeric metadata (original ctime is provenance only). Use bounded chunks and resumable immutable transaction IDs. No overwriting existing archive, no recopy to meet arbitrary bytes-saved targets. Optionally compress highly compressible text, recording compressed and original digests, with byte-identical original restoration proof. Source file release is a **separate**, source-owner-only operation with explicit exact approval and fresh activity/identity checks; keep an fsync journal and avoid any `rm -rf` or unapproved glob.

Source and target branch receipts must include full SOURCE→164→RESTORE index, per-batch signed READY/DEST_VERIFIED/SOURCE_KEEP, SHA256, proof scope, interruption/HOLD ledger, bridge cleanup, before/after `df` and source-release receipts. Archive bytes, compressed bytes, source apparent/allocated bytes, immediate source `df` gain, long-window delta and duplicated/shared input estimates **must be reported separately**. Final recovery pointer must be on genuine164 and in GitHub. Do not declare SOURCE_RELEASED when only archived.

No new algorithmic TLS development, paper/research changes, or Lane state modifications. Ordinary engineering faults: solve-and-continue within frozen contract. Stop for scientific provenance, boundary, authority or filesystem safety changes. Do not run a resident daemon.

## Execution order

- A: old174 bounded inventory, PID/FD/registry/poller audit, classify full TLS-exclusive scope; freeze immutable selector(s) and source READY; target independently verifies genuine164 and existing V9 tooling.
- B: archive/restore P9 public + matrix-v3/v4 first **only if idle**; follow with V5 generated outputs/build, Dynamic-way generated assets, remaining exclusive TLS cold files. Transfer multiple bounded batches under one sender. Preserve source and any active datasets.
- C: mixed TLS/C2P branch and poller-dependent assets are final audit/conditional substage only; if not quiescent, retain HOLD/KEEP and finish V10 with exact deferred list rather than touching a live process.
- D: propose **exact** release selector for safely restored, idle, TLS-exclusive non-code files and record blocked/active exceptions. Apply cleanup only after its exact separate approval through old174; otherwise complete `ARCHIVED_SOURCE_KEEP`. Keep small index/pointers without modifying tracked source or replacing active paths.
- E: independently cross-check target and source report, push on NEW isolated branches, remote-read back all receipts. Do not reset or re-run V9.

See role-specific Goals in the same directory.