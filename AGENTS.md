# AGENTS.md — Decoupled-Tag L1 M5 Research Workflow

This repository is the coordination, experiment-orchestration, and evidence repository for M5 performance/mechanism reproduction.

## Mandatory read order on `hrl/decoupled-l1-exp-m5-v0`

1. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
2. `docs/dtc_l1/m5/M5_V1_APPROVAL.md`
3. `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md`
4. `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`
5. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`
6. `docs/dtc_l1/m5/M5_GRAPHICS_PREP.md`
7. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`
8. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`
9. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
10. `docs/dtc_l1/review_packs/M4_COMPUTE_BRINGUP/README.md`
11. Core M5 `AGENTS.md`
12. Core `docs/dtc_l1/DTC_L1_SPEC.md`

`M5_V1_APPROVAL.md` activates the detailed matrix. Its approval supersedes the stale `PLANNING DRAFT` banner inside `M5_EXPERIMENT_MATRIX.md`; the matrix body remains the approved v1 execution plan.

## Branch roles

Validated historical anchors:

- Core M1-M4: `hrl/decoupled-l1-m1m4-v0` at `cdeec769fd0c1be12b45d58536ecb81074d4b415`.
- Framework M1-M4: `hrl/decoupled-l1-exp-m1m4-v0` at `56369da33dc5f48fc9ac071fd122fde4b35bd8c9`.

M5 working branches:

- Core: `hrl/decoupled-l1-m5-v0`.
- Framework: `hrl/decoupled-l1-exp-m5-v0`.

Do not write M5 changes back to M0 or M1-M4 branches.

## Current authorized progression

M5 v1 is ACTIVE. Execute continuously:

`M5.0A -> M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`.

After each substage PASS, write the required handoff, run parser/counter sanity, commit/push compact evidence, update `LATEST_REPORT.md`, and continue automatically.

Terminal compute state:

`M5_COMPUTE_READY_FOR_REVIEW`.

## Scientific objective

M5 targets **mechanism/trend fidelity**, not numerical fitting to thesis speedup values.

The expected causal chain is:

`Base structural stalls -> limited concurrent misses -> DTC removes structural constraints -> higher live miss concurrency / latency hiding -> performance effect`.

If this chain is weak or broken on a workload, diagnose the reason. Do not tune the workload or architecture to make the bars look like the thesis.

## Researcher-frozen M5 v1 interpretations

### Figure 4.5

Primary DTC main-result configuration is 16KB logical Tag/cache capacity + 80KB physical Cacheline Array. IO PIB=256, OO PIB=128. Base remains conventional 16KB L1, PIB=8, MSHR=32.

### Figure 4.7

Count one live miss from new-miss lower-request commit through final lower-response completion. Pending-hit merge adds no second miss; a real duplicate lower request after logical-Tag eviction does.

Primary plotted metric is per-SM cycle average:

`sum(live misses across all SMs/cycles) / (num_SM * sampled_kernel_cycles)`.

### Figure 4.2

Formal paper-facing categories only:

- PIB/waiting-buffer full;
- true Tag & Cacheline allocation failure;
- MSHR entry/merge capacity failure;
- Miss Queue/lower-request-capacity failure.

Tag-bank arbitration conflict remains diagnostic and must not be folded into Tag & Cacheline allocation failure.

## Problem behavior

Ordinary problems are resolved inside the Goal according to `M5_PROBLEM_RESOLUTION_POLICY.md`.

Do not STOP merely for:

- missing workload binary/input;
- alias/provenance uncertainty that can still be researched;
- build/PTX/parser failure;
- workload assertion;
- Base/IO/OO operation-count mismatch;
- poor or negative speedup;
- timeout with diagnosable progress;
- counter/instrumentation gap;
- unexpected Tag-bank/downstream bottleneck;
- a repairable source-backed simulator bug;
- stale formal results after a justified repair.

Diagnose -> repair/reconstruct -> regress -> invalidate stale results when necessary -> resume.

Pause only at a real `RESEARCHER_DECISION_REQUIRED` boundary defined in the active problem-resolution policy, or final `M5_COMPUTE_READY_FOR_REVIEW`.

## Workload-recovery discipline

M5.0B must recover/source-verify all ten thesis compute algorithms. Explicit first-priority alias audit:

- `gemv -> gemver?`;
- `gesu -> gesummv?`;
- `conv2d -> 2DConvolution/pb_2dconv?`.

Missing ready binaries are not permission to substitute algorithms. Recover canonical source/build wrappers/PTX where justified and record algorithm proof plus hashes.

Input scale must come from canonical/standard datasets and Base-only full-load/work-amount evidence, never from the size with the best DTC speedup.

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

Graphics G0-G2 preparation is ACTIVE but nonblocking for compute M5.

## Handoff progression

Use `M5_HANDOFF_CONTRACT.md`. Substage PASS is a checkpoint-and-continue boundary, not a human-approval stop. Preserve evidence, commit/push, update `LATEST_REPORT.md`, and continue to the next authorized substage automatically.
