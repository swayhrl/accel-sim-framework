# AGENTS.md — Decoupled-Tag L1 M5 Research Workflow

This repository is the coordination, experiment-orchestration, and evidence repository for M5 performance/mechanism reproduction.

## Mandatory read order on `hrl/decoupled-l1-exp-m5-v0`

1. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
2. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
3. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`
4. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`
5. `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md`
6. `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`
7. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`
8. `docs/dtc_l1/m5/M5_GRAPHICS_PREP.md`
9. `docs/dtc_l1/review_packs/M4_COMPUTE_BRINGUP/README.md`
10. Core M5 `AGENTS.md`
11. Core `docs/dtc_l1/DTC_L1_SPEC.md`

If M5 execution status is `PLANNING HOLD` or `DRAFT ONLY`, do not begin formal M5 experiments.

## Branch roles

Validated historical anchors:

- Core M1-M4: `hrl/decoupled-l1-m1m4-v0` at `cdeec769fd0c1be12b45d58536ecb81074d4b415`.
- Framework M1-M4: `hrl/decoupled-l1-exp-m1m4-v0` at `56369da33dc5f48fc9ac071fd122fde4b35bd8c9`.

M5 working branches:

- Core: `hrl/decoupled-l1-m5-v0`.
- Framework: `hrl/decoupled-l1-exp-m5-v0`.

Do not write M5 changes back to M0 or M1-M4 branches.

## Scientific objective

M5 targets **mechanism/trend fidelity**, not numerical fitting to thesis speedup values.

The expected causal chain is:

`Base structural stalls -> limited concurrent misses -> DTC removes structural constraints -> higher live miss concurrency / latency hiding -> performance effect`.

If this chain is weak or broken on a workload, diagnose the reason. Do not tune the workload or architecture to make the bars look like the thesis.

## Problem behavior

After M5 Goal activation, ordinary problems are resolved inside the Goal according to `M5_PROBLEM_RESOLUTION_POLICY.md`.

Do not STOP merely for:

- missing workload binary/input;
- alias/provenance uncertainty that can still be researched;
- build/PTX/parser failure;
- workload assertion;
- poor or negative speedup;
- timeout with measurable progress;
- counter/instrumentation gap;
- unexpected bottleneck;
- a repairable simulator bug.

Diagnose -> repair/reconstruct -> regress -> invalidate stale results when necessary -> resume.

Pause only at a real researcher-decision boundary that cannot be source/thesis resolved, or final `M5_COMPUTE_READY_FOR_REVIEW`.

## Formal-result discipline

Every result records:

- Core SHA;
- Framework SHA;
- config hash;
- workload source/binary/PTX/input hashes;
- parser schema;
- result classification.

FORMAL data from a behavior/timing SHA that is later repaired becomes OBSOLETE for affected stages. Instrumentation-only changes may retain old performance cycles only after exact neutrality differential.

Do not commit raw logs, traces, binaries, build trees, or large datasets. Commit compact JSON/CSV and raw-log indexes.

## Git discipline

- Never use `git add .` or `git add -A`.
- Stage explicit paths only.
- Keep semantic commits separate.
- Do not force-push shared branches.
- Use clean worktrees and `git diff --check` at substage handoffs.

## Paper/extension separation

Primary paper-mode figures use only:

- PAPER_BASE;
- PAPER_IO;
- PAPER_OO.

Do not mix `MODERN_OO_SECTOR`, equal-area controls, coalescer sensitivities, or other extensions into Figures 4.2-4.10.

Compute-only aggregate is `GM-GP`; reserve `GM-ALL-PAPER` until all five graphics workloads have a source-backed execution path.

Graphics preparation is nonblocking for compute M5.

## Handoff progression

Use `M5_HANDOFF_CONTRACT.md`. Substage PASS is a checkpoint-and-continue boundary, not a human-approval stop. After M5 authorization, preserve evidence, commit/push, update `LATEST_REPORT.md`, and continue to the next authorized substage automatically.