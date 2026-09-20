# CODEX NEXT STAGE — 109 20h MoE Routing-Skew Characterization V1

Date: 2026-09-20

Mode:
`GOAL MODE / 20H UNATTENDED / solve-and-continue`

Node:
`109 / RTX4080`

Stage:
`AWMA_109_MOE_ROUTING_SKEW_CHARACTERIZATION_20H_V1`

Coordination branch:
`hrl/awma-109-moe-skew-20h-handoff-v1`

Accepted parent:
`hrl/awma-109-20h-unattended-e1-e3-v3r1 @ c766a9d8ede59ef4b81ffd151ac49c839495a115`

Suggested execution branch:
`hrl/awma-109-moe-routing-skew-20h-v1`

Read:
1. `REVIEW_109_V3R1_MOE_NEXT_2026-09-20.md`
2. accepted V3R1 review pack
3. accepted Q30 S2/T2048 state authority
4. this Goal

## 0. Fresh campaign clock

At actual launch:
- START_UTC = now
- DEADLINE_UTC = START + 20h
- NO_NEW_GPU_SCIENCE_AFTER = DEADLINE - 2h

Write `CAMPAIGN_TIME_AUTHORITY.json`.

Do not inherit the previous campaign deadline.

## 1. Shared frozen authority

Primary authority:
`Q30 S2/T2048 Prefill exact state/replay @ ee67225edc8fc5868de585d38e0391cbeb755d9f`

Reuse the accepted V3R1 exact expert harness.

Require exact:
- hidden-state SHA;
- target layer;
- gate/router implementation;
- expert modules/weights;
- top-k=8;
- backend/precision/residency;
- expert combine semantics.

Natural state:
- M=2048
- total assignments=16384
- natural active set = accepted V3R1 active set (93 experts in the accepted canary)
- N/P canary bitwise contracts remain accepted.

No change to model revision/runtime.

## 2. Scientific DAG

```text
A0 freeze natural histogram and harness
 |
 +--> A1 multi-P order sensitivity
 |
 +--> A2 U-active order sensitivity
 |
 +--> A3 fixed-active-set skew continuum
 |      |
 |      +--> A4 expert-granularity microbenchmark/resource diagnosis
 |
 +--> A5 S0/T128 independent holdout

B1 E1 down_proj resource profile      independent secondary
B2 profiler protocol sanity           depends on working NCU
```

Task-local failure must not stop independent READY work.

## 3. A0 — Freeze natural histogram

From exact natural selected_experts:

Produce:
- per-expert assignment counts for all 128 experts;
- active-set list;
- min/p25/median/p75/p95/max over active counts;
- mean/std/CV;
- entropy/Gini if implemented deterministically;
- total assignments.

Save:
`E3_NATURAL_HISTOGRAM.tsv`
`E3_NATURAL_HISTOGRAM_SUMMARY.json`

Do not select controls based on timing.

## 4. A1 — Multi-permutation P control

Purpose:
measure execution variation caused by token/order/layout while expert histogram is exactly fixed.

Create 5 deterministic token permutations P0..P4.

Seed derivation must be frozen before timing, for example SHA256 of:
`authority_sha || "P" || index`.

For each P_i:
- jointly permute hidden rows;
- selected_experts rows;
- routing_weights rows;
- execute exact harness;
- inverse-permute output;
- require bitwise equality with N;
- require exact expert histogram unchanged.

Timing:
- 3 warmups;
- 9 measured expert-region repetitions;
- retain all samples.

Output:
`E3_P_MULTI_CONTROL.tsv`

Report distribution of P medians:
- min/max;
- median;
- spread.

Do not call N-vs-single-P difference a routing-balance effect.

## 5. A2 — U-active order sensitivity

Reuse the accepted deterministic balanced U-active assignment.

Keep its exact expert-count histogram fixed.

Create 5 deterministic token-row permutations U0..U4 by jointly permuting:
- hidden;
- balanced selected_experts;
- routing_weights.

No inverse-output semantic equivalence claim to N is possible because U is synthetic.

Require for every U_i:
- same balanced expert histogram;
- same active set;
- max-min active count=1;
- total assignments=16384;
- per-token 8 distinct expert IDs;
- routing-weight values move with the token.

Timing:
- 3 warmups;
- 9 repetitions.

Output:
`E3_U_ORDER_CONTROL.tsv`

This estimates ordering variance inside the balanced synthetic condition.

## 6. A3 — Fixed-active-set skew continuum

Question:
with the active expert set and total work fixed, how does assignment-count skew affect expert-region time?

Use:
- natural active set A only;
- M=2048;
- k=8;
- total assignments=16384;
- same hidden states;
- same routing-weight values per token/rank;
- same expert modules/backend.

Let:
- `h_N` = natural active-expert count vector;
- `h_U` = balanced active-set count vector with max-min <=1.

Pre-freeze skew levels:

`beta = {0.25, 0.50, 0.75}`

Target count vector:
`h_beta = (1-beta)*h_N + beta*h_U`

Convert to integer counts with a deterministic largest-remainder rule preserving:
- sum=16384;
- nonnegative counts;
- same active set.

Then construct selected_experts as a deterministic bipartite degree-realization problem:
- every token row degree=8;
- every active expert column degree=target count;
- no duplicate expert within a token.

Use deterministic max-flow/b-matching or another exact construction.
Engineering difficulty is solve-and-continue, not a scientific STOP.

For each beta:
- verify exact target column counts;
- verify row distinctness;
- save construction SHA;
- label `SYNTHETIC_ROUTING_SKEW_CONTROL`.

For each beta, run 3 deterministic token-order permutations after construction, each with 9 timing samples.

Also include accepted endpoints:
- beta=0 natural/P controls;
- beta=1 U-active/U-order controls.

Outputs:
`E3_SKEW_CONTINUUM_CONSTRUCTION.json`
`E3_SKEW_CONTINUUM_TIMING.tsv`

Primary descriptive analysis:
- expert-count CV vs expert-region median;
- p95/max expert count vs time;
- ordering spread at fixed histogram.

Do not fit a causal model beyond what the controls support.

## 7. A4 — Expert granularity efficiency diagnostic

Purpose:
determine whether skew affects time through expert GEMM granularity/utilization.

Using the natural active-count histogram, derive token-count shapes by a pre-frozen rule:

```text
Q = unique({
 min_nonzero,
 p25_nearest,
 median_nearest,
 p75_nearest,
 p95_nearest,
 max
})
```

Select one fixed expert module before timing:
- use expert ID 0 if it is in the accepted natural active set;
- otherwise smallest active expert ID.

For each M in Q:
- use the first M accepted hidden rows as a controlled expert input;
- execute that same expert MLP module;
- no claim of natural routing semantics;
- label `CONTROLLED_EXPERT_SHAPE_MICROBENCH`.

Timing:
- 3 warmups;
- 9 native samples.

Record:
- M;
- module execution time;
- time/token;
- kernel sequence/shapes.

### Resource profiling

Use the proven isolated NCU workflow.

Profile representative Q shapes:
- smallest;
- median;
- p95;
- max.

Discover installed metrics; prefer:
- DRAM/L2/L1 bytes;
- SM/tensor/math utilization;
- occupancy/warp activity;
- instruction evidence.

Native timing remains uninstrumented.

Outputs:
`E3_EXPERT_SHAPE_CURVE.tsv`
`E3_EXPERT_SHAPE_NCU.tsv`
`E3_EXPERT_SHAPE_INTERPRETATION.md`

## 8. A5 — S0/T128 independent holdout

Use existing accepted Q30 S0 semantic/replay authority:
`ba4358b8059be4fb5756f49852e50ecfe7dea9a3`

and accepted target qualification where needed:
`acbda39f5714cedb0e8b88ec32b07b4db2845885`.

Use the same semantic target layer/region as far as the frozen authority supports.

Do not regenerate S0 if exact state authority exists.

Materialize the same exact experts harness under S0.

Run:
- N
- 3 histogram-preserving P permutations
- U-active balanced within S0 natural active set

Require N/P canaries exactly as in S2.

Timing:
- 3 warmups;
- 9 repetitions.

Label U synthetic.

Output:
`E3_S0_T128_HOLDOUT.tsv`

Purpose:
test whether the skew/granularity trend survives at a much smaller natural token population.

## 9. B1 — Secondary E1 resource explanation

The isolated NCU path is now proven to work.

Complete a bounded resource profile for down_proj:

- raw M1
- AWQ deployed M1
- raw M256
- AWQ deployed M256
- AWQ M1023
- AWQ M1024

If practical, add M3 decomposition paths:
- B one-time-dequant matmul M256/M1024
- C per-call-dequant matmul M256/M1024

Use exact isolated replay/NVTX process.

Before metrics:
- prove selector canary for each distinct path class.

Discover installed metrics rather than inventing names.

Output:
`E1_DOWNPROJ_RESOURCE_PROFILE.tsv`
`E1_DOWNPROJ_RESOURCE_INTERPRETATION.md`

This is secondary; do not delay A1-A5 excessively.

## 10. B2 — Protocol sanity

Only after B1 is stable.

Use one exact AWQ down_proj M256 target.

Compare the already-used supported cache-control protocols with the same metric set.

Claim:
`PROFILER_PROTOCOL_SENSITIVITY`

Do not call cache control a TLB flush.

## 11. Scheduler / solve-and-continue

Engineering problems are authorized:
- deterministic flow construction;
- harness wrappers;
- parsers;
- isolated NCU replay;
- input slicing;
- receipts/transfers.

A task-local scientific failure freezes only that task.

Before any final COMPLETE marker:
- all A1-A5 must be ACCEPTED or have a concrete scientific/authority reason;
- missing helper/script is not a valid skip reason;
- no READY task may remain.

## 12. Final two-hour reserve

At NO_NEW_GPU_SCIENCE_AFTER:
- no new GPU experiment;
- finish safely closable work;
- transfer;
- hash;
- analyze;
- node164 ACK;
- report;
- commit/push;
- remote verify;
- clean;
- release lock.

## 13. Forbidden

No:
- new model download;
- runtime/model revision change;
- expert math/backend change;
- model-quality claim for synthetic routes;
- architecture mechanism;
- detailed SASS/NVBit campaign by default;
- unbounded layer/shape sweep.

## 14. Deliverables

Report:
`docs/vm_tlb/codex_handoff/awma/MOE_ROUTING_SKEW_CHARACTERIZATION_20H_109_V1_REPORT.md`

Review pack:
`docs/vm_tlb/review_packs/AWMA_109_MOE_ROUTING_SKEW_CHARACTERIZATION_20H_V1/`

Minimum:
- README.md
- SOURCE_ANCHORS.md
- CAMPAIGN_TIME_AUTHORITY.json
- PIPELINE_STATE.json
- E3_NATURAL_HISTOGRAM.tsv
- E3_NATURAL_HISTOGRAM_SUMMARY.json
- E3_P_MULTI_CONTROL.tsv
- E3_U_ORDER_CONTROL.tsv
- E3_SKEW_CONTINUUM_CONSTRUCTION.json
- E3_SKEW_CONTINUUM_TIMING.tsv
- E3_EXPERT_SHAPE_CURVE.tsv
- E3_EXPERT_SHAPE_NCU.tsv
- E3_EXPERT_SHAPE_INTERPRETATION.md
- E3_S0_T128_HOLDOUT.tsv
- E1_DOWNPROJ_RESOURCE_PROFILE.tsv
- E1_DOWNPROJ_RESOURCE_INTERPRETATION.md
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Success marker:
`AWMA_109_MOE_ROUTING_SKEW_CHARACTERIZATION_20H_V1_COMPLETE_WITH_SCOPE`

Then STOP. Do not automatically design a MoE scheduling mechanism.
