# AGENTS.md — Decoupled-Tag L1 Research Workflow

This repository is the coordination, experiment-orchestration, and review-evidence repository for the Decoupled-Tag L1 (DTC-L1) reproduction project.

## Mandatory read order

Before doing project work on `hrl/decoupled-l1-exp-m1m4-v0`, read:

1. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
2. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
3. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`
4. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`
5. `docs/dtc_l1/goal/M4_FENCE_REACHABILITY_RESOLUTION.md`
6. `docs/dtc_l1/implementation/M4_MEMORY_OP_SEMANTICS.md`
7. `docs/dtc_l1/goal/VALIDATION_ACCEPTANCE_MATRIX.md`
8. `docs/dtc_l1/goal/M1_M4_GOAL_PLAN.md`
9. `docs/dtc_l1/goal/COUNTER_INVARIANT_SPEC.md`
10. `docs/dtc_l1/chatgpt_handoff/DISCUSSION_REFERENCE.md`
11. Core architecture spec in `swayhrl/gpgpu-sim@hrl/decoupled-l1-m1m4-v0:docs/dtc_l1/DTC_L1_SPEC.md`

For M4 fence-related requirements only, `M4_FENCE_REACHABILITY_RESOLUTION.md` and the updated `VALIDATION_ACCEPTANCE_MATRIX.md` are the specific authoritative refinement of older generic plan language. This precedence is intentional, not a conflict.

For all other conflicts, STOP and report rather than silently choosing a meaning.

## Repository roles

- M0 frozen core anchor: `swayhrl/gpgpu-sim@hrl/decoupled-l1-v0`.
- Active goal core: `swayhrl/gpgpu-sim@hrl/decoupled-l1-m1m4-v0`.
- M0 frozen framework anchor: `swayhrl/accel-sim-framework@hrl/decoupled-l1-exp-v0`.
- Active goal framework: `swayhrl/accel-sim-framework@hrl/decoupled-l1-exp-m1m4-v0`.

M0 branches are read-only design anchors. Do not implement M1-M4 on them.

## Frozen upstream anchors

Framework upstream base: `accel-sim/accel-sim-framework:dev` at `d930ad6d02c09bb56867132583735aba0389cff4`.

Core upstream base: `accel-sim/gpgpu-sim_distribution:dev` at `91880c53383d5a6a6742bfb1be2c5f34e39c7871`.

## Authority and evidence states

`docs/dtc_l1/chatgpt_handoff/` is ChatGPT-owned coordination state. Codex must not modify it unless explicitly authorized.

`docs/dtc_l1/codex_handoff/`, `docs/dtc_l1/review_packs/`, and `docs/dtc_l1/implementation/` are Codex-owned execution/evidence locations during the active goal.

Use evidence labels:

- `VERIFIED_SOURCE`
- `USER_CONFIRMED`
- `THESIS_SPEC`
- `PROVISIONAL_MODEL`
- `UNKNOWN`
- `SOURCE_UNREACHABLE_NA` only when an active specification explicitly authorizes that classification from source audit.

Do not silently guess or upgrade uncertainty.

## Current Goal-mode progression

M1, M2, and M3 are closed PASS. The currently authorized persistent Goal is to finish M4 only and stop at `READY_FOR_M5_REVIEW`.

Ordinary progress is not a stop boundary. Do not stop merely because a directed test, build, workload, or semantic checkpoint passes. Commit/push safe evidence and continue.

M4 may close only when every **active** HARD gate in the updated validation matrix passes and `review_packs/M4_COMPUTE_BRINGUP/` is complete.

If an active HARD gate fails, a source-reachable semantic ambiguity requires guessing, or a closed M1-M3 stage regresses, record evidence and STOP.

M5 is not authorized.

## Fence source-reachability boundary

The frozen current PTX frontend has been verified unable to generate the existing dynamic proxy-fence path. Do not repair this by expanding PTX frontend semantics during M4.

Explicitly forbidden:

- adding `fence` lexer/parser/static-decode semantics;
- mapping `membar` to `FENCE_OP` or proxy fence;
- forcing proxy-fence fields on ordinary instructions;
- bypassing the source's unsupported regular-fence behavior to satisfy old F01-F03.

Use F00A-F00D and `SOURCE_UNREACHABLE_NA` exactly as defined in `M4_FENCE_REACHABILITY_RESOLUTION.md`.

## Scientific and implementation discipline

- Do not duplicate simulator-core logic inside framework scripts as a workaround.
- Do not change LEGACY or closed M1-M3 behavior.
- Do not add cache semantics merely to make a benchmark complete.
- Do not tune any mechanism to reproduce target speedups.
- Do not special-case expected deadlock/performance outcomes.
- Do not alter L2/NoC/DRAM for DTC benefit in this goal.
- Preserve architectural L1 bypass and keep it distinct from out-of-scope DTC policy bypass.
- Atomic operations are side effects and must never be collapsed by read pending-hit merge logic.

## Git discipline

- Never use `git add .` or `git add -A`.
- Stage explicit paths only.
- Keep semantic commits separate.
- Record Core/Framework/config/workload identity for evidence.
- Run `git diff --check` and record clean/expected working-tree status at closeout.
- Do not force-push shared project branches.

## Experiment discipline

M4 workload runs are `DIAGNOSTIC` bring-up evidence, not final paper-performance evidence.

Accepted Base/IO/OO triplets must preserve identical workload input/trace and unrelated GPU configuration and must close dynamic instruction/Load/Store/Atomic/source-reachable-FENCE_OP counts, invariants, and provenance.

Do not commit raw traces, large logs, build trees, or binaries; commit compact summaries plus log hashes/indexes.

## Long-running jobs

Inspect no-progress jobs around 20 minutes, diagnose/escalate around 40 minutes, and stop plus record state around 60 minutes unless the stage explicitly expects longer silence. A job making measurable progress is not itself a stop condition.

## Review-pack requirement

A stage is not PASS because Codex says PASS. The M4 review pack must allow independent review from source anchors, changed files, tests, configs, CSV summaries, invariants, limitation statements, and log indexes.
