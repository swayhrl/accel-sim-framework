# DTC-L1 Explicit Goal Launch Contract

Status: **ACTIVE GOAL CONTRACT — FINISH M4, STOP BEFORE M5**

This file is the short durable objective for Codex Goal mode. Detailed architecture, validation, and the current source-reachability refinement live in the referenced files.

## Goal

Complete M4 from the current M1/M2/M3 validated state without stopping for ordinary progress reports.

The verifiable end state is:

`READY_FOR_M5_REVIEW`

This means:

1. M1, M2, and M3 remain closed PASS without regression;
2. M4 preserves source-backed Store/Atomic/architectural-bypass semantics;
3. the verified PTX proxy-fence reachability limitation is handled exactly as specified in `goal/M4_FENCE_REACHABILITY_RESOLUTION.md`, without inventing fence frontend semantics;
4. every active M4 HARD gate passes;
5. at least five provenance-resolved representative Chapter-4 compute workloads complete under PAPER_BASE/PAPER_IO/PAPER_OO with matching dynamic operation counts and closed invariants;
6. required compact CSV/parser/review evidence exists;
7. both active worktrees are clean/pushed and `git diff --check` passes;
8. `codex_handoff/LATEST_REPORT.md` says `READY_FOR_M5_REVIEW`;
9. M5 has not started.

## Active branches

Core:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0`

Framework:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0`

M0 branches are read-only anchors.

## Mandatory current-state read order

Framework:

1. `AGENTS.md`
2. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
4. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`
5. this file
6. `docs/dtc_l1/goal/M4_FENCE_REACHABILITY_RESOLUTION.md`
7. `docs/dtc_l1/implementation/M4_MEMORY_OP_SEMANTICS.md`
8. `docs/dtc_l1/goal/VALIDATION_ACCEPTANCE_MATRIX.md`
9. `docs/dtc_l1/goal/M1_M4_GOAL_PLAN.md`
10. `docs/dtc_l1/goal/COUNTER_INVARIANT_SPEC.md`

Core:

11. `AGENTS.md`
12. `docs/dtc_l1/DTC_L1_SPEC.md`

For M4 fence-related requirements only, `M4_FENCE_REACHABILITY_RESOLUTION.md` plus the updated validation matrix are the specific authoritative refinement of older generic plan language.

## Closed stages

- M1: PASS.
- M2: PASS.
- M3: PASS, including whole-line OO, Ref Count/Shadow Ref, merge/wakeup, causal HOL validation, and sector S01-S09.

Do not redo closed work unless an actual M4 regression is found.

## M4 current source limitation

The frozen PTX frontend cannot create `FENCE_OP` / proxy-fence dynamic state. `membar` is distinct and regular dynamic fence is unsupported. Therefore do not implement or substitute fence semantics merely to satisfy the old F01-F03 end-to-end tests.

The accepted disposition is:

- F00A-F00D are active HARD source-domain gates;
- F01-F03 are `SOURCE_UNREACHABLE_NA` for this source anchor after F00A-F00D close;
- accepted workload triplets must have identical source-reachable FENCE_OP counts, expected zero for the frozen source;
- discovery of a real source-backed FENCE_OP producer reopens the fence gate and requires STOP/review.

## Immediate priority

1. close F00A-F00D and record F01-F03 disposition;
2. close remaining Store/Atomic/bypass and refined mixed-operation HARD tests;
3. finalize workload manifest;
4. run/validate the required representative compute workload set;
5. close parsers/CSV/invariants/provenance/hygiene;
6. create `review_packs/M4_COMPUTE_BRINGUP/`;
7. update `LATEST_REPORT.md` to `READY_FOR_M5_REVIEW`;
8. push and STOP.

## Continuation policy

Do not stop merely for a checkpoint commit, individual test PASS, build PASS, workload PASS, or intermediate report. Commit/push safe semantic checkpoints when useful and continue toward M4 closeout.

STOP on an active HARD failure, source-reachable semantic ambiguity requiring human judgment, regression of a closed stage, need to change frozen M0 semantics, or final `READY_FOR_M5_REVIEW`.

Do not begin M5.
