# DTC-L1 Explicit Goal Launch Contract

Status: **ACTIVE GOAL CONTRACT — RECOVER M4 COMPLETION ACCOUNTING, THEN FINISH M4, STOP BEFORE M5**

This file is the short durable objective for Codex Goal mode. The active recovery details are in `goal/M4_COMPLETION_ACCOUNTING_RECOVERY.md`.

## Goal

Recover the source-reachable DTC cacheable-load completion-accounting failure exposed by PolyBench 2DConv, prove no regression of closed M1-M3 behavior, then finish all remaining M4 HARD validation and stop at:

`READY_FOR_M5_REVIEW`

The persistent Goal is not complete merely because 2DConv is repaired. It is complete only when:

1. the first 2DConv `PAPER_IO` / `PAPER_OO` dependency mismatch is localized to a source-backed root cause;
2. a minimal architecture-neutral repair restores conserved exactly-once DTC dependency ownership;
3. permanent cardinality/completion regressions exist;
4. exact 2DConv IO/OO runs complete with closed dependency/PIB/inflight/credit invariants;
5. PAPER_BASE timeout is separately classified from progress evidence;
6. closed-stage CTests and IO/OO/sector/LEGACY regression checks pass;
7. the existing PTX fence reachability resolution remains respected without adding frontend semantics;
8. all remaining active M4 Store/Atomic/bypass/mixed/workload/parser/CSV/hygiene gates pass;
9. at least five provenance-resolved representative Base/IO/OO workload triplets are accepted;
10. `review_packs/M4_COMPUTE_BRINGUP/` is complete;
11. both branches are pushed/clean and `git diff --check` passes;
12. `codex_handoff/LATEST_REPORT.md` says `READY_FOR_M5_REVIEW`;
13. M5 has not started.

## Active branches

Core:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0`

Framework:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0`

M0 branches remain read-only anchors.

## Mandatory current-state read order

Framework:

1. `AGENTS.md`
2. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
4. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`
5. this file
6. `docs/dtc_l1/goal/M4_COMPLETION_ACCOUNTING_RECOVERY.md`
7. `docs/dtc_l1/implementation/M4_COMPUTE_BRINGUP_FAILURE.md`
8. `docs/dtc_l1/implementation/M4_MEMORY_OP_SEMANTICS.md`
9. `docs/dtc_l1/goal/M4_FENCE_REACHABILITY_RESOLUTION.md`
10. `docs/dtc_l1/goal/VALIDATION_ACCEPTANCE_MATRIX.md`
11. `docs/dtc_l1/goal/M1_M4_GOAL_PLAN.md`
12. `docs/dtc_l1/goal/COUNTER_INVARIANT_SPEC.md`

Core:

13. `AGENTS.md`
14. `docs/dtc_l1/DTC_L1_SPEC.md`

Specific precedence:

- for the active completion-accounting blocker, `M4_COMPLETION_ACCOUNTING_RECOVERY.md` is authoritative;
- for fence/source-reachability only, `M4_FENCE_REACHABILITY_RESOLUTION.md` plus the updated validation matrix are authoritative refinements of older generic plan language.

## Closed stages

- M1: PASS.
- M2: PASS.
- M3: PASS.

Do not redo or weaken closed work unless the active recovery demonstrates a real regression.

## Current active blocker

PolyBench 2DConv:

- `PAPER_IO` aborts on `pending >= dependencies` in DTC instruction completion;
- `PAPER_OO` aborts on the same invariant;
- `PAPER_BASE` reached the fixed 240-second diagnostic wall-clock limit and is not yet classified as deadlock.

The IO/OO failure is a source-reachable correctness failure. It must be repaired by tracing and conserving dependency ownership, not by weakening assertions.

## Immediate priority

Execute `R4C.0 -> R4C.8` from `M4_COMPLETION_ACCOUNTING_RECOVERY.md`.

Do not stop for ordinary localization/checkpoint PASS results. Commit/push safe semantic checkpoints and continue until either:

- a recovery HARD stop condition occurs; or
- recovery fully passes and the remaining M4 Goal can resume automatically.

After recovery PASS, continue the remaining M4 work without new human authorization and stop only at an active HARD failure or final `READY_FOR_M5_REVIEW`.

## Forbidden shortcuts

Do not:

- clamp/zero pending-write accounting;
- remove the failing assertion to obtain workload completion;
- release scoreboard state without exact dependency ownership;
- change 128B DTC dependency granularity just to match a failing count;
- reintroduce conventional L1D MSHR/fill as the IO/OO read backend;
- modify L2/NoC/DRAM;
- add PTX fence frontend semantics or map `membar` to `FENCE_OP`;
- tune performance toward thesis numbers;
- begin M5.

## Final STOP boundary

STOP with pushed evidence if a source-backed minimal repair cannot be established, a closed-stage regression appears, PAPER_BASE is proven unexpectedly no-progress/deadlocked, another active M4 HARD gate fails, or M4 reaches `READY_FOR_M5_REVIEW`.

Do not begin M5.
