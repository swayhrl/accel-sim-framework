# AGENTS.md — Decoupled-Tag L1 Research Workflow

This repository is the coordination, experiment-orchestration, and review-evidence repository for the Decoupled-Tag L1 (DTC-L1) reproduction project.

## Mandatory read order

Before doing any project work on `hrl/decoupled-l1-exp-m1m4-v0`, read:

1. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
2. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
3. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`
4. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`
5. `docs/dtc_l1/chatgpt_handoff/DISCUSSION_REFERENCE.md`
6. `docs/dtc_l1/goal/M2_IO_RESPONSE_RECOVERY_SPEC.md`
7. `docs/dtc_l1/goal/M1_M4_GOAL_PLAN.md`
8. `docs/dtc_l1/goal/COUNTER_INVARIANT_SPEC.md`
9. `docs/dtc_l1/goal/VALIDATION_ACCEPTANCE_MATRIX.md`
10. Core architecture spec in `swayhrl/gpgpu-sim@hrl/decoupled-l1-m1m4-v0:docs/dtc_l1/DTC_L1_SPEC.md`

If these disagree, STOP and report the conflict. Do not choose a meaning silently.

## Repository roles

- M0 frozen core anchor: `swayhrl/gpgpu-sim@hrl/decoupled-l1-v0`.
- Active goal core: `swayhrl/gpgpu-sim@hrl/decoupled-l1-m1m4-v0`.
- M0 frozen framework anchor: `swayhrl/accel-sim-framework@hrl/decoupled-l1-exp-v0`.
- Active goal framework: `swayhrl/accel-sim-framework@hrl/decoupled-l1-exp-m1m4-v0`.

The M0 branches are read-only design anchors. Do not implement M1-M4 on them.

Do not duplicate simulator-core logic inside framework scripts as a workaround for missing core behavior.

## Frozen upstream anchors

Framework upstream base:

- upstream: `accel-sim/accel-sim-framework:dev`
- SHA: `d930ad6d02c09bb56867132583735aba0389cff4`

Core upstream base:

- upstream: `accel-sim/gpgpu-sim_distribution:dev`
- SHA: `91880c53383d5a6a6742bfb1be2c5f34e39c7871`

## Authority and ownership

`docs/dtc_l1/chatgpt_handoff/` is ChatGPT-owned coordination state. Codex must not modify it unless an active stage explicitly grants permission.

`docs/dtc_l1/codex_handoff/`, `docs/dtc_l1/review_packs/`, and `docs/dtc_l1/implementation/` are Codex-owned execution/evidence locations during the active goal.

Architecture facts use:

- `VERIFIED_SOURCE`
- `USER_CONFIRMED`
- `THESIS_SPEC`
- `PROVISIONAL_MODEL`
- `UNKNOWN`

Do not silently guess or upgrade uncertainty.

## Goal-mode progression rule

The currently authorized persistent Goal is the remaining M2 work through M4 only. The explicit durable objective and final stopping condition are in `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`.

Codex may continue automatically M2 -> M3 -> M4 without waiting for human confirmation only when every HARD gate for the completed stage passes.

At each major stage boundary Codex must:

1. run the required validation;
2. create/update that stage's review pack;
3. make semantic commits with explicit-path staging;
4. push both affected repositories;
5. update Codex-owned `codex_handoff/LATEST_REPORT.md`;
6. then continue to the next stage if and only if all HARD gates pass.

Ordinary progress is not a stop boundary. Do not stop merely because a directed test passed, a safe semantic checkpoint was committed/pushed, a build succeeded, or M2/M3 passed. Preserve evidence and continue toward the persistent Goal.

If any HARD gate fails, or a source-semantic ambiguity would require guessing, Codex must record evidence, push review material if safe, and STOP. Do not continue in order to "see if later stages fix it".

M5 experiments, paper-result reproduction, graphics proxy work, equal-area studies, and performance claims are NOT authorized by this goal.

## Git discipline

- Never use `git add .` or `git add -A`.
- Stage explicit paths only.
- Keep semantic commits separate.
- Record both Core SHA and Framework SHA in every formal/diagnostic result.
- Run `git diff --check` and record clean/expected working-tree status at stage closeout.
- Do not force-push shared project branches without explicit authorization.

## Experiment discipline

Formal comparisons must preserve identical workload input/trace and unrelated GPU configuration across variants. Only intended DTC knobs may differ.

Every result must carry:

- Core SHA;
- Framework SHA;
- config identity/SHA;
- trace/workload identity;
- status: `FORMAL`, `DIAGNOSTIC`, `PRE_FIX`, or `OBSOLETE`.

M4 workload runs in this goal are `DIAGNOSTIC` bring-up evidence, not final paper evidence.

Do not mix results from different source SHAs into one formal aggregate unless explicitly normalized and documented.

Do not commit raw traces, large simulator logs, build trees, or large generated artifacts. Commit compact summaries and `RAW_LOG_INDEX.tsv` provenance instead.

## Baseline protection

When DTC/paper instrumentation is disabled, modified code/configuration must remain behaviorally and timing neutral relative to the frozen clean baseline. M1 is already closed PASS; later stages must not regress that boundary.

## Research-scope protection

- Do not add cache semantics merely to make a benchmark complete.
- Do not tune any mechanism to reproduce a target speedup.
- Do not special-case expected deadlock/performance outcomes.
- Do not alter L2/NoC/DRAM to make DTC look better unless a later explicitly authorized sensitivity experiment requires it.
- Preserve architectural L1 bypass behavior; do not confuse it with later DTC policy bypass.
- Atomic operations are side effects and must never be collapsed by read pending-hit merge logic.

## Long-running jobs

Inspect a no-progress job around 20 minutes, diagnose/escalate around 40 minutes, and stop plus record state by around 60 minutes unless the active stage explicitly expects a longer silent interval. A long job that is making measurable progress is not itself a stop condition.

## Review-pack requirement

A stage is not PASS because Codex says PASS. The review pack must allow independent review from source anchors, changed files, tests, configs, CSV summaries, invariants, and logs/indexes.
