# Decoupled-Tag L1 Reproduction Project

This directory is the cross-repository coordination root for reproducing and evaluating the thesis Decoupled-Tag L1 cache in Accel-Sim/GPGPU-Sim.

## Repositories and branches

### Frozen M0 anchors

Framework:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-v0`

Core:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-v0`

These remain read-only architecture/design anchors.

### Validated M1-M4 parents

Framework:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0`
- final validated SHA `56369da33dc5f48fc9ac071fd122fde4b35bd8c9`

Core:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0`
- final validated SHA `cdeec769fd0c1be12b45d58536ecb81074d4b415`

### Active M5 branches

Framework / coordination / formal experiments:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m5-v0`

Core simulator / M5 instrumentation and fidelity repairs:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m5-v0`

Official source anchors remain:

- framework: `accel-sim/accel-sim-framework:dev` at `d930ad6d02c09bb56867132583735aba0389cff4`;
- core: `accel-sim/gpgpu-sim_distribution:dev` at `91880c53383d5a6a6742bfb1be2c5f34e39c7871`.

Core architecture specification:

`docs/dtc_l1/DTC_L1_SPEC.md` in the Core repository.

## M5 authority

M5 v1 is approved and ACTIVE.

Read:

1. `m5/M5_V1_APPROVAL.md`;
2. `m5/M5_EXPERIMENT_MATRIX.md`;
3. `m5/M5_PROBLEM_RESOLUTION_POLICY.md`;
4. `m5/M5_HANDOFF_CONTRACT.md`;
5. `m5/M5_GRAPHICS_PREP.md`;
6. `chatgpt_handoff/CURRENT_STATE.md` and `GOAL_START.md`.

`M5_V1_APPROVAL.md` supersedes the stale planning banner inside the long matrix; the matrix body is the approved v1 detailed plan.

## Coordination layout

```text
docs/dtc_l1/
├── chatgpt_handoff/     # ChatGPT-owned current state and Goal authorization
├── goal/                # historical M1-M4 specs/recovery contracts
├── m5/                  # active M5 experiment matrix/policies/handoffs
├── implementation/      # Codex-owned source/workload/issue records
├── codex_handoff/       # mutable Codex execution report
└── review_packs/        # stage-by-stage independent-review evidence
```

## Current status

M0 is frozen. M1-M4 are complete and validated. M5 v1 is authorized from M5.0A through M5.6 on the dedicated M5 branches.

The compute Goal is mechanism/trend reproduction: establish whether DTC removes traditional L1 structural constraints, increases common live concurrent misses/latency hiding, and how this translates into performance. Exact thesis speedups are references, not pass thresholds.

Ordinary workload/build/assertion/instrumentation/performance problems are solved in Goal mode under `M5_PROBLEM_RESOLUTION_POLICY.md`; they are not automatic human-stop boundaries.

Terminal compute state:

`M5_COMPUTE_READY_FOR_REVIEW`.

Graphics G0-G2 preparation is authorized in parallel but must not block compute M5. Post-review graphics formal aggregation, Figure 4.6 area claims, sector-extension comparisons, and M5.7+ supplemental studies require later authorization.
