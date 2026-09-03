# AGENTS.md — Decoupled-Tag L1 Research Workflow

This repository is the coordination, experiment-orchestration, and review-evidence repository for the Decoupled-Tag L1 (DTC-L1) reproduction project.

## Mandatory read order

Before doing project work on `hrl/decoupled-l1-exp-m1m4-v0`, read:

1. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
2. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
3. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`
4. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`
5. `docs/dtc_l1/goal/M4_COMPLETION_ACCOUNTING_RECOVERY.md`
6. `docs/dtc_l1/implementation/M4_COMPUTE_BRINGUP_FAILURE.md`
7. `docs/dtc_l1/goal/M4_FENCE_REACHABILITY_RESOLUTION.md`
8. `docs/dtc_l1/implementation/M4_MEMORY_OP_SEMANTICS.md`
9. `docs/dtc_l1/goal/VALIDATION_ACCEPTANCE_MATRIX.md`
10. `docs/dtc_l1/goal/M1_M4_GOAL_PLAN.md`
11. `docs/dtc_l1/goal/COUNTER_INVARIANT_SPEC.md`
12. `docs/dtc_l1/chatgpt_handoff/DISCUSSION_REFERENCE.md`
13. Core architecture spec in `swayhrl/gpgpu-sim@hrl/decoupled-l1-m1m4-v0:docs/dtc_l1/DTC_L1_SPEC.md`

Specific precedence is intentional:

- for the active 2DConv completion-accounting blocker, `M4_COMPLETION_ACCOUNTING_RECOVERY.md` is authoritative;
- for M4 fence/source-reachability requirements only, `M4_FENCE_REACHABILITY_RESOLUTION.md` and the updated validation matrix refine older generic plan language.

For other conflicts, STOP and report rather than silently choosing a meaning.

## Repository roles

- M0 frozen core anchor: `swayhrl/gpgpu-sim@hrl/decoupled-l1-v0`.
- Active goal core: `swayhrl/gpgpu-sim@hrl/decoupled-l1-m1m4-v0`.
- M0 frozen framework anchor: `swayhrl/accel-sim-framework@hrl/decoupled-l1-exp-v0`.
- Active goal framework: `swayhrl/accel-sim-framework@hrl/decoupled-l1-exp-m1m4-v0`.

M0 branches are read-only design anchors.

## Frozen upstream anchors

Framework upstream base: `accel-sim/accel-sim-framework:dev` at `d930ad6d02c09bb56867132583735aba0389cff4`.

Core upstream base: `accel-sim/gpgpu-sim_distribution:dev` at `91880c53383d5a6a6742bfb1be2c5f34e39c7871`.

## Authority and evidence states

`docs/dtc_l1/chatgpt_handoff/` and `docs/dtc_l1/goal/` are coordination/specification state. Codex must not silently rewrite architecture/acceptance requirements to pass a failing test.

`docs/dtc_l1/codex_handoff/`, `docs/dtc_l1/review_packs/`, and `docs/dtc_l1/implementation/` are Codex-owned execution/evidence locations during the active goal unless an active specification says otherwise.

Use evidence labels:

- `VERIFIED_SOURCE`
- `USER_CONFIRMED`
- `THESIS_SPEC`
- `PROVISIONAL_MODEL`
- `UNKNOWN`
- `SOURCE_UNREACHABLE_NA` only when an active specification explicitly authorizes that classification from source audit.

Do not silently guess or upgrade uncertainty.

## Current Goal-mode progression

M1, M2, and M3 are closed PASS. The persistent Goal is currently blocked inside M4 by a source-reachable cacheable-load completion-accounting assertion exposed by PolyBench 2DConv.

The immediate authorized task is the ordered recovery `R4C.0-R4C.8` in `M4_COMPLETION_ACCOUNTING_RECOVERY.md`.

Ordinary progress is not a stop boundary. Do not stop merely because localization, a directed test, build, regression, or semantic checkpoint passes. Preserve safe evidence and continue.

If the full recovery passes, resume the remaining M4 Goal automatically without waiting for human confirmation.

M4 may close only when every active HARD gate passes and `review_packs/M4_COMPUTE_BRINGUP/` is complete.

If an active HARD gate fails, dependency ownership remains ambiguous after source-backed localization, scoreboard correctness would require an unverified shortcut, or a closed M1-M3 stage regresses, record evidence and STOP.

M5 is not authorized.

## Completion-accounting recovery boundary

The active failure is `pending >= dependencies` in both PAPER_IO and PAPER_OO DTC completion on real 2DConv.

Recovery must prove:

```text
issue-registered DTC dependency count
== PIB-owned 128B line dependency count
== dependencies closed at retirement
```

and exactly-once ownership for every DTC-owned cacheable-load UID.

Explicitly forbidden:

- removing/weakening the failing assertion;
- clamping dependencies to current pending value;
- forcing `m_pending_writes` to zero;
- releasing scoreboard registers without exact ownership closure;
- changing frozen 128B DTC dependency granularity merely to match the failure;
- reintroducing conventional L1D MSHR/fill as the DTC read backend.

## Fence source-reachability boundary

The frozen PTX frontend is verified unable to generate the current dynamic proxy-fence path. Do not repair this by expanding frontend semantics during M4.

Do not add `fence` lexer/parser/static-decode semantics, map `membar` to `FENCE_OP`, force proxy-fence fields on ordinary instructions, or bypass unsupported regular-fence behavior.

The fence resolution resumes after the active completion-accounting blocker is closed.

## Scientific and implementation discipline

- Do not duplicate simulator-core logic inside framework scripts as a workaround.
- Do not change LEGACY or closed M1-M3 semantics.
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

Accepted Base/IO/OO triplets must preserve identical workload input/trace and unrelated GPU configuration and must close dynamic instruction/Load/Store/Atomic/source-reachable-FENCE_OP counts, DTC invariants, and provenance.

Do not commit raw traces, large logs, build trees, or binaries; commit compact summaries plus log hashes/indexes.

## Long-running jobs

Inspect no-progress jobs around 20 minutes, diagnose/escalate around 40 minutes, and stop plus record state around 60 minutes unless the stage explicitly expects longer silence. A job making measurable progress is not itself a stop condition.

## Review-pack requirement

A stage is not PASS because Codex says PASS. The M4 review pack must allow independent review from source anchors, changed files, tests, configs, CSV summaries, invariants, recovery evidence, limitation statements, and log indexes.
