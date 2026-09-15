# AWMA Simulation Analysis — Planning Handoff

Status: **PLANNED / NOT ACTIVE while the current Qwen Decode/analysis Goal is running on 174-new.**

Project: **AI Workload Memory Analysis (AWMA)**.

This directory freezes the Simulation Analysis mainline so it can start immediately when 174-new is free, without disturbing the parallel Native Characterization line.

## Scope

Simulation Analysis is the modeled/counterfactual evidence plane of AWMA:

```text
simulator-compatible trace
        ↓
qualified Accel-Sim/GPGPU-Sim runtime
        ↓
baseline TLB/PTW/cache/memory-hierarchy characterization
        ↓
mechanism variants
        ↓
Simulation Evidence datasets
```

It is distinct from, but identity-aligned with, Native Characterization:

```text
Native Characterization
  = what the real GPU actually did

Simulation Analysis
  = what would happen under modeled architecture changes
```

Do not merge the scientific meanings of the two evidence planes.

## Read order

1. `CURRENT_STATE.md`
2. `SIMULATION_ANALYSIS_ARCHITECTURE.md`
3. `RUNTIME_BASELINE_AND_CALIBRATION_PLAN.md`
4. `SIMULATOR_INPUT_AND_CAPTURE_PLAN.md`
5. `SIMULATION_METRICS_AND_DATA_MODEL.md`
6. `EXECUTION_ROADMAP.md`
7. `CODEX_NEXT_STAGE_174NEW_SIMULATION_FOUNDATION.md`
8. `ACCEPTANCE_AND_REVIEW_REQUIREMENTS.md`

## Important execution boundary

The executable Goal in this directory is **prepared but not active yet**.

Do not interrupt an existing Qwen Decode/analysis Goal merely to start this work. Once that Goal closes, this Simulation Analysis stage is intended to run as a large CPU/filesystem/toolchain-focused round on 174-new, while 109 may continue Native Characterization independently.

## Naming

Existing `C16` paths, manifests, receipts and run IDs remain historical/compatibility identifiers. New planning and future evidence should use the AWMA project terminology. No cosmetic mass rename is authorized.
