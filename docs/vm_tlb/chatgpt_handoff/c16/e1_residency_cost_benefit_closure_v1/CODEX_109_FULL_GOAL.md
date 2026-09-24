# CODEX 109 — C16 E1 Residency Cost/Benefit Closure Full Goal V1

## Mode

GOAL MODE / solve-and-continue

Suggested branch:
`hrl/c16-e1-residency-cost-benefit-closure-109-v1`

Recommended execution parent:
`hrl/c16-e1-operator-family-expansion-109-v1@eae1cc4d831ae8459da558cf1358bb8daf8d76e6`

## Read first

Fetch and verify:

`hrl/c16-e1-residency-cost-benefit-closure-handoff-v1`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_residency_cost_benefit_closure_v1/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/e1_residency_cost_benefit_closure_v1/DESIGN.md`
3. `docs/vm_tlb/chatgpt_handoff/c16/e1_residency_cost_benefit_closure_v1/BUDGET_MATRIX_PRECONTRACT.json`
4. `docs/vm_tlb/chatgpt_handoff/c16/e1_residency_cost_benefit_closure_v1/STAGE_DECISION_PRECONTRACT.json`
5. this file
6. `docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

## Goal

Execute one bounded real-hardware closure Goal:

1. sweep global persistence budget for all 28 up_proj;
2. instrument top-level model components;
3. preserve all 84 FFN child timings;
4. localize the operator-family negative residual;
5. profile representative up_proj and self-attention points;
6. close the residency system case.

No simulator, trace capture, or mechanism implementation.

## Stage 1 — freeze top-level semantic authority

Runtime-discover the actual Qwen layer structure.

Attempt to instrument, per layer:
- input_layernorm
- self_attn
- post_attention_layernorm
- mlp

Also attempt:
- final model norm
- lm_head / output projection.

Do not assume names if runtime differs.

For every accepted top-level category:
- freeze module identity;
- freeze natural order;
- require one expected occurrence/layer/decode where applicable;
- preserve exact token/SHA identity.

Nested rule:
- MLP top-level contains gate/up/down;
- never sum MLP top-level with its children in whole-step accounting.

## Stage 2 — frozen budget matrix

Use exactly:

`BUDGET_MATRIX_PRECONTRACT.json`

Budgets:
- 8 MiB
- 16 MiB
- 24 MiB
- full qweight request 33,947,648 B

For each requested budget:
- query runtime actual set-aside;
- freeze actual query-back for all fresh runs of that budget;
- require actual <= runtime max;
- do not infer a generic rounding law.

Selected family:
all 28 up_proj qweight regions only.

## Stage 3 — matched CONTROL/FAIR pairs

For every budget B:

CONTROL:
- exact 28 up_proj update points
- exact full qweight windows
- hitRatio=min(1, B/(28*qweight_bytes))
- NORMAL/NORMAL
- nonpersisting

FAIR:
- identical update points/windows/hitRatio
- PERSISTING/STREAMING

Reset only before/after full condition.
No in-run reset.

## Stage 4 — native runs

Every condition:
- 7 fresh processes;
- accepted prefix;
- tokens [23578,11,323,3950];
- exact module/backend identity;
- all 84 FFN child timings;
- all qualified top-level timings;
- D0-D3 decode-step timing;
- complete policy history;
- per-update CPU API duration.

No inner-loop synchronize.

All top-level and child events must be present in both CONTROL and FAIR so instrumentation is matched.

## Stage 5 — run-aligned decomposition

For stable D1-D3 compute from same-run raw rows:

DIRECT_UP_SAVING
GATE_SAVING
DOWN_SAVING
TOTAL_FFN_PROJECTION_SAVING
MLP_TOP_SAVING
MLP_INTERNAL_RESIDUAL
SELF_ATTN_SAVING
NORM_SAVING
FINAL_STAGE_SAVING
OBSERVED_DECODE_SAVING
ACCOUNTED_TOPLEVEL_SAVING
UNEXPLAINED_RESIDUAL

Use DESIGN formulas exactly.

No ratio clamping.

Negative category saving means that category became slower.
Do not rename any negative value "cache slowdown" unless supported directly by the measured category.

## Stage 6 — decomposition qualification

Require:
- stable top-level call identities;
- no overlap among top-level accounting categories;
- exact expected occurrence matrix;
- abs(median UNEXPLAINED_RESIDUAL) <=0.10 ms.

If not:
mark TOPLEVEL_DECOMPOSITION_INCOMPLETE and preserve residual.

Do not force closure.

## Stage 7 — local/system effects

Per up_proj D3:
MATERIAL_LOCAL_UP:
>=5% benefit and > combined dispersion.

Whole stable D1-D3:
MATERIAL_SYSTEM:
>=2% benefit and > combined dispersion.

Also report positive-beyond-dispersion sub-2% points.

Apply STAGE_DECISION_PRECONTRACT exactly.

## Stage 8 — representative NCU

Re-query installed NCU metrics/version.

Profile:

16 MiB:
- L0 up D3 CONTROL / FAIR
- L0 self_attn D3 CONTROL / FAIR

Full:
- L0 up D3 CONTROL / FAIR
- L0 self_attn D3 CONTROL / FAIR

Total 8 profiles.

Use:
--replay-mode application
--cache-control none

Preserve complete natural policy history.

Collect:
- L1/TEX bytes
- L2 bytes
- DRAM bytes
- kernel duration
- L2 read hit/miss sectors
- DRAM read bytes
- long scoreboard
- LSU utilization
- active warps
when available.

For multi-kernel self_attn:
- additive metrics may sum;
- percentages/stalls/utilization remain per-kernel.

## Stage 9 — interpretation

Explicitly answer:

1. Which budget preserves the strongest up_proj local benefit?
2. Does reducing budget improve whole-decode outcome?
3. Where does the UP28 negative residual localize?
4. Is self_attn slower under persistence?
5. Is MLP top-level saving smaller than the projection-level sum?
6. Do norms/final stages contribute materially?
7. How much residual remains unexplained?
8. Does any budget cross 2%?
9. If no budget crosses 2%, is the system case weak or is a specific measurable interference target exposed?
10. Should the next step be simulator mechanism, mechanism revision, or stop?

Do not auto-authorize simulator work.

## Stage 10 — review pack

Create:

`docs/vm_tlb/review_packs/C16_E1_RESIDENCY_COST_BENEFIT_CLOSURE_109_V1/`

with all DESIGN-required files and raw evidence.

Update scientific log.

Then:
SHA256SUMS
-> commit
-> push
-> fetch-back/remote verify
-> clean
-> release GPU lock
-> STOP_FOR_CHATGPT_REVIEW

## Boundaries

Forbidden:
- Accel-Sim execution
- GPGPU-Sim mutation
- NVBit
- trace capture
- mechanism implementation
- mechanism simulation

Routine PyTorch/CUDA/NCU/parser/Git issues:
solve-and-continue.

Small correctness-preserving fixes:
repair inside this Goal.

STOP early only for real semantic/model/policy identity failure, GPU/runtime corruption, or scientific contract change.
