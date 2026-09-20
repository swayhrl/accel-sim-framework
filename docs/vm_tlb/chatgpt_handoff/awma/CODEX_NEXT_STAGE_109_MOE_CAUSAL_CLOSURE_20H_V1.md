# CODEX NEXT STAGE — 109 MoE Causal Closure + Scale Phase Diagram 20h V1

Date: 2026-09-20

Mode:

`GOAL MODE / 20H UNATTENDED / solve-and-continue`

Node:

`109 / RTX4080`

Stage:

`AWMA_109_MOE_CAUSAL_CLOSURE_AND_SCALE_PHASE_DIAGRAM_20H_V1`

Coordination branch:

`hrl/awma-109-moe-causal-closure-20h-handoff-v1`

Accepted parent:

`hrl/awma-109-moe-routing-skew-20h-v1 @ ed645f3aec0fe4623e1895dee2754ece0ab063f1`

Suggested execution branch:

`hrl/awma-109-moe-causal-closure-scale-20h-v1`

Read first:

1. `docs/vm_tlb/chatgpt_handoff/awma/REVIEW_109_MOE_SKEW_V1_2026-09-20.md`
2. accepted MoE skew V1 review pack
3. accepted Q30 S2/T2048 and S0/T128 state authorities
4. this Goal

## 0. Fresh 20h clock

At actual launch:

- START_UTC = now
- DEADLINE_UTC = START + 20h
- NO_NEW_GPU_SCIENCE_AFTER = DEADLINE - 2h

Do not inherit older deadlines.

Write:

`CAMPAIGN_TIME_AUTHORITY.json`

## 1. Shared frozen authority

Primary:

`Q30 S2/T2048 exact state @ ee67225edc8fc5868de585d38e0391cbeb755d9f`

Reuse exact accepted expert harness from:

`ed645f3...`

Freeze:

- model revision;
- target layer;
- hidden-state SHA;
- gate/router;
- expert modules/weights;
- top-k;
- precision/backend;
- grouping/combine semantics.

No package/runtime/model upgrade.

## 2. Scientific DAG

```text
C0 accepted-data synthesis
 |
 +--> C1 independent degree realizations
 |
 +--> C2 randomized interleaved timing
 |
 +--> C3 token-population phase diagram
 |      |
 |      +--> C4 component/per-expert decomposition
 |
 +--> C5 existing-backend scope audit/holdout
 |
 +--> C6 deterministic cross-layer holdout

C7 secondary E1 resource closure   independent / low priority
```

Task-local failures must not terminate independent READY tasks.

## 3. C0 — Freeze accepted baseline

Reuse without rerun:

- natural S2 histogram;
- beta=0.25/0.50/0.75 target histograms;
- balanced endpoint;
- P/U controls;
- S0/T128 N/P/U;
- expert-shape microbench.

Create one compact accepted summary:

`MOE_ACCEPTED_BASELINE_SUMMARY.tsv`

Include:

- histogram CV/min/p50/p95/max;
- assignment count;
- active expert count;
- timing median;
- scope/label.

## 4. C1 — Multiple independent degree realizations at fixed histogram

Purpose:

separate histogram skew from one particular token-to-expert graph realization.

Use the exact already-frozen target column degrees for:

- beta=0.25
- beta=0.50
- beta=0.75
- balanced endpoint

For each histogram generate 5 deterministic but independent exact realizations:

`R0..R4`

Seed derivation must be pre-frozen, e.g.:

`SHA256(authority_sha || beta || realization_index)`.

Every realization must satisfy:

- row degree = 8;
- exact target column degrees;
- no duplicate expert per token;
- exact same active expert set;
- total assignments=16384;
- same hidden states;
- same per-token routing-weight value vector by rank;
- same expert modules/backend.

Do NOT derive seeds from timing.

Save every selected-expert tensor SHA.

Output:

`E3_DEGREE_REALIZATION_AUTHORITY.json`

## 5. C2 — Randomized/interleaved native timing

Purpose:

remove long-block temporal/clock drift as a confound.

Conditions:

- natural N
- one pre-frozen histogram-preserving P reference
- beta=0.25 R0..R4
- beta=0.50 R0..R4
- beta=0.75 R0..R4
- balanced R0..R4

Use a pre-frozen randomized block schedule.

Minimum:

- 10 blocks;
- every condition appears once per block;
- block order derived from a deterministic seed fixed before timing.

For each condition occurrence:

- synchronize before measured region;
- one expert-region CUDA-event measurement after sufficient campaign-level warmup.

Do not run all measurements for one condition consecutively.

Record:

- block;
- position;
- condition;
- measured ms;
- GPU clock/temperature snapshot if cheap and nonintrusive.

Primary statistics:

- per-condition median;
- paired within-block difference vs N;
- realization-to-realization spread;
- histogram-level aggregate.

Output:

`E3_INTERLEAVED_TIMING.tsv`

No causal claim until this closes.

## 6. C3 — Token-population scale phase diagram

Question:

when does balancing/skew reduction help or hurt as token population changes?

Use exact S2 accepted hidden-state prefix:

`M = {128, 256, 512, 1024, 2048}`

For each M:

1. take first M exact hidden rows;
2. execute the same frozen router/gate on those rows;
3. freeze natural selected_experts/routing_weights;
4. freeze the natural active expert set for that M;
5. compute natural histogram;
6. construct balanced U within that M-specific natural active set;
7. construct beta=0.5 midpoint histogram.

Requirements:

- same top-k=8;
- exact M*8 total assignments;
- row distinctness;
- per-token routing-weight values preserved by rank;
- no new model execution outside the frozen layer semantics.

For each M run:

- N;
- 3 histogram-preserving P order controls;
- beta=0.5 with 3 independent exact degree realizations;
- balanced with 3 independent exact degree realizations.

Use interleaved timing within each M.

Record:

- active expert count;
- mean assignments/active expert;
- CV;
- p95/max;
- timing.

Output:

`E3_SCALE_PHASE_DIAGRAM.tsv`

Primary desired result:

identify whether there is a crossover region where balancing changes from neutral/harmful to beneficial.

S0/T128 remains a separate natural-input holdout and must not be silently merged with the S2-prefix M128 control.

## 7. C4 — Component and per-expert timing decomposition

Purpose:

determine which exact semantic-preserving stage explains the skew sensitivity.

Keep the normal uninstrumented expert-region timing as performance authority.

Create a separate DIAGNOSTIC instrumented harness.

Time components using CUDA events/ranges without changing math:

- route-mask/index extraction;
- gather/current_state construction;
- expert module compute;
- routing-weight multiply;
- scatter/index_add/combine.

Also collect per-active-expert:

- token count;
- gather duration;
- expert compute duration;
- combine duration.

Do not synchronize inside the normal performance path.

Instrumentation may synchronize in the diagnostic path only if explicitly labeled:

`INSTRUMENTED_COMPONENT_DIAGNOSTIC`.

Run component diagnostics for:

- natural M2048;
- beta=0.50 representative realization;
- balanced representative realization;
- natural M128/M512/M1024 scale points where useful.

Compute:

```text
SUM_EXPERT_COMPUTE
SUM_GATHER
SUM_COMBINE
REGION_RESIDUAL
```

Do not force exact additivity if overlap/event semantics prevent it.

Output:

`E3_COMPONENT_BREAKDOWN.tsv`
`E3_PER_EXPERT_DIAGNOSTIC.tsv`
`E3_COMPONENT_INTERPRETATION.md`

## 8. C4b — Expert-shape generality

The prior curve used expert 0 only.

Add two deterministic validation experts based on workload structure, not timing:

- expert with maximum natural assignment count;
- median-ID active expert.

Reuse the same pre-frozen shape set:

`M={1,4,14,205,793,1602}`

or clip only if an exact module shape restriction requires it.

Run 9 native samples per shape.

Purpose:

check whether the expert-0 shape curve is representative across expert weights.

Output:

`E3_EXPERT_SHAPE_MULTIEXPERT.tsv`

## 9. C5 — Existing-backend scope audit

Question:

is skew sensitivity specific to the frozen eager expert loop?

Audit the current environment only.

Look for already-installed and already-compatible semantics-preserving MoE/grouped-GEMM paths, e.g.:

- existing model/runtime internal grouped expert op;
- installed vLLM/sglang grouped expert primitive;
- installed Triton grouped-GEMM helper;
- PyTorch grouped-MoE primitive.

Do NOT install or upgrade packages.

Produce:

`EXISTING_MOE_BACKEND_AUDIT.md`

If no acceptable existing backend:

`NO_EXISTING_GROUPED_BACKEND_HOLDOUT`

and continue.

If one exists:

1. bind exact source/binary/version;
2. use same expert weights and exact selected_experts/routing_weights;
3. prove numerical equivalence against frozen harness for N;
4. only then run N / beta=0.5 / balanced at M2048 and one smaller M.

Label:

`IMPLEMENTATION_BACKEND_HOLDOUT`

Do not modify the accepted eager-harness result.

## 10. C6 — Deterministic cross-layer holdout

Purpose:

avoid a single-layer characterization.

Inspect exact Q30 architecture.

Pre-freeze two additional MoE layers by structural rule before timing:

- earliest eligible MoE layer other than primary target;
- latest eligible MoE layer other than primary target.

Do not choose layers based on observed skew/performance.

For each selected layer:

- capture exact S2/T2048 layer input from the frozen full-model execution;
- freeze hidden-state SHA;
- run exact router;
- materialize exact expert harness from the same source class;
- N canary must pass;
- run N, 3 P controls, beta=0.5, balanced.

No full skew continuum required.

Output:

`E3_CROSS_LAYER_HOLDOUT.tsv`

If architecture/state capture cannot be done without changing runtime, record task-local scoped stop and continue.

## 11. C7 — Secondary E1 resource closure

Low priority.

Reuse proven isolated NCU path.

If time remains, produce one compact comparable resource table for down_proj:

- raw M1/M256;
- AWQ deployed M1/M256;
- AWQ M1023/M1024.

No new E1 science expansion.

Output:

`E1_DOWNPROJ_RESOURCE_CLOSURE.tsv`

## 12. Interpretation gates

Do NOT start mechanism design inside this Goal.

At closeout classify the evidence into one of:

- `SKEW_EFFECT_ROBUST_AND_COMPONENT_LOCALIZED`
- `SKEW_EFFECT_ROBUST_BUT_IMPLEMENTATION_SPECIFIC`
- `SKEW_EFFECT_SCALE_DEPENDENT_NO_SINGLE_MECHANISM`
- `SKEW_EFFECT_NOT_ROBUST_AFTER_REALIZATION_INTERLEAVING`

Mechanism work requires a later ChatGPT review.

## 13. Solve-and-continue

Engineering tasks are authorized:

- exact b-matching/max-flow realization;
- interleaved scheduler;
- component event instrumentation;
- layer-state capture;
- existing-backend adapter.

Missing helper is not a scientific STOP.

Task-local scientific STOP only when continuation requires:

- new model revision;
- changed expert math/weights/backend for an accepted comparison;
- weakened numerical contract;
- synthetic route presented as natural.

## 14. Final two-hour reserve

At NO_NEW_GPU_SCIENCE_AFTER:

- no new GPU target;
- finish safely closable work;
- transfer;
- hash;
- node164 ACK;
- report;
- commit/push;
- remote verify;
- clean;
- release lock.

## 15. Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/MOE_CAUSAL_CLOSURE_SCALE_20H_109_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_109_MOE_CAUSAL_CLOSURE_SCALE_20H_V1/`

Minimum:

```text
README.md
SOURCE_ANCHORS.md
CAMPAIGN_TIME_AUTHORITY.json
PIPELINE_STATE.json
MOE_ACCEPTED_BASELINE_SUMMARY.tsv
E3_DEGREE_REALIZATION_AUTHORITY.json
E3_INTERLEAVED_TIMING.tsv
E3_SCALE_PHASE_DIAGRAM.tsv
E3_COMPONENT_BREAKDOWN.tsv
E3_PER_EXPERT_DIAGNOSTIC.tsv
E3_COMPONENT_INTERPRETATION.md
E3_EXPERT_SHAPE_MULTIEXPERT.tsv
EXISTING_MOE_BACKEND_AUDIT.md
E3_CROSS_LAYER_HOLDOUT.tsv
E1_DOWNPROJ_RESOURCE_CLOSURE.tsv
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

Success marker:

`AWMA_109_MOE_CAUSAL_CLOSURE_AND_SCALE_PHASE_DIAGRAM_20H_V1_COMPLETE_WITH_SCOPE`

Then STOP.
