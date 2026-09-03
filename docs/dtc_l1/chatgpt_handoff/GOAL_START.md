# DTC-L1 M5 Explicit Goal Launch Contract

Status: **ACTIVE — M5 v2 CONTINUOUS COMPUTE + POST-COMPUTE GRAPHICS GOAL**

This is the durable objective for Codex Goal mode.

Primary authority:

- `docs/dtc_l1/m5/M5_V1_APPROVAL.md` — compute experiment contract;
- `docs/dtc_l1/m5/M5_DIRTY_VICTIM_POLICY_RESOLUTION.md` — approved M5-T005 refinement;
- `docs/dtc_l1/m5/M5_V2_GRAPHICS_CONTINUATION_APPROVAL.md` — extends the Goal after M5.6;
- `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md`;
- `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`;
- `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`;
- `docs/dtc_l1/m5/M5_GRAPHICS_PREP.md`;
- `docs/dtc_l1/m5/M5_GRAPHICS_POST_COMPUTE_PLAN.md`;
- `docs/dtc_l1/m5/M5_GRAPHICS_HANDOFF_CONTRACT.md`.

## Persistent Goal

First complete the source-faithful ten-compute DTC reproduction, then freeze that result set and continue into a source-backed graphics reproduction attempt for the five thesis glmark2 workloads.

Scientific target:

`traditional L1 structural limits -> fewer live concurrent misses -> DTC removes structural limits -> more concurrency / better latency hiding -> performance effect`.

Exact thesis speedups are references, not pass thresholds.

## Terminal states

Successful full performance/mechanism reproduction:

`M5_FULL_REPRO_READY_FOR_REVIEW`

If exhaustive graphics recovery proves no source-backed graphics path can be established without inventing semantics:

`M5_COMPUTE_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`

`M5_COMPUTE_READY_FOR_REVIEW` is no longer a Goal terminal state. It is the M5.6 compute freeze/checkpoint before graphics continuation.

Figure 4.6 area/synthesis is not part of this Goal and does not start automatically.

## Active compute branches

Core:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m5-v0`

Framework:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m5-v0`

Validated parents remain the M1-M4 final anchors. Do not write M5 work back to them.

After M5.6, create isolated graphics branches from the exact compute-freeze heads:

- Core `hrl/decoupled-l1-m5-graphics-v0`;
- Framework `hrl/decoupled-l1-exp-m5-graphics-v0`.

Do not contaminate frozen compute FORMAL evidence with later graphics-infrastructure changes.

## Mandatory read order

Framework:

1. `AGENTS.md`
2. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/dtc_l1/m5/M5_V1_APPROVAL.md`
4. `docs/dtc_l1/m5/M5_DIRTY_VICTIM_POLICY_RESOLUTION.md`
5. `docs/dtc_l1/m5/M5_V2_GRAPHICS_CONTINUATION_APPROVAL.md`
6. `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md`
7. `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`
8. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`
9. `docs/dtc_l1/m5/M5_GRAPHICS_PREP.md`
10. `docs/dtc_l1/m5/M5_GRAPHICS_POST_COMPUTE_PLAN.md`
11. `docs/dtc_l1/m5/M5_GRAPHICS_HANDOFF_CONTRACT.md`
12. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`
13. this file
14. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
15. `docs/dtc_l1/implementation/M5_ISSUE_LOG.md`
16. final M4 review pack as regression context

Core:

17. `AGENTS.md`
18. `docs/dtc_l1/DTC_L1_SPEC.md`

## Researcher-frozen compute definitions

### Main configuration

- PAPER_BASE: conventional 16 KiB L1, 128B, 4-way, PIB=8, MSHR=32.
- PAPER_IO: 16 KiB logical Tag capacity + 80 KiB physical Cacheline Array, PIB=256.
- PAPER_OO: 16 KiB logical Tag capacity + 80 KiB physical Cacheline Array, PIB=128.

### Conventional-L1 dirty-victim policy

All paper-facing formal configs explicitly use:

`-gpgpu_l1_cache_write_ratio 0`.

Keep write-through and all other frozen cache semantics unchanged. Ratio 25 is diagnostic only.

### Figure 4.7

Common live miss = new-miss lower-request commit through final lower response. Primary plotted metric = per-SM cycle average.

### Figure 4.2

Paper-facing categories = PIB full, true Tag+Cacheline allocation failure, MSHR capacity/merge, Miss Queue/lower-capacity. Tag-bank arbitration is separate diagnostic evidence.

## Current compute resume point

M5.0A is PASS. M5.0B is active.

Close M5-T005 through `M5_DIRTY_VICTIM_POLICY_RESOLUTION.md`, then resume unresolved workload recovery without redoing valid checkpoints.

Existing diagnostics may continue if host resources permit.

## Authorized compute sequence

Continue automatically:

`M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`

At every PASS boundary:

1. satisfy acceptance criteria;
2. produce required handoff/review evidence;
3. run strict parser/counter sanity;
4. explicit-path commit/push;
5. update `codex_handoff/LATEST_REPORT.md`;
6. begin the next substage without asking for confirmation.

## M5.6 compute-to-graphics transition

When M5.6 passes:

1. finish/freeze the compute review pack;
2. record `COMPUTE_FREEZE_CORE_SHA` and `COMPUTE_FREEZE_FRAMEWORK_SHA`;
3. create `m5/handoffs/M5_6_TO_GRAPHICS.md`;
4. verify compute branches pushed/clean;
5. create isolated graphics branches from those exact SHAs;
6. **continue automatically** into M5.7. Do not stop merely to report compute completion.

## Authorized graphics sequence

Follow `M5_GRAPHICS_POST_COMPUTE_PLAN.md` and `M5_GRAPHICS_HANDOFF_CONTRACT.md`:

`M5.7 Graphics Provenance -> M5.8 Graphics Path Recovery -> M5.9 Graphics Infrastructure -> M5.10 Graphics Fidelity Pilot -> M5.11 Five-Scene Formal Graphics -> M5.12 Full Synthesis`

The existing G1 `UNAVAILABLE_WITH_CURRENT_INFRA` result is valid current-infrastructure evidence but not the terminal conclusion. M5.8 must perform deeper recovery of original thesis/project artifacts, historical graphics-enabled simulator paths, defensible direct integration, and source-backed trace/replay options before declaring graphics unavailable.

A calibrated memory proxy may be supplemental only. It cannot be used for paper graphics bars or `GM-ALL-PAPER`.

If M5.8 exhaustively proves no source-backed path is possible, skip formal graphics execution and proceed to M5.12 negative-evidence closure.

## Graphics aggregation rule

Figure 4.9 remains compute-only.

`GM-ALL-PAPER` is permitted only if:

- all ten compute and all five graphics workloads are source-backed/correctness-clean;
- graphics formal path is DIRECT_SOURCE_BACKED or TRACE_SOURCE_BACKED;
- compute/graphics performance-metric comparability is explicitly proven.

Do not combine unrelated fields merely because both are called cycles.

## Problem-resolution behavior

Follow `M5_PROBLEM_RESOLUTION_POLICY.md` plus the graphics continuation plan.

Ordinary issues — missing workload/asset, build/PTX/shader failure, assertions, counter gaps, parser/integration bugs, timeout, poor speedup, absent expected pressure, platform bottlenecks, or repairable source-backed bugs — are solved inside the Goal.

A substantial performance difference caused by a fidelity correction is evidence to classify, not a target to tune away.

## Pause conditions

Pause only for a genuine researcher-decision boundary that cannot be source/thesis resolved without choosing different experiment meaning, a required change to frozen DTC/M0-M4 architecture semantics, a proposal to use a proxy as formal graphics reproduction, an irreducible compute/graphics comparability ambiguity for a combined claim, or one of the two final M5 review states.

## Forbidden

Do not:

- enlarge 16 KiB Base merely to bypass pressure;
- restore ratio 25 to paper-facing runs to change performance;
- invent a new dirty-victim fallback just to preserve the inherited heuristic;
- disable deadlock detection or weaken scoreboard/accounting assertions;
- tune architecture/input/downstream settings to thesis bars;
- substitute compute or graphics workloads silently;
- mix MODERN_OO_SECTOR into Figures 4.2-4.10;
- present a graphics memory proxy as direct paper reproduction;
- emit `GM-ALL-PAPER` without the cross-path comparability gate;
- start Figure 4.6 area/synthesis work without separate M6 authorization.
