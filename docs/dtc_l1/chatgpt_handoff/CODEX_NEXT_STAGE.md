# CODEX_NEXT_STAGE

## Status

**ACTIVE — M4 COMPLETION-ACCOUNTING RECOVERY AUTHORIZED; RESUME M4 ONLY AFTER RECOVERY PASS**

M1, M2, and M3 are closed PASS. M4 correctly stopped on a new source-reachable correctness failure exposed by PolyBench 2DConv. The active blocker is now DTC cacheable-load completion accounting, not PTX fence reachability.

Primary recovery specification:

`docs/dtc_l1/goal/M4_COMPLETION_ACCOUNTING_RECOVERY.md`

Existing fence/source-reachability specification remains valid but is temporarily downstream of this blocker:

`docs/dtc_l1/goal/M4_FENCE_REACHABILITY_RESOLUTION.md`

For the active recovery, `M4_COMPLETION_ACCOUNTING_RECOVERY.md` is the specific authoritative refinement of older generic M4 continuation language.

## Active branches

Core:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0`

Framework:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0`

M0 branches remain read-only anchors.

## Closed validated stages

- `M1_FOUNDATION`: PASS.
- `M2_IO_READ`: PASS; dedicated IO request/response path, no-MSHR proof, I01-I15 and review pack closed.
- `M3_OO_SECTOR`: PASS; whole-line OO, Ref Count/Shadow Ref, merge/wakeup, active reclamation, O01-O13, causal HOL, and S01-S09 closed.

Do not redo or weaken M1-M3 unless the active recovery proves an actual regression.

## Current HARD failure

Failure evidence:

`docs/dtc_l1/implementation/M4_COMPUTE_BRINGUP_FAILURE.md`

Recorded checkpoints:

- Core: `56a9230e4a538b69a30673ebdf66c42526fb324a`
- Framework: `5f674edccdf48dc768155fbd008723dc8a126b31`

PolyBench 2DConv under identical workload/input/unrelated configuration produced:

- `PAPER_IO`: assertion in `dtc_l1_io_complete_instruction`, `pending >= dependencies`;
- `PAPER_OO`: assertion in `dtc_l1_oo_complete_instruction`, same invariant;
- `PAPER_BASE`: 240-second diagnostic timeout, not yet classified as deadlock.

The IO/OO failure is source reachable and blocks all remaining M4 acceptance and M5.

## Required read order before resuming Goal

Framework:

1. `AGENTS.md`
2. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
4. this file
5. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`
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

## Immediate execution objective

Execute `M4_COMPLETION_ACCOUNTING_RECOVERY.md` in order:

- `R4C.0`: deterministic pre-fix localization of the first failing UID/PC/cardinality;
- `R4C.1`: add per-instruction DTC dependency ownership ledger/checker;
- `R4C.2`: trace pending-write mutation provenance and classify root cause A/B/C/D/E;
- `R4C.3`: apply only the minimal source-backed repair;
- `R4C.4`: add permanent cardinality/exactly-once regressions;
- `R4C.5`: rerun exact 2DConv PAPER_IO/PAPER_OO and require clean completion/accounting;
- `R4C.6`: rerun closed-stage regression subset including CTests, IO/OO/sector VecAdd and LEGACY neutrality smoke;
- `R4C.7`: separately classify the PAPER_BASE timeout using progress evidence;
- `R4C.8`: only after all recovery HARD items close, resume the remaining M4 Goal automatically.

## Critical repair constraints

Do NOT:

- weaken/remove `pending >= dependencies` or other accounting assertions to make the workload run;
- clamp `dependencies` to the current aggregate pending value;
- force pending state to zero;
- release scoreboard registers without exactly-once source-backed dependency closure;
- change 128B DTC dependency granularity merely to match the failing number;
- reintroduce conventional L1D MSHR/fill as the hidden IO/OO read backend;
- alter L2/NoC/DRAM;
- implement PTX fence frontend support or map `membar` to `FENCE_OP`;
- begin M5.

## Progression authorization

If and only if R4C.0-R4C.7 all pass/close without an active HARD failure:

1. create/update `implementation/M4_COMPLETION_ACCOUNTING_RECOVERY_EVIDENCE.md`;
2. commit/push safe semantic state with explicit-path staging;
3. update Codex-owned `LATEST_REPORT.md` to recovery PASS / M4 in progress;
4. resume F00/Fence-source-domain disposition plus W/A/BP/MIX/workload-manifest/compute-bring-up/parser/CSV/hygiene automatically;
5. create/push `review_packs/M4_COMPUTE_BRINGUP/` only after every active M4 HARD gate passes;
6. set `LATEST_REPORT.md` to `READY_FOR_M5_REVIEW`, push, and STOP.

No new human authorization is required after a full recovery PASS.

## Goal behavior

Ordinary diagnostic checkpoints are not stop conditions. During recovery, preserve compact evidence at safe checkpoints and continue automatically unless a HARD stop condition occurs.

STOP on:

- irreproducible/ambiguous dependency ownership that cannot be source-resolved;
- need to change frozen M0 semantics;
- scoreboard correctness requiring an unverified shortcut;
- closed M1-M3 regression;
- 2DConv IO/OO remaining incorrect after the minimal repair;
- PAPER_BASE proven unexpectedly no-progress/deadlocked;
- any new active M4 HARD failure;
- final `READY_FOR_M5_REVIEW`.

Do not begin M5.
