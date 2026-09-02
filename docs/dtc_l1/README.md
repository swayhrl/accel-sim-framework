# Decoupled-Tag L1 Reproduction Project

This directory is the cross-repository coordination root for reproducing the thesis Decoupled-Tag L1 cache in Accel-Sim/GPGPU-Sim.

## Repositories and branches

### Framework / coordination

- repository: `swayhrl/accel-sim-framework`
- branch: `hrl/decoupled-l1-exp-v0`
- official base: `accel-sim/accel-sim-framework:dev`
- official base SHA: `d930ad6d02c09bb56867132583735aba0389cff4`

### Core simulator

- repository: `swayhrl/gpgpu-sim`
- branch: `hrl/decoupled-l1-v0`
- official base: `accel-sim/gpgpu-sim_distribution:dev`
- official base SHA: `91880c53383d5a6a6742bfb1be2c5f34e39c7871`

Core architecture specification:

`docs/dtc_l1/DTC_L1_SPEC.md` in the core repository.

## Coordination layout

```text
docs/dtc_l1/
├── chatgpt_handoff/     # research decisions and active stage specification
├── codex_handoff/       # Codex execution report entry point
└── review_packs/        # stage-by-stage review evidence
```

Ownership:

- `chatgpt_handoff/`: ChatGPT-owned;
- `codex_handoff/`: Codex-owned after bootstrap;
- `review_packs/`: Codex-generated evidence.

## Current status

M0 architecture/model decisions are frozen. The current stage is intentionally HOLD until M1-M3 implementation goals are planned and written into `CODEX_NEXT_STAGE.md`.
