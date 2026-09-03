# CODEX_NEXT_STAGE

## Status

**ACTIVE — M5 v1 CONTINUOUS COMPUTE GOAL AUTHORIZED**

M1-M4 are closed PASS and frozen as validated infrastructure. M5 v1 has been researcher-approved and may now execute continuously on the dedicated M5 branches.

## Active branches

Core:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m5-v0`

Framework:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m5-v0`

Validated parents:

- Core M1-M4 final: `cdeec769fd0c1be12b45d58536ecb81074d4b415`;
- Framework M1-M4 final: `56369da33dc5f48fc9ac071fd122fde4b35bd8c9`.

Do not run M5 formal work on the M1-M4 branches.

## Mandatory read order

Framework:

1. `AGENTS.md`
2. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/dtc_l1/m5/M5_V1_APPROVAL.md`
4. `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md`
5. `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`
6. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`
7. `docs/dtc_l1/m5/M5_GRAPHICS_PREP.md`
8. this file
9. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`
10. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
11. final M4 review pack and completion-recovery evidence as regression context

Core:

12. `AGENTS.md`
13. `docs/dtc_l1/DTC_L1_SPEC.md`

`M5_V1_APPROVAL.md` supersedes the stale planning-status banner in the long matrix. The matrix body is the approved detailed v1 plan.

## Research objective

Do not optimize for the thesis' exact +22%/+30% numbers. The Goal is to establish the performance effect and causal chain of the already implemented DTC mechanism.

For weak/negative/unexpected performance, determine whether the cause is:

- implementation/modeling fidelity;
- workload/input fidelity;
- downstream/platform saturation;
- traffic side effect;
- compute-bound behavior;
- or genuine mechanism limitation.

Preserve valid negative results after diagnosis.

## Researcher-frozen M5 v1 choices

1. Figure 4.5 primary DTC configuration: **16KB logical Tag capacity + 80KB physical Cacheline Array**; IO PIB=256, OO PIB=128.
2. Figure 4.7 primary metric: new-miss lower-request commit through final lower-response completion; plotted as per-SM cycle average.
3. Figure 4.2 formal categories: PIB full, true Tag+Cacheline allocation failure, MSHR capacity/merge failure, Miss Queue/lower-capacity failure. Tag-bank arbitration is diagnostic only.

Do not reinterpret these without a researcher-decision handoff.

## Immediate execution — M5.0A

Execute `M5.0A Branch/anchor and reproducibility lock` exactly as defined in `M5_EXPERIMENT_MATRIX.md`:

- verify M5 branch ancestry;
- release build and all DTC CTests;
- LEGACY/PAPER_BASE/PAPER_IO/PAPER_OO VecAdd sentinel regression against M4;
- create `m5/FORMAL_ANCHOR.md`;
- create resumable formal-result registry keyed by source/config/workload/parser identity;
- calibrate safe host simulation concurrency from measured CPU/RAM use;
- emit `m5/handoffs/M5_0A_ANCHOR.md`;
- commit/push compact evidence;
- update `codex_handoff/LATEST_REPORT.md`;
- continue immediately to M5.0B when acceptance passes.

## Continuous authorized sequence

After each substage passes its acceptance criteria, continue automatically:

`M5.0A -> M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`.

Required major products:

- all ten thesis compute workloads source-resolved;
- Figure 4.2 compute stall reproduction;
- Figure 4.5 Base/IO/OO compute result;
- Figure 4.7 common average concurrent misses;
- Figure 4.8 logical sensitivity;
- Figure 4.9 physical sensitivity/deadlock pressure;
- Figure 4.10 PIB sensitivity;
- integrated causal classification;
- parallel graphics G0-G2 preparation status.

Terminal compute state:

`M5_COMPUTE_READY_FOR_REVIEW`.

## First workload-recovery priority

M5.0B must explicitly source-resolve:

- `gemv -> gemver?`;
- `gesu -> gesummv?`;
- `conv2d -> 2DConvolution/pb_2dconv?`.

Do not stop merely because a ready binary is missing. Search canonical source, rebuild scientifically equivalent wrappers where justified, extract PTX, validate output, and record provenance.

All ten compute workloads must receive deterministic input provenance. Select scale from canonical/standard datasets and Base-only full-load/work-amount evidence, never from which size gives the highest DTC speedup.

SpMV requires special fidelity investigation because the M4 `fidapm05` case did not reproduce the thesis-discussed Base PIB pressure.

## Problem handling — solve and continue

Follow `M5_PROBLEM_RESOLUTION_POLICY.md`.

Normally do **not** pause for:

- missing workload/input/wrapper;
- build/PTX-extraction failures;
- missing counter/parser;
- simulator assertion found during M5 workload bring-up;
- Base/IO/OO dynamic-count mismatch;
- timeout with diagnosable progress;
- poor or negative speedup;
- absent expected PIB/MSHR pressure;
- Tag-bank/downstream domination;
- source-backed implementation bug;
- stale formal data after a justified repair.

Instead create/update `implementation/M5_ISSUE_LOG.md`, reproduce/classify, repair or scientifically resolve, regress, invalidate affected formal data, and resume the same substage.

## Researcher-decision pause conditions

Pause only when the issue cannot be solved without a genuine research decision, including:

- changing frozen M0/M1-M4 architecture semantics;
- two scientifically different source-supported interpretations remain and the thesis cannot resolve them;
- a required compute algorithm cannot be source-verified/reconstructed without changing experiment meaning;
- a finding contradicts the researcher-frozen M5 metric/config interpretation;
- terminal `M5_COMPUTE_READY_FOR_REVIEW`.

Use `RESEARCHER_DECISION_REQUIRED` with compact evidence when such a boundary is reached.

## Graphics parallelism

Run graphics G0-G2 opportunistically in parallel with compute work when resources allow. Graphics preparation must not block compute M5 and must not modify/contaminate the compute formal behavior anchor.

Do not emit `GM-ALL-PAPER` unless all five thesis graphics workloads become source-backed and correctness-clean.

## Forbidden scope before compute review

Do not:

- change M0/M1-M4 architecture to chase speedup;
- select inputs by DTC benefit;
- hide/omit valid negative results;
- fold Tag-bank conflicts into Figure 4.2 Tag+Cacheline allocation failures;
- use heterogeneous occupancy proxies as Figure 4.7 concurrent misses;
- include `MODERN_OO_SECTOR` in Figures 4.2-4.10 paper-reproduction plots;
- claim C++ simulator object size as Figure 4.6 area;
- use graphics memory proxies as direct paper graphics results;
- begin post-review M5.7+ supplemental studies before compute review.
