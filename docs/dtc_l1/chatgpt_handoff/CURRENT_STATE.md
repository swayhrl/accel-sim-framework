# DTC-L1 Current State

Last coordination update: 2026-09-04

Status: **M1-M4 VALIDATED; M5.0A PASS; M5.0B R5DV VALIDATION ACTIVE; POST-COMPUTE GRAPHICS CONTINUATION AUTHORIZED**

## Validated anchors

M1-M4 remain frozen validated infrastructure:

- Core final: `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0` at `cdeec769fd0c1be12b45d58536ecb81074d4b415`.
- Framework final: `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0` at `56369da33dc5f48fc9ac071fd122fde4b35bd8c9`.

Active compute M5 branches:

- Core `swayhrl/gpgpu-sim:hrl/decoupled-l1-m5-v0`.
- Framework `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m5-v0`.

After compute M5.6, create isolated graphics branches from exact compute-freeze heads:

- Core `hrl/decoupled-l1-m5-graphics-v0`;
- Framework `hrl/decoupled-l1-exp-m5-graphics-v0`.

## Active authority

1. `docs/dtc_l1/m5/M5_V1_APPROVAL.md`
2. `docs/dtc_l1/m5/M5_DIRTY_VICTIM_POLICY_RESOLUTION.md`
3. `docs/dtc_l1/m5/M5_V2_GRAPHICS_CONTINUATION_APPROVAL.md`
4. `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md`
5. `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`
6. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`
7. `docs/dtc_l1/m5/M5_GRAPHICS_PREP.md`
8. `docs/dtc_l1/m5/M5_GRAPHICS_POST_COMPUTE_PLAN.md`
9. `docs/dtc_l1/m5/M5_GRAPHICS_HANDOFF_CONTRACT.md`
10. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`
11. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`

## Research objective

M5 is a mechanism/trend reproduction, not numerical fitting to thesis speedup values.

Causal target:

`Base structural limits -> constrained live misses -> DTC removes limits -> concurrency/latency hiding changes -> performance effect`.

Weak/negative results require source-backed classification rather than tuning.

## Frozen compute definitions

### Figure 4.5

- PAPER_BASE: conventional 16 KiB L1, 128B, 4-way, PIB=8, MSHR=32.
- PAPER_IO: 16 KiB logical Tag + 80 KiB physical Cacheline Array, PIB=256.
- PAPER_OO: 16 KiB logical Tag + 80 KiB physical Cacheline Array, PIB=128.

### Figure 4.7

Live miss = new-miss lower-request commit through final lower response. Primary metric = per-SM cycle average.

### Figure 4.2

Formal structural categories: PIB full, true Tag+Cacheline allocation failure, MSHR capacity/merge, Miss Queue/lower capacity. Tag-bank arbitration is diagnostic.

### Dirty-victim policy

All paper-facing formal configs explicitly use:

`-gpgpu_l1_cache_write_ratio 0`

Preserve write-through/cache-allocation/LRU/MSHR/scoreboard semantics otherwise. Ratio 25 is diagnostic platform policy only.

## Current stage — M5.0B / R5DV

M5.0A is PASS.

M5-T005's prior 16 KiB ratio-25 dirty-set deadlock researcher decision is resolved. Ratio-zero config and directed dirty-victim regression are active/validated according to the latest Codex evidence. Canonical SpMV LEGACY/PAPER_BASE ratio-zero completion/output checks remain the closure gate before M5-T005 can be marked CLOSED.

After R5DV closes, resume remaining M5.0B work without redoing valid provenance checkpoints.

## Compute progression

`M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`

M5.6 PASS produces a frozen compute result set and `M5_6_TO_GRAPHICS.md` handoff. It is no longer the persistent Goal terminal state.

## Graphics continuation after compute

Post-compute sequence is now authorized:

`M5.7 Graphics Provenance -> M5.8 Graphics Path Recovery -> M5.9 Graphics Infrastructure -> M5.10 Graphics Fidelity Pilot -> M5.11 Five-Scene Formal Graphics -> M5.12 Full Synthesis`

The existing G1 classification `UNAVAILABLE_WITH_CURRENT_INFRA` remains valid for the current ready-made infrastructure, but post-compute M5.8 must perform deeper source/artifact recovery before treating graphics as scientifically unavailable.

Valid final M5 states:

- `M5_FULL_REPRO_READY_FOR_REVIEW`; or
- `M5_COMPUTE_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW` after exhaustive source-backed graphics path recovery fails.

A memory proxy can be supplemental only and cannot be used as paper graphics reproduction.

`GM-ALL-PAPER` requires all 15 source-backed/correctness-clean workloads plus an explicit compute/graphics performance-metric comparability proof.

## Problem behavior

Ordinary workload/build/assertion/parser/counter/timeout/performance/graphics-integration issues are resolve-in-goal. Diagnose, repair/reconstruct, regress, invalidate stale evidence as needed, and continue.

Pause only at a genuine researcher-decision boundary or a final M5 review state.

## Scope boundary

Figure 4.6 fresh area/synthesis reproduction is outside M5. If required, treat it as a separately authorized M6 track.
