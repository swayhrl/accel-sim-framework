# AGENTS.md — Decoupled-Tag L1 M5 Research Workflow

This repository is the coordination, experiment-orchestration, and evidence repository for M5 performance/mechanism reproduction.

## Mandatory read order on `hrl/decoupled-l1-exp-m5-v0`

1. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
2. `docs/dtc_l1/m5/M5_V1_APPROVAL.md`
3. `docs/dtc_l1/m5/M5_DIRTY_VICTIM_POLICY_RESOLUTION.md`
4. `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md`
5. `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`
6. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`
7. `docs/dtc_l1/m5/M5_GRAPHICS_PREP.md`
8. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`
9. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`
10. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
11. `docs/dtc_l1/implementation/M5_ISSUE_LOG.md`
12. `docs/dtc_l1/review_packs/M4_COMPUTE_BRINGUP/README.md`
13. Core M5 `AGENTS.md`
14. Core `docs/dtc_l1/DTC_L1_SPEC.md`

`M5_V1_APPROVAL.md` activates the detailed matrix. `M5_DIRTY_VICTIM_POLICY_RESOLUTION.md` is the researcher-approved specific refinement for M5-T005. For unrelated scientific conflicts that change experiment meaning, do not guess.

## Branch roles

Validated historical anchors:

- Core M1-M4: `hrl/decoupled-l1-m1m4-v0` at `cdeec769fd0c1be12b45d58536ecb81074d4b415`.
- Framework M1-M4: `hrl/decoupled-l1-exp-m1m4-v0` at `56369da33dc5f48fc9ac071fd122fde4b35bd8c9`.

M5 working branches:

- Core: `hrl/decoupled-l1-m5-v0`.
- Framework: `hrl/decoupled-l1-exp-m5-v0`.

Do not write M5 changes back to M0 or M1-M4 branches.

## Current progression

M5.0A is PASS. M5.0B is ACTIVE.

M5-T005's prior `RESEARCHER_DECISION_REQUIRED` boundary is resolved. Execute the R5DV sequence in `M5_DIRTY_VICTIM_POLICY_RESOLUTION.md`, close the issue with evidence, then resume the existing M5.0B workload work without redoing valid provenance work.

After M5.0B PASS, continue automatically:

`M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`.

Terminal compute state:

`M5_COMPUTE_READY_FOR_REVIEW`.

## Scientific objective

M5 targets **mechanism/trend fidelity**, not numerical fitting to thesis speedup values.

Expected causal chain:

`Base structural stalls -> limited concurrent misses -> DTC removes structural constraints -> higher live-miss concurrency / latency hiding -> performance effect`.

If this chain is weak or broken, diagnose the reason. Do not tune workload or architecture to make bars resemble the thesis.

## Researcher-frozen M5 definitions

### Figure 4.5

Primary DTC main-result configuration is 16 KiB logical Tag/cache capacity + 80 KiB physical Cacheline Array. IO PIB=256, OO PIB=128. Base remains conventional 16 KiB L1, PIB=8, MSHR=32.

### Conventional-L1 dirty-victim policy

All paper-facing M5 formal configurations explicitly use:

`-gpgpu_l1_cache_write_ratio 0`.

Preserve current write-through, allocation, LRU, MSHR, scoreboard, and DTC semantics. Do not add a new `tag_array::probe` fallback solely to preserve the inherited 25% dirty-retention heuristic. Ratio 25 is diagnostic only.

Already-running ratio-25 jobs may finish and be preserved as diagnostics; they cannot become paper-facing formal results. Corrected work may start concurrently when the calibrated resource budget permits.

### Figure 4.7

Count one live miss from new-miss lower-request commit through final lower response. Primary plotted metric is per-SM cycle average.

### Figure 4.2

Formal categories are PIB/waiting-buffer full, true Tag & Cacheline allocation failure, MSHR entry/merge capacity failure, and Miss Queue/lower-request-capacity failure. Tag-bank arbitration remains separate diagnostic evidence.

## Problem behavior

Ordinary problems are resolved inside the Goal according to `M5_PROBLEM_RESOLUTION_POLICY.md`.

Do not STOP merely for:

- missing workload binary/input/wrapper;
- alias/provenance uncertainty that can still be researched;
- build/PTX/parser failure;
- workload assertion;
- Base/IO/OO operation-count mismatch;
- poor or negative speedup;
- timeout with diagnosable progress;
- counter/instrumentation gap;
- unexpected Tag-bank/downstream bottleneck;
- a repairable source-backed simulator bug;
- a significant performance change after the ratio-0 correction.

Diagnose -> repair/reconstruct -> regress -> invalidate stale formal results when necessary -> resume.

Pause only at a new genuine `RESEARCHER_DECISION_REQUIRED` boundary or final `M5_COMPUTE_READY_FOR_REVIEW`.

## Workload-recovery discipline

M5.0B must recover/source-verify all ten thesis compute algorithms. Explicit alias audit includes `gemv -> gemver?`, `gesu -> gesummv?`, and `conv2d -> 2DConvolution/pb_2dconv?`.

Missing ready binaries are not permission to substitute algorithms. Input scale must come from canonical/standard datasets and Base-only work-amount evidence, never from the size with the best DTC speedup.

## Formal-result discipline

Every result records Core SHA, Framework SHA, config hash, workload source/binary/PTX/input hashes, parser schema, and classification.

FORMAL data from an invalidated behavior/config identity becomes OBSOLETE for affected stages. Preserve diagnostic evidence accurately; do not relabel ratio-25 runs as ratio-0 results.

Do not commit raw logs, traces, binaries, build trees, or large datasets. Commit compact JSON/CSV and raw-log indexes.

## Git discipline

- Never use `git add .` or `git add -A`.
- Stage explicit paths only.
- Keep semantic commits separate.
- Do not force-push shared branches.
- Preserve pre-policy evidence.
- Use clean worktrees and `git diff --check` at substage handoffs.

## Paper/extension separation

Primary paper-mode figures use only PAPER_BASE, PAPER_IO, and PAPER_OO.

Do not mix `MODERN_OO_SECTOR`, equal-area controls, coalescer sensitivities, dirty-ratio sensitivity controls, or other extensions into Figures 4.2-4.10.

Compute-only aggregate is `GM-GP`; reserve `GM-ALL-PAPER` until all five graphics workloads have a source-backed execution path.

Graphics G0-G2 preparation is active but nonblocking for compute M5.

## Handoff progression

Use `M5_HANDOFF_CONTRACT.md`. Substage PASS is a checkpoint-and-continue boundary, not a human-approval stop. Preserve evidence, commit/push, update `LATEST_REPORT.md`, and continue automatically.