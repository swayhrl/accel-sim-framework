# AWMA Simulation Analysis — Execution Handoff

Status: **ACTIVE / may run in parallel with the ongoing Native Characterization and Qwen Decode/analysis work.**

Project: **AI Workload Memory Analysis (AWMA)**.

This directory defines the Simulation Analysis mainline and its first executable foundation Goal. It is intentionally separated from the Native Characterization worktree so both lines can progress concurrently.

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
7. `PARALLEL_EXECUTION_AND_AUTONOMOUS_RECOVERY.md`
8. `ACCEPTANCE_AND_REVIEW_REQUIREMENTS.md`
9. `CODEX_NEXT_STAGE_174NEW_SIMULATION_FOUNDATION.md`

## Execution boundary

A new Codex window on 174-new may start this work **now**, even while another 174-new worktree is running Qwen Decode/native analysis, provided that:

- a fresh Git worktree/branch is used;
- current Native/Qwen worktrees and processes are not modified, cleaned, killed, restarted or repurposed;
- build/hash/simulation work uses bounded resources;
- node164 writes stay in the authorized AWMA simulation/catalog/provenance namespaces;
- this foundation Goal uses no 109 GPU and starts no production simulator sweep.

## Goal-mode behavior

This is a solve-and-continue Goal. Recoverable engineering blockers should be diagnosed and fixed inline, regression-tested, recorded, and execution should continue.

Do not stop merely because of:

```text
missing path
stale legacy path
missing helper binary
first build failure
missing default nvcc/tool path
user-space dependency gap
small parser/schema plumbing mismatch
fixture/catalog issue with unambiguous intended semantics
```

Escalate only when continuing would change workload identity, trace semantics, simulator architectural semantics, scientific status/claim scope, accepted raw authority, or require an unsafe/destructive operation.

## Naming

Existing `C16` paths, manifests, receipts and run IDs remain historical/compatibility identifiers. New planning and future evidence use AWMA terminology. No cosmetic mass rename is authorized.
