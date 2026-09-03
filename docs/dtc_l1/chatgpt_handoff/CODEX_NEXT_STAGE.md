# CODEX_NEXT_STAGE

## Status

**ACTIVE — RESUME M4 UNDER VERIFIED SOURCE-REACHABILITY BOUNDARY**

M1, M2, and M3 are closed PASS. M4 correctly stopped after proving that the frozen current PTX frontend cannot generate the existing dynamic proxy-fence path. That finding is now an accepted, explicitly documented source limitation rather than a requirement to implement unrelated PTX frontend semantics.

Primary Goal contract:

`docs/dtc_l1/chatgpt_handoff/GOAL_START.md`

Specific M4 fence disposition:

`docs/dtc_l1/goal/M4_FENCE_REACHABILITY_RESOLUTION.md`

For M4 fence-related requirements only, the resolution file and the updated `VALIDATION_ACCEPTANCE_MATRIX.md` are authoritative refinements of older generic M4 plan language.

## Active branches

Core:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0`

Framework:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0`

M0 branches remain read-only anchors.

## Closed validated stages

- `M1_FOUNDATION`: PASS; review pack exists.
- `M2_IO_READ`: PASS; review pack exists.
- `M3_OO_SECTOR`: PASS; whole-line OO, Ref Count/Shadow Ref, merge/wakeup, active reclamation, IO-vs-OO causal HOL, and sector S01-S09 are closed.

Do not redo closed-stage work unless M4 reveals a real regression.

## Current M4 source-backed state

Core M4 checkpoint before this specification refinement: `5aea1cbb41575e31c0c61f97dfc6d77cc15a3c9f`.

Framework fence-evidence checkpoint: `b18eca499b6fe92569070c4ebebe8d7374f6f68a`.

`implementation/M4_MEMORY_OP_SEMANTICS.md` establishes:

- Store lifecycle observation without changing the configured source write/cache policy;
- Atomic lifecycle observation without merging/loss of side effects;
- architectural bypass preservation;
- current PTX frontend cannot produce `FENCE_OP` / proxy-fence state;
- PTX `membar` is distinct and must not be substituted;
- regular dynamic fence behavior is explicitly unsupported.

The source limitation is not permission to invent new parser/decode semantics.

## Required read order before resuming Goal

Framework:

1. `AGENTS.md`
2. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
4. this file
5. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`
6. `docs/dtc_l1/goal/M4_FENCE_REACHABILITY_RESOLUTION.md`
7. `docs/dtc_l1/implementation/M4_MEMORY_OP_SEMANTICS.md`
8. `docs/dtc_l1/goal/VALIDATION_ACCEPTANCE_MATRIX.md`
9. `docs/dtc_l1/goal/M1_M4_GOAL_PLAN.md`
10. `docs/dtc_l1/goal/COUNTER_INVARIANT_SPEC.md`

Core:

11. `AGENTS.md`
12. `docs/dtc_l1/DTC_L1_SPEC.md`

## Immediate execution objective

Resume M4 from the existing safe checkpoint. Do not add PTX fence support.

1. Record `F00A FenceReachabilityAudit` PASS from the existing source evidence.
2. Close `F00B NoSilentSubstitution`, `F00C CurrentDomainFenceAccounting`, and `F00D DynamicProxyPathPreserved`.
3. Classify legacy end-to-end `F01-F03` as `SOURCE_UNREACHABLE_NA` for this frozen source anchor; do not call them PASS and do not substitute `membar`.
4. Close W01-W04, A01-A04, BP01-BP02, and refined source-reachable MIX01.
5. Finalize `implementation/WORKLOAD_MANIFEST.md`.
6. Run at least five provenance-resolved representative Chapter-4 compute workloads under PAPER_BASE/PAPER_IO/PAPER_OO with identical input/unrelated configuration.
7. For each accepted triplet, require identical dynamic instruction/Load/Store/Atomic/source-reachable-FENCE_OP counts, clean invariants, provenance, and accounting. Current-source FENCE_OP is expected to be zero; a real producer requires STOP/review.
8. Close required CSV/parser outputs and hygiene.
9. Create/push `review_packs/M4_COMPUTE_BRINGUP/` only after every active M4 HARD gate passes.
10. Set `LATEST_REPORT.md` to `READY_FOR_M5_REVIEW`, push, and STOP.

## Explicit Goal behavior

Ordinary checkpoints are not stop conditions. Continue automatically through M4 validation/workload bring-up when tests pass.

A verified unsupported source feature is not repaired by inventing semantics. Stay inside the frozen source-reachable domain and report limitations explicitly.

## HARD stop conditions

STOP only when:

- an **active** HARD gate fails reproducibly;
- a source-reachable correctness/architecture ambiguity cannot be resolved without guessing;
- a real PTX/source path unexpectedly produces `FENCE_OP` and therefore reopens fence ordering validation;
- a fix would require changing frozen M0 DTC semantics;
- M1/M2/M3 closed behavior regresses;
- unauthorized L2/NoC/DRAM redesign is required;
- M4 reaches `READY_FOR_M5_REVIEW`.

## Forbidden scope

Do NOT:

- implement `fence` lexer/parser/static-decode support in this goal;
- map `membar` to `FENCE_OP` or proxy fence;
- force `set_proxy_fence()`/`set_fence_proxy_kind()` on ordinary instructions;
- bypass the source's unsupported regular-fence assertion to make a test run;
- modify M0 anchors;
- tune to thesis speedup values;
- begin M5.

## Final completion condition

The persistent Goal completes when M4 passes under the explicitly documented frozen-source reachability domain, the M4 review pack is complete, accepted Base/IO/OO workload triplets close all active invariants/provenance, both branches are pushed/clean, `LATEST_REPORT.md` says `READY_FOR_M5_REVIEW`, and M5 has not started.
