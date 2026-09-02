# DTC-L1 Explicit Goal Launch Contract

Status: **ACTIVE GOAL CONTRACT — M2 CLOSEOUT -> M3 -> M4**

This file is the short durable objective for Codex Goal mode. Detailed architecture, tests, counters, and recovery rules remain authoritative in the referenced files below.

## Goal

Complete the validated DTC-L1 implementation from the current M2 recovery state through M4 without stopping for ordinary progress reports.

The verifiable end state is:

`READY_FOR_M5_REVIEW`

This means:

1. `M2_IO_READ` passes every HARD gate and has a complete review pack;
2. `M3_OO_SECTOR` passes whole-line OO HARD gates first, then the sector-extension HARD gates, and has a complete review pack;
3. `M4_COMPUTE_BRINGUP` preserves source-backed Store/Atomic/Fence/architectural-bypass semantics, passes all HARD gates, and completes the required Base/IO/OO compute bring-up set with closed invariants and provenance;
4. both active worktrees are clean, pushed, and `git diff --check` passes;
5. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md` says `READY_FOR_M5_REVIEW`;
6. M5 has **not** started.

## Active branches

Core:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0`

Framework:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0`

M0 branches are read-only anchors.

## Mandatory read order

Before continuing work, read:

Framework:

1. `AGENTS.md`
2. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
4. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`
5. this file
6. `docs/dtc_l1/goal/M2_IO_RESPONSE_RECOVERY_SPEC.md`
7. `docs/dtc_l1/goal/M1_M4_GOAL_PLAN.md`
8. `docs/dtc_l1/goal/COUNTER_INVARIANT_SPEC.md`
9. `docs/dtc_l1/goal/VALIDATION_ACCEPTANCE_MATRIX.md`

Core:

10. `AGENTS.md`
11. `docs/dtc_l1/DTC_L1_SPEC.md`

If the files conflict, STOP and report the conflict. Do not silently choose a meaning.

## Current verified execution state

M1 is closed PASS and must remain closed.

M2 recovery has already established the dedicated Paper-IO read request/response/PIB-writeback path. Source-backed evidence currently includes:

- root/sector-child request identity round trip;
- no IO-owned read response routed through conventional `baseline_cache::fill()`;
- real PAPER_IO VecAdd PASS;
- IO PIB/dependency/inflight/lower-credit drain closure;
- transient allocation-block retry handling;
- cap=2 lower-outstanding pressure recovery.

The mutable detailed checkpoint is always `codex_handoff/LATEST_REPORT.md`; do not redo passed work solely because this launch file is older than the latest semantic checkpoint.

## Immediate priority queue

Finish M2 rather than redesigning it.

Priority order:

1. close remaining directed M2 HARD cases, especially I06-I11;
2. close resource-pressure cases I12-I15; reuse already-valid I14 evidence where appropriate instead of rerunning without purpose;
3. perform an explicit high-MLP no-traditional-L1-MSHR proof that exceeds Baseline PIB=8 / MSHR=32 concurrency and demonstrates PAPER_IO read progress does not depend on conventional L1D MSHR capacity/merge state;
4. close IO counters/parser/drain assertions/build/CTest/hygiene;
5. create and push `review_packs/M2_IO_READ/` only when every M2 HARD item passes;
6. immediately continue to M3 without waiting for human confirmation.

For M3:

- finish **PAPER_OO whole-line first**;
- implement/validate random-access PIB, deterministic oldest-ready selection, retire width, line-level Ref Count, Shadow Ref checker, Merge/wakeup, active reclamation, O01-O13, and the IO-vs-OO causal HOL test;
- do **not** start sector extension before all whole-line OO HARD gates pass;
- only then implement/validate the 4x32B readiness/merge sector extension;
- create/push the M3 review pack and continue to M4 on PASS.

For M4:

- perform the source-backed Store/Atomic/Fence/architectural-bypass semantics audit before functional edits;
- preserve the underlying memory semantics; attach them to the correct DTC lifecycle rather than reinventing them;
- Atomic side effects must never be collapsed by read pending-hit merging;
- finish mixed-operation regressions, workload manifest, representative Base/IO/OO compute bring-up, strict invariant/provenance checks, and the M4 review pack.

## Goal-mode continuation policy

Do **not** stop merely to report:

- a semantic checkpoint commit;
- a directed test passing;
- M2 PASS;
- M3 PASS;
- a successful build;
- a long-running job that is still making measurable progress.

At safe semantic checkpoints, commit and push compact evidence, update Codex-owned `LATEST_REPORT.md` when useful, then continue working toward the goal.

At each major-stage PASS, create the required review pack, push it, update `LATEST_REPORT.md`, and automatically enter the next authorized stage.

When a long job is running, use the project 20/40/60-minute no-progress policy. While waiting on a genuinely long independent job, use the time only for non-conflicting analysis/documentation/test preparation; do not mutate the same active state concurrently in a way that invalidates the run.

## HARD stop conditions

STOP, preserve compact evidence, push safe semantic state, and update `LATEST_REPORT.md` if any of the following occurs:

1. a HARD validation item fails after a reproducible attempt;
2. a source-semantic ambiguity affecting architecture/correctness cannot be resolved from source plus frozen specs;
3. a fix would require changing a frozen M0 architecture decision;
4. LEGACY/M1 closed behavior regresses;
5. a proposed shortcut would reintroduce conventional L1D MSHR/fill as the hidden PAPER_IO read backend;
6. correctness would require special-casing an expected performance/deadlock result;
7. the task would require unauthorized L2/NoC/DRAM redesign;
8. M4 reaches `READY_FOR_M5_REVIEW`.

Do not keep trying unrelated speculative fixes after a HARD stop condition. Do not begin M5.

## Git/evidence discipline

- never use `git add .` or `git add -A`;
- stage explicit paths only;
- use semantic commits;
- preserve Core/Framework/config/workload/log provenance;
- do not commit large raw logs, traces, build trees, or generated binaries;
- maintain reviewable compact evidence and raw-log indexes/hashes;
- do not force-push the shared active branches.

## Goal completion statement

The Goal is complete only when Codex can state, with review-pack evidence:

> M2, M3, and M4 HARD gates all pass; Base/IO/OO compute bring-up is complete with closed invariants and provenance; both branches are pushed and clean; `LATEST_REPORT.md` is `READY_FOR_M5_REVIEW`; M5 has not started.
