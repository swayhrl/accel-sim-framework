# AGENTS.md — Decoupled-Tag L1 Research Workflow

This repository is the coordination and experiment-orchestration repository for the Decoupled-Tag L1 (DTC-L1) reproduction project.

## Mandatory read order

Before doing any project work on `hrl/decoupled-l1-exp-v0`, read:

1. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
2. `docs/dtc_l1/chatgpt_handoff/DISCUSSION_REFERENCE.md`
3. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`
4. `docs/dtc_l1/README.md`
5. Core architecture spec in `swayhrl/gpgpu-sim@hrl/decoupled-l1-v0:docs/dtc_l1/DTC_L1_SPEC.md`

If the active stage file says HOLD or STOP, do not infer permission to implement from other documents.

## Repository roles

- `swayhrl/gpgpu-sim@hrl/decoupled-l1-v0`: authoritative simulator-core implementation and M0 architecture specification.
- `swayhrl/accel-sim-framework@hrl/decoupled-l1-exp-v0`: experiment configuration, workload orchestration, cross-repository handoff, review packs, and formal result provenance.

Do not duplicate simulator-core logic inside framework scripts as a workaround for missing core behavior.

## Frozen source anchors

Framework base:

- upstream: `accel-sim/accel-sim-framework`
- ref: `dev`
- SHA: `d930ad6d02c09bb56867132583735aba0389cff4`

Core base:

- upstream: `accel-sim/gpgpu-sim_distribution`
- ref: `dev`
- SHA: `91880c53383d5a6a6742bfb1be2c5f34e39c7871`

The project branches were created directly from those official upstream commits before project documentation was added.

## Authority and ownership

`docs/dtc_l1/chatgpt_handoff/` is ChatGPT-owned coordination state. Codex must not modify it unless an active stage explicitly grants permission.

`docs/dtc_l1/codex_handoff/` and `docs/dtc_l1/review_packs/<stage>/` are Codex-owned execution evidence after a stage begins.

Architecture facts use these labels:

- `VERIFIED_SOURCE`
- `USER_CONFIRMED`
- `THESIS_SPEC`
- `PROVISIONAL_MODEL`
- `UNKNOWN`

Do not silently guess or upgrade uncertainty.

## Stage isolation

Use dedicated branches/worktrees. Do not modify or rebuild another study's active worktree. Do not merge unrelated L2/TLB/cache-study branches into DTC-L1.

Codex executes only the current `CODEX_NEXT_STAGE.md` and must STOP at its boundary. No autonomous continuation into later stages.

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

Do not mix results from different source SHAs into one formal aggregate unless explicitly normalized and documented.

Do not commit raw traces, large simulator logs, build trees, or large generated artifacts. Commit compact summaries and `RAW_LOG_INDEX.tsv`-style provenance instead.

## Baseline protection

When DTC is disabled, modified code/configuration must remain behaviorally and timing neutral relative to the frozen clean baseline except for explicitly enabled instrumentation. If neutrality is not demonstrated, formal speedup experiments are blocked.

## Research-scope protection

- Do not add cache semantics merely to make a benchmark complete.
- Do not tune a graphics proxy to reproduce the desired speedup; calibration must target memory-access signatures only.
- Do not label a proxy as direct glmark2 execution.
- Do not special-case expected deadlock/performance outcomes.
- Do not alter L2/NoC/DRAM to make DTC look better unless running an explicitly named sensitivity experiment.

## Long-running jobs

Inspect a no-progress job around 20 minutes, diagnose/escalate around 40 minutes, and stop plus record state by around 60 minutes unless the active stage explicitly expects a longer silent interval.

## Review-pack requirement

A stage is not PASS because Codex says PASS. The review pack must allow independent review from source anchors, changed files, tests, configs, CSV summaries, invariants, and logs/indexes.

At completion: update Codex-owned `LATEST_REPORT.md`, create the stage review pack, commit explicit paths, push, and STOP.
