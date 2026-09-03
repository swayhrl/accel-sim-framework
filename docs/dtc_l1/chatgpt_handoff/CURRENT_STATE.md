# DTC-L1 Current State

Last coordination update: 2026-09-04

Status: **M1-M4 VALIDATED; M5.0A PASS; M5.0B/R5DV ACTIVE; EXTENDED-20 APPROVED; GRAPHICS M5.7/M5.8 PARALLEL RESEARCH AUTHORIZED**

## Validated anchors

M1-M4 remain frozen validated infrastructure:

- Core final M1-M4: `cdeec769fd0c1be12b45d58536ecb81074d4b415`.
- Framework final M1-M4: `56369da33dc5f48fc9ac071fd122fde4b35bd8c9`.

Active M5 compute branches:

- Core `swayhrl/gpgpu-sim:hrl/decoupled-l1-m5-v0`;
- Framework `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m5-v0`.

## Current authority

Read current M5 authority in this order:

1. `docs/dtc_l1/m5/M5_V3_PARALLEL_TRACKS_APPROVAL.md`
2. `docs/dtc_l1/m5/M5_V1_APPROVAL.md`
3. `docs/dtc_l1/m5/M5_DIRTY_VICTIM_POLICY_RESOLUTION.md`
4. `docs/dtc_l1/m5/M5_EXTENDED20_APPROVAL.md`
5. `docs/dtc_l1/m5/M5_EXTENDED20_FORMAL_MATRIX.md`
6. `docs/dtc_l1/m5/M5_PARALLEL_BATCH_POLICY.md`
7. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`
8. `docs/dtc_l1/m5/M5_EXTENDED20_HANDOFF_CONTRACT.md`
9. `docs/dtc_l1/m5/M5_BRANCH_OWNERSHIP.md`
10. `docs/dtc_l1/m5/M5_GRAPHICS_INDEPENDENT_WINDOW_HANDOFF.md`
11. `docs/dtc_l1/m5/M5_GRAPHICS_POST_COMPUTE_PLAN.md`
12. `docs/dtc_l1/m5/M5_GRAPHICS_HANDOFF_CONTRACT.md`
13. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`
14. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`

Older M5 v2 graphics sequencing that required all graphics research to wait until M5.6 is superseded by v3. Scientific no-proxy/comparability constraints remain.

## Research objective

M5 is mechanism/trend reproduction, not numerical fitting to thesis speedups.

`Base structural limits -> constrained live misses -> DTC removes limits -> concurrency/latency hiding changes -> performance effect`

Weak/negative results require causal classification rather than tuning.

## Frozen compute definitions

### Main paper configuration

- PAPER_BASE: conventional 16 KiB L1, 128B line, 4-way, PIB=8, MSHR=32.
- PAPER_IO: 16 KiB logical Tag + 80 KiB physical Cacheline Array, PIB=256.
- PAPER_OO: 16 KiB logical Tag + 80 KiB physical Cacheline Array, PIB=128.

### Dirty-victim policy

All paper-facing/formal M5 configs explicitly use:

`-gpgpu_l1_cache_write_ratio 0`

Ratio 25 remains diagnostic platform policy only.

### Figure 4.7

Live miss = new-miss lower-request commit through final lower response; primary metric = per-SM cycle average.

### Figure 4.2

Formal categories: PIB full, true Tag+Cacheline allocation failure, MSHR capacity/merge, Miss Queue/lower capacity. Tag-bank arbitration remains diagnostic.

## Current Paper-10 stage — M5.0B / R5DV

M5.0A is PASS.

M5-T005's ratio-25 dirty-set deadlock decision is resolved by explicit ratio 0. Directed dirty-victim regression, Release build, DTC CTests, four-mode VecAdd and mixed Store/Atomic/.cg sentinels have passed according to latest Codex evidence. Canonical SpMV medium LEGACY/PAPER_BASE ratio-zero completion/output validation remains the R5DV closure gate.

After R5DV closes, resume remaining M5.0B work without redoing valid provenance checkpoints.

Paper progression:

`M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`

## Extended-20 state

Selection branch:

`hrl/decoupled-l1-exp-m5-extended20-select-v0`

Reviewed selection commit:

`d43b6eec93f68efa94057f34ffa699463b53e6a6`

Independent review verdict: **APPROVED**.

Approved set: 20 primary workloads + 5 ranked alternates as recorded in `M5_EXTENDED20_APPROVAL.md`.

One metadata correction is required during E1: CUDA SDK BlackScholes must be described as Black-Scholes option pricing, not assumed Monte Carlo.

Extended progression:

`M5.E0 selection approved -> M5.E1 formalization -> M5.E2 60-run Base/IO/OO wave -> M5.E3 synthesis`

E1 may prepare source/build/input identity early. E2 begins only after M5.2 freezes the common formal anchor.

Extended jobs must use the resource-aware worker pool in `M5_PARALLEL_BATCH_POLICY.md`; unnecessary one-by-one execution is forbidden.

## Graphics state

Existing audit: ready-made current infrastructure is `UNAVAILABLE_WITH_CURRENT_INFRA` for direct/source-faithful graphics execution. This is starting evidence, not the terminal M5.8 conclusion.

A separate Framework-only graphics-research branch/window is authorized now for:

`M5.7 provenance -> M5.8 path recovery`

Target branch:

`hrl/decoupled-l1-exp-m5-graphics-research-v0`

It may not modify active compute Framework/Core or start M5.9 Core integration.

M5.9+ waits for `M5.COMPUTE_FREEZE`.

## Compute-freeze join barrier

M5.6 alone does not freeze compute.

`M5.COMPUTE_FREEZE` requires:

- Paper M5.6 PASS;
- Extended M5.E3 PASS;
- no unresolved correctness/fidelity issue;
- active compute branches pushed/clean.

Then record immutable `COMPUTE_FREEZE_CORE_SHA` and `COMPUTE_FREEZE_FRAMEWORK_SHA` and create fresh graphics integration branches from those exact SHAs.

## Final M5 dependency

M5.12 requires:

- Paper-10 through M5.6;
- Extended-20 through M5.E3;
- compute freeze;
- graphics M5.11 PASS or exhaustive M5.8 source-backed-unavailable evidence;
- no unresolved correctness/fidelity issue.

Reporting groups remain distinct:

- `GM-PAPER10` / `GM-GP`;
- `GM-EXTENDED20`;
- `GM-ALL-COMPUTE30` supplemental;
- `GM-GRAPHICS` if source-backed;
- `GM-ALL-PAPER` only original ten compute + five graphics with comparability proof.

## Final states

- `M5_FULL_REPRO_READY_FOR_REVIEW`; or
- `M5_COMPUTE30_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`.

Figure 4.6 fresh area/synthesis is outside M5 and remains a separate M6 decision.
