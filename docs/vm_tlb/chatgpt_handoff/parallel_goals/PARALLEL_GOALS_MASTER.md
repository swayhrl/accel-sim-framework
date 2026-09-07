# Parallel goals master

Status: **AUTHORIZED**.

## Objective

Exploit the 512-logical-CPU, large-memory host with three isolated goal-mode Codex windows while preserving one authoritative evidence lineage.

The governing rule is:

> Parallelize independent experiments and offline analysis; never parallelize a stateful formal ROI by restarting each kernel independently.

A formal `config × ROI` run must preserve cross-kernel VM/TLB/PWC/cache/replacement history in one simulator process. Offline immutable-trace analysis may shard freely by kernel/file.

## Window ownership

### A — authoritative M4C

Scope:

`remaining C3 -> C3 8/8 closeout -> C4 export/locality/characterization -> review pack -> STOP`

A may repair Framework-only analysis/export tooling after C3 if needed, but must not change the frozen formal binary/config/list/object-map and then retroactively reuse old C3 results as if produced by the new binary.

### B — speculative farm

Scope:

`B0 resource calibration -> B1 offline trace mining -> B2 VM OFAT sweeps -> B3 cache sweeps -> B4 non-LLM controls -> B5 optional TLB×L2 grid -> B6 closeout`

B may run many independent simulators concurrently. It must retain one continuous simulator process per `ROI × config` and label all results speculative.

### C — speculative M4B

Scope:

`C0 admission -> C1 paper/sub-entry audit -> C2 sub-entry candidate -> C3 Weight Segmentation -> C4 bounded real-trace validation -> C5 optional full candidate runs -> C6 closeout -> STOP before M5`

C may use the pre-authorized `REFERENCE_APPROX_SUBENTRY_16` only when the exact/reference-backed sub-entry details remain unavailable after targeted audit, and must retain the approximation label.

## Evidence priority

1. Window A accepted/formal evidence.
2. Window A derived C4 tables from accepted C3.
3. Window B/C speculative results.
4. Diagnostics/pilots.

A later speculative result must never silently replace a formal one. Promotion requires explicit review and provenance binding.

## Repository/worktree policy

### Window A

Continue the already-running authoritative worktrees. Do not checkout the coordination branch into the active formal worktree. Read coordination docs from a separate checkout or via `git show`.

### Window B

Recommended:

- Framework branch: `hrl/vm-spec-farm-v0`
- Framework worktree: `/workspace/worktrees/accel-sim-vm-spec-farm`
- Core branch: `hrl/vm-spec-farm-v0`
- Core worktree: `/workspace/worktrees/gpgpu-sim-vm-spec-farm`
- Scratch root: `/workspace/vm-spec-farm/`

Core starts exactly from `0d92e6aa8fd8bc885ffdf081a559bc616aaa85fd`. Framework starts from this coordination handoff head or an exact descendant containing only handoff/docs changes relative to the accepted source.

### Window C

Recommended:

- Framework branch: `hrl/vm-m4b-speculative-v0`
- Framework worktree: `/workspace/worktrees/accel-sim-vm-m4b-speculative`
- Core branch: `hrl/vm-m4b-speculative-v0`
- Core worktree: `/workspace/worktrees/gpgpu-sim-vm-m4b-speculative`
- Scratch root: `/workspace/vm-m4b-speculative/`

Core starts exactly from `0d92e6aa8fd8bc885ffdf081a559bc616aaa85fd`.

## Git rules

- Never `git add .` or `git add -A`.
- Explicit-path staging only.
- No force push.
- No pushes to official upstream.
- B/C never merge/cherry-pick themselves into A automatically.
- Large traces, run logs, binaries, build trees, SQLite scratch, and experiment outputs stay outside Git; commit manifests/hashes/tables/review packs only.

## Continuous execution

Each window is a Goal with internal gates. Passing ordinary gates auto-continues. Do not stop to ask for confirmation on normal transitions.

For ordinary failures Codex must attempt repair: inspect logs/code, reproduce minimally, patch, validate, and continue. If an experiment is invalid because of a local script/config error, fix it and rerun that experiment; do not abandon the Goal.

## Normal final stops

- A: after C4 review pack, before C5.
- B: after B6 speculative farm closeout.
- C: after C6 speculative M4B closeout, before synthetic-KV/M5.
