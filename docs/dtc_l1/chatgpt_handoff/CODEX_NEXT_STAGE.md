# CODEX_NEXT_STAGE

## Status

**ACTIVE — CLOSE M5-T005, CONTINUE COMPUTE THROUGH M5.6, THEN CONTINUE GRAPHICS THROUGH M5.12**

The M5-T005 researcher-decision boundary is resolved by:

`docs/dtc_l1/m5/M5_DIRTY_VICTIM_POLICY_RESOLUTION.md`

The researcher has also authorized post-compute graphics continuation through:

- `docs/dtc_l1/m5/M5_V2_GRAPHICS_CONTINUATION_APPROVAL.md`
- `docs/dtc_l1/m5/M5_GRAPHICS_POST_COMPUTE_PLAN.md`
- `docs/dtc_l1/m5/M5_GRAPHICS_HANDOFF_CONTRACT.md`

M1-M4 remain closed PASS. M5.0A is closed PASS. Current work remains M5.0B/R5DV until canonical ratio-zero SpMV closes M5-T005.

## Active compute branches

Core:
- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m5-v0`

Framework:
- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m5-v0`

Do not modify validated M1-M4 branches.

## Immediate work — finish R5DV

Complete R5DV.0-R5DV.5 from `M5_DIRTY_VICTIM_POLICY_RESOLUTION.md`.

The formal paper-facing policy remains:

`-gpgpu_l1_cache_write_ratio 0`

for LEGACY/PAPER_BASE/PAPER_IO/PAPER_OO and all derived formal configs unless a later authorized sensitivity explicitly varies it.

Require canonical Parboil JDS SpMV medium LEGACY/PAPER_BASE to complete with correct output, no old dirty-set deadlock, and clean accounting. Close M5-T005 only after that evidence is complete.

Do not kill existing ratio-25 diagnostic jobs solely because they are non-formal.

## Continue compute automatically

After M5-T005 closes, resume the existing valid M5.0B checkpoint and execute:

`M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`

At each substage PASS:

1. close acceptance checks;
2. strict parser/counter sanity;
3. produce required handoff/review evidence;
4. explicit-path commit/push;
5. update `codex_handoff/LATEST_REPORT.md`;
6. continue automatically.

Do not stop at ordinary workload, implementation, instrumentation, timeout, or performance problems. Follow `M5_PROBLEM_RESOLUTION_POLICY.md`.

## M5.6 is now a freeze boundary, not terminal Goal state

When compute M5.6 passes:

1. create/finalize the compute review pack;
2. record immutable `COMPUTE_FREEZE_CORE_SHA` and `COMPUTE_FREEZE_FRAMEWORK_SHA`;
3. emit `docs/dtc_l1/m5/handoffs/M5_6_TO_GRAPHICS.md`;
4. push/clean both compute branches;
5. create graphics branches from the exact freeze heads:
   - Core `hrl/decoupled-l1-m5-graphics-v0`
   - Framework `hrl/decoupled-l1-exp-m5-graphics-v0`
6. continue automatically to M5.7.

Do not modify frozen compute results from the graphics branches.

## Post-compute graphics sequence

Execute:

`M5.7 -> M5.8 -> M5.9 -> M5.10 -> M5.11 -> M5.12`

### M5.7
Close provenance for all five thesis graphics workloads and exact/closest source-backed glmark2 scene, shader, model, texture, resolution, and invocation identities.

### M5.8
Treat the existing `UNAVAILABLE_WITH_CURRENT_INFRA` audit as starting evidence, then deeply recover possible source-backed execution paths in this order:

1. original thesis/project simulator/artifacts/traces;
2. historical graphics-enabled simulator/fork/artifacts;
3. real direct graphics frontend integration;
4. source-backed shader/request trace replay;
5. proxy only as supplemental non-formal work.

Do not declare graphics unavailable merely because the current ready-made path is absent. Exhaust the source-backed routes first.

If a DIRECT_SOURCE_BACKED or TRACE_SOURCE_BACKED path is established, continue M5.9.

If all source-backed routes are exhaustively ruled out, record `GRAPHICS_SOURCE_BACKED_UNAVAILABLE` and proceed to M5.12 negative-evidence closure rather than inventing a proxy.

### M5.9-M5.10
Integrate/validate the selected path and perform directed graphics-DTC tests plus representative Base/IO/OO pilots. Preserve texture/order/completion semantics and separate fixed-function traffic outside DTC scope.

### M5.11
Run all five source-backed graphics workloads for paper-facing Figure 4.2, 4.5, 4.7, 4.8 and 4.10 experiments. Figure 4.9 remains compute-only.

Do not emit `GM-ALL-PAPER` until compute/graphics performance metric comparability is explicitly proven.

### M5.12
Produce integrated compute+graphics causal synthesis and the final review pack.

## Final Goal terminal states

Successful graphics reproduction:

`M5_FULL_REPRO_READY_FOR_REVIEW`

Exhaustive source-backed graphics unavailability:

`M5_COMPUTE_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`

`M5_COMPUTE_READY_FOR_REVIEW` alone is no longer a stop condition.

## Pause conditions

Pause only at a genuine `RESEARCHER_DECISION_REQUIRED` boundary, including:

- the only source-correct next step changes frozen DTC/M0-M4 architecture semantics;
- irreducible scientific ambiguity requires choosing a different experiment meaning;
- formal graphics would require a proxy/approximation rather than a source-backed path;
- compute/graphics metric comparability is irreducibly ambiguous while attempting a combined claim;
- or one of the final M5 terminal review states is reached.

## Forbidden shortcuts

Do not:

- enlarge the formal 16 KiB Base L1 to bypass pressure;
- weaken deadlock, pending-write, scoreboard, or accounting assertions;
- change ratio 0 asymmetrically across paper-facing modes;
- tune inputs/architecture for target speedups;
- silently substitute algorithms/scenes;
- treat current graphics infeasibility as permission to use a compute proxy;
- mix MODERN_OO_SECTOR into paper Figures 4.2-4.10;
- start Figure 4.6 area/synthesis without separate M6 authorization.
