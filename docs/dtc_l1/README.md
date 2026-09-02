# Decoupled-Tag L1 Reproduction Project

This directory is the cross-repository coordination root for reproducing the thesis Decoupled-Tag L1 cache in Accel-Sim/GPGPU-Sim.

## Repositories and branches

### Frozen M0 anchors

Framework:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-v0`

Core:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-v0`

These remain read-only architecture/design anchors.

### Active M1-M4 Goal branches

Framework / coordination / experiments:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0`

Core simulator:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0`

Official source anchors remain:

- framework: `accel-sim/accel-sim-framework:dev` at `d930ad6d02c09bb56867132583735aba0389cff4`;
- core: `accel-sim/gpgpu-sim_distribution:dev` at `91880c53383d5a6a6742bfb1be2c5f34e39c7871`.

Core architecture specification:

`docs/dtc_l1/DTC_L1_SPEC.md` in the core repository.

## Coordination layout

```text
docs/dtc_l1/
├── chatgpt_handoff/     # ChatGPT-owned state and executable authorization
├── goal/                # ChatGPT-owned M1-M4 execution / counters / validation specs
├── implementation/      # Codex-owned source-backed implementation records
├── codex_handoff/       # Codex execution report entry point
└── review_packs/        # stage-by-stage review evidence
```

## Current status

M0 is frozen. A continuous Goal-mode execution from M1 through M4 is authorized on the active goal branches, with HARD validation gates between each major stage. Codex may continue automatically only after a stage fully passes; any hard failure or unresolved semantic ambiguity requires STOP.

M5 paper-result reproduction and later research experiments remain unauthorized until review of M1-M4.
