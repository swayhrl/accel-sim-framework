# DTC-L1 M5 Explicit Goal Launch Contract

Status: **ACTIVE — M5 v1 CONTINUOUS COMPUTE GOAL; M5-T005 DECISION RESOLVED**

This is the durable objective for Codex Goal mode.

Primary M5 authority:

- `docs/dtc_l1/m5/M5_V1_APPROVAL.md`;
- `docs/dtc_l1/m5/M5_DIRTY_VICTIM_POLICY_RESOLUTION.md` — specific approved refinement for M5-T005;
- `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md`;
- `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`;
- `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`;
- `docs/dtc_l1/m5/M5_GRAPHICS_PREP.md`.

## Persistent Goal

Reproduce and explain the Decoupled-Tag Cache mechanism on the ten thesis general-purpose compute workloads through Figures 4.2, 4.5, 4.7, 4.8, 4.9, and 4.10, resolving ordinary implementation/workload/platform issues inside Goal mode rather than stopping at the first failure.

Scientific target:

`traditional L1 structural limits -> fewer live concurrent misses -> DTC removes structural limits -> more concurrency / better latency hiding -> performance effect`.

Exact thesis speedups are references, not pass thresholds.

Terminal compute state:

`M5_COMPUTE_READY_FOR_REVIEW`.

## Active branches

Core:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m5-v0`

Framework:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m5-v0`

Validated parents remain M1-M4 final anchors. Do not write M5 work back to them.

## Mandatory read order

Framework:

1. `AGENTS.md`
2. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/dtc_l1/m5/M5_V1_APPROVAL.md`
4. `docs/dtc_l1/m5/M5_DIRTY_VICTIM_POLICY_RESOLUTION.md`
5. `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md`
6. `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`
7. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`
8. `docs/dtc_l1/m5/M5_GRAPHICS_PREP.md`
9. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`
10. this file
11. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
12. `docs/dtc_l1/implementation/M5_ISSUE_LOG.md`
13. final M4 review pack as regression context

Core:

14. `AGENTS.md`
15. `docs/dtc_l1/DTC_L1_SPEC.md`

## Researcher-frozen M5 definitions

### Main configuration

- PAPER_BASE: conventional 16 KiB L1, 128B, 4-way, PIB=8, MSHR=32.
- PAPER_IO: 16 KiB logical Tag capacity + 80 KiB physical Cacheline Array, PIB=256.
- PAPER_OO: 16 KiB logical Tag capacity + 80 KiB physical Cacheline Array, PIB=128.

### Conventional-L1 dirty-victim policy

All paper-facing formal configs explicitly use:

`-gpgpu_l1_cache_write_ratio 0`.

Keep write-through and all other frozen cache semantics unchanged. Ratio 25 is diagnostic only.

### Figure 4.7

Common live miss = new-miss lower-request commit through final lower response. Primary plotted metric = per-SM cycle average.

### Figure 4.2

Paper-facing categories = PIB full, true Tag+Cacheline allocation failure, MSHR capacity/merge, Miss Queue/lower-capacity. Tag-bank arbitration is separate diagnostic evidence.

## Current resume point

M5.0A is PASS. M5.0B is active.

Before continuing unresolved workload recovery, close M5-T005 through the ordered R5DV sequence in `M5_DIRTY_VICTIM_POLICY_RESOLUTION.md`:

- preserve ratio-25 diagnostics;
- change the complete formal config family to explicit ratio 0 only;
- directed dirty-set replacement regression;
- canonical SpMV LEGACY/PAPER_BASE 16 KiB ratio-0 recovery;
- sentinel/config-identity refresh;
- close M5-T005;
- resume M5.0B from existing valid checkpoints.

Existing diagnostic jobs may continue. Corrected work need not wait for them if calibrated host resources permit parallel execution.

## Authorized continuous sequence

After M5-T005 closes, continue automatically:

`M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`.

At each PASS boundary:

1. satisfy acceptance criteria;
2. produce required handoff/review evidence;
3. strict parser/counter sanity;
4. explicit-path commit/push;
5. update `codex_handoff/LATEST_REPORT.md`;
6. begin the next substage without asking for confirmation.

## Problem-resolution behavior

Follow `M5_PROBLEM_RESOLUTION_POLICY.md`.

Ordinary issues — missing workload/wrapper, build/PTX failure, assertions, counter gaps, timeout, poor speedup, absent expected pressure, platform bottlenecks, or source-correct repairable bugs — are normally solved inside the Goal.

A substantial speed/performance difference caused by the ratio-0 correction is evidence to classify, not a target to tune away.

## Pause conditions

Pause only for a genuine researcher-decision boundary that cannot be source/thesis resolved without choosing different experiment meaning, a required change to frozen M0-M4 architecture semantics, or terminal `M5_COMPUTE_READY_FOR_REVIEW`.

## Parallel graphics

Graphics G0-G2 preparation remains nonblocking and may progress when resources permit. Do not contaminate compute formal identities. Do not emit `GM-ALL-PAPER` until all five graphics workloads are source-backed and correctness-clean.

## Forbidden before compute review

Do not:

- enlarge 16 KiB Base to bypass pressure;
- restore ratio 25 to paper-facing runs merely because it changes performance;
- invent a new `tag_array::probe` fallback just to keep the 25% heuristic;
- disable deadlock detection or weaken scoreboard/accounting assertions;
- tune architecture/input/downstream settings to thesis bars;
- substitute algorithms silently;
- mix MODERN_OO_SECTOR into Figures 4.2-4.10;
- begin M5.7+ supplemental studies before compute review.
