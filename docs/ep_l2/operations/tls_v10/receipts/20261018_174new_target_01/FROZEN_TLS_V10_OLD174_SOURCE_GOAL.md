# Codex Goal — old174 TLS-V10 source owner (one continuous solve-and-continue task)

**Source environment only:** original 174, SSH port 2233, namespace `mnt:[4026534768]`, native `/workspace`. Do **not** run in 174-new. Source repo `swayhrl/gpu-l2-cache-verilog`, existing V9 closed at `3891fcd93a7ac5c3361d8f476d3c41036104b151`. Create an isolated **new** V10 execution branch/worktree for receipts and tooling; do not reset/restart V9.

**First read fully:** sibling `TLS_V10_MASTER_CONTRACT.md` at immutable coordinating commit supplied with this Goal; follow exact scope, roles, budgets, source deletion restrictions and genuine164 identity. Do not silently expand either the source inventory or existing source release rights.

## Task A: bounded TLS-complete inventory NOW (read-only)

- Read-only inspect the three major TLS worktree categories, including old P9 public/v3/v4, V5-observe and discover the two Dynamic-way canonical worktree roots. Identify the remainder of the ~11.8GiB TLS-exclusive inventory without double counting nested trees and hardlinks.
- Separately inventory the mixed TLS/C2P ~1.4GiB (report only; **do not move or delete while old offloader lives**), and the ~6.8GiB shared traces (referenced dependencies only; never claim as TLS-exclusive). Preserve source code, scripts, Git objects and tracked/untracked modifications without changes.
- Determine latest true writers/readers before deciding any historical output is cold: V9 source owner receipts; TLS P9 poller (staging read every minute and matrix-v2 writer), paused 80GiB-gated `tls-c2p-v100` offloader, cron/systemd/tmux/codex schedulers, PID/start_ticks/boot_id, open FD, cwd, argv, parent directory identity, registry and known plans. Do not stop/kill/adjust pollers. `lsof` failure is not proof of no readers.
- Classify every candidate as CODE_KEEP, COLD_TRANSFER_CANDIDATE, ACTIVE_OR_SHARED_KEEP, or HOLD; list reason and provenance. Do not use suffix-only selection. Keep `.git`, source, editable configs, research documents, active output, and non-reconstructable working inputs in place.
- Capture `df -B1` before the work and an exact non-overlapping logical/allocated bytes summary. SHA256 and lstat/fstat all frozen candidate files with path, dev/inode/nlink, UID/GID/mode/mtime_ns/ctime_ns, file type, size, st_blocks; separately archive directory native metadata and link policy. Handle changing files as HOLD; do not get a stale reading then later delete.

## Task B: first eligible group and subsequent batches

- Before 19:30:14.500719 CST 2026-10-18 do no bulk disk hashing, staging, compression, transfer or cleanup; only bounded inventory. After that, independently verify current Lane5 reservations/PIDs and workspace>=48GiB, Share>=40GiB, free RAM>=64GiB before starting. The clock passing is NOT proof Lane5 has finished.
- Freeze immutable selectors for all idle TLS-only non-code artifacts, start first with P9 public and matrix-v3/v4 if idle; then V5 generated build/results, the two Dynamic-way outputs, and remaining TLS-exclusive cold outputs. Keep actively read or written files out; do not write into their original paths.
- Coordinate with **one** 174-new sender through the verified existing V9 bridge. For each <=256MiB physical staging batch, publish source-owned `COPY_READY` manifest/transaction digest and bridge SHA; wait for target `DEST_VERIFIED`, independent `RESTORE_VERIFIED` and source own `SOURCE_KEEP` receipt before allowing target to delete exact bridge staging and requesting the next batch. Cap one stream at 30MiB/s.
- Reopen and recheck current source SHA/identity before each stage; compare target/bridge receipts and txid. If target or source commits differ from expected exact content, HOLD. Resumable idempotency must never silently change a frozen original.
- Do not migrate V9's C2P/M2D, Git packs, other project science or shared traces. Keep original `matrix-v2` and P9 staging while the poller remains active.

## Task C: source release proposal / optional separately authorized release

- Once 174-new publishes genuine164 archived+restore all-file digest/metadata proof, recheck source identity and all active references and produce a **complete exact per-file `TLS_V10_RELEASE_APPROVAL_PROPOSAL.jsonl`**, with nonselected path fingerprints and expected allocated bytes.
- Current user gave category-level direction to move non-code TLS assets; treat that as authority to ARCHIVE, not permission to unlink an unpublished selector. Without an explicit prior or subsequent authorization naming the exact frozen selector SHA256, publish `ARCHIVED_SOURCE_KEEP_RELEASE_PENDING_APPROVAL` and **do not unlink**. Active/shared/mixed/poller-dependent/unknown/dirty-code files must never enter an exact release list.
- If and only if exact selector authorization exists: source-only fsync INTENT/exact lstat+O_NOFOLLOW/file SHA and no active references, exact unlink, fsync DONE, crash audit. No rm -rf, glob deletes, directory wholesale removal, git clean/prune or speculative cleanup. If any intermediate state is uncertain, HOLD rather than repeat unlink. Preserve native paths or small recovery pointers required by running scripts; never create placeholders that misrepresent active data.
- Record immediate before/after `df` for any authorized release, and long-window endpoint separately from 164 archive size and estimated compression. If no actual source unlink, report workspace reclaim as **zero** even if archived data volume is large.

## Task D: closure

Publish small Git receipts on a NEW source branch (no GB artifacts in Git) with:
`TLS_V10_SOURCE_INVENTORY.jsonl`, `TLS_V10_CLASSIFICATION_AND_EXCLUSIONS.json`, `TLS_V10_EXACT_SELECTOR_MANIFEST.json`, per-batch READY and SOURCE_KEEP ACK, `TLS_V10_RELEASE_APPROVAL_PROPOSAL.jsonl`, `TLS_V10_SOURCE_FINAL_RECEIPT.json`, `TLS_V10_SOURCE_STATUS.md`, SHA256 manifests, signed source/target result join, actual disk and concurrency accounting. Push, fetch from remote, verify bytes/SHA. Report full gross/exclusive/mixed/shared counts, archived-and-restored counts, release-eligible count, actual deleted count, skipped active reasons, latest HEAD and next exact action. Do not start a new persistent watcher or a second pipeline.

Ordinary engineering issues solve-and-continue. Any ambiguity about scientific authority, ownership, live reader, mount identity, numerical source, or release authorization => fail closed with an exact itemized HOLD (not a generic stop).