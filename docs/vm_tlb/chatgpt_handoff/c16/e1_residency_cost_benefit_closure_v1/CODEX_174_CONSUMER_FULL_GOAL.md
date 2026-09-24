# CODEX 174-new — Operator-Family Closure + Residency Cost/Benefit Consumer Prep Full Goal V1

## Mode

GOAL MODE / CPU-only independent closure + next-stage prep

Suggested branch:
`hrl/c16-e1-residency-cost-benefit-consumer-174new-v1`

No GPU.
No simulator execution.
No trace capture.
No simulator mutation.

## Read first

Fetch and verify:

`hrl/c16-e1-residency-cost-benefit-closure-handoff-v1`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_residency_cost_benefit_closure_v1/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/e1_residency_cost_benefit_closure_v1/DESIGN.md`
3. `docs/vm_tlb/chatgpt_handoff/c16/e1_residency_cost_benefit_closure_v1/BUDGET_MATRIX_PRECONTRACT.json`
4. `docs/vm_tlb/chatgpt_handoff/c16/e1_residency_cost_benefit_closure_v1/STAGE_DECISION_PRECONTRACT.json`
5. this file

Accepted operator-family producer:
`hrl/c16-e1-operator-family-expansion-109-v1@eae1cc4d831ae8459da558cf1358bb8daf8d76e6`

Current operator-family consumer prep:
`hrl/c16-e1-operator-family-expansion-consumer-174new-v1@eb4e737e24c27d1908a2fdf43f465ed5e0cfc66f`

## Goal

Execute one large CPU-only Goal:

1. independently close operator-family producer raw evidence;
2. preserve its stage label separately;
3. verify the negative residual decomposition;
4. freeze/build the new residency cost/benefit consumer before producer data;
5. fetch new producer once after prep and consume if ready;
6. otherwise STOP READY.

No simulator run.

# Part A — operator-family independent closure

## A1. Direct raw consumption

Do not use producer summary JSON as calculation authority.

Consume:
- RAW_ORDER_run*.json
- all RAW_NATIVE_CONTROL/FAIR_* runs
- raw NCU BASE/SESSION/PROFILE
- raw metric query
- raw policy histories.

Build deterministic adapters only from raw evidence.
Preserve source SHA provenance.

## A2. Real-artifact canaries

At minimum:
- RAW_ORDER_run0
- CONTROL_UP28 run0
- FAIR_UP28 run0
- FAIR_GUD84 run0
- one GUD84 NCU profile.

Verify:
- natural gate->up->down order from raw authority;
- all 84 module identities;
- selected update attachment;
- requested/actual set-aside;
- no in-run reset;
- token/SHA closure.

## A3. Independent analysis

Recompute:
- role-only
- pairwise
- GUD84
- direct selected saving
- unselected FFN saving
- total FFN saving
- outside-FFN residual
- realization
- host API overhead
- stage label.

Producer label is cross-check only:
`OPERATOR_FAMILY_NOT_SUPPORTED`.

## A4. NCU

Independently consume exact 12-profile representative matrix.

Apply multi-pass rule:
- all PASS receipts identical in semantic/token/policy identity;
- BASE replayer pass count equals PASS receipt count.

Preserve non-additive metrics per-kernel.

## A5. FULLHINT trigger

Independently verify GUD84 material selected fraction <0.50 if raw evidence says so.

If trigger false:
require FULLHINT native/NCU evidence absent.

## A6. Finalize operator-family consumer pack

Complete:
`docs/vm_tlb/review_packs/C16_E1_OPERATOR_FAMILY_EXPANSION_CONSUMER_174NEW_V1/`

Add/fill:
- INDEPENDENT_ROLE_ONLY_ANALYSIS.json
- INDEPENDENT_PAIRWISE_ANALYSIS.json
- INDEPENDENT_ALL_FFN_ANALYSIS.json
- INDEPENDENT_RESIDUAL_DECOMPOSITION.json
- INDEPENDENT_CRITICAL_PATH.json
- INDEPENDENT_FULLHINT_GUD84.json
- PRODUCER_RAW_PROVENANCE_AUDIT.json
- REAL_ARTIFACT_CANARIES.json
- PRODUCER_MATCH_CHECK.json
- FINAL_DECISION.json
- NEXT_STEP_AUTHORIZATION.json.

Preserve no simulator authorization.

# Part B — freeze cost/benefit consumer before producer data

## B1. Budget matrix consumer

Use exact:
`BUDGET_MATRIX_PRECONTRACT.json`

Validate four requested budgets:
- 8 MiB
- 16 MiB
- 24 MiB
- full 33,947,648 B.

For each budget:
- runtime actual query-back frozen per budget;
- actual <= runtime max;
- exact 28 up_proj windows;
- hitRatio formula;
- matched CONTROL/FAIR;
- no in-run reset.

Do not infer alignment law.

## B2. Top-level semantic consumer

Implement runtime-derived top-level module authority for:
- input_layernorm
- self_attn
- post_attention_layernorm
- mlp
- final norm/output if available.

Do not assume unavailable names.

Fail closed on:
- overlapping top-level ranges
- duplicate/missing expected occurrence
- cross-run order drift
- semantic SHA drift.

## B3. FFN child consumer

Require all 84 gate/up/down child timings in every condition.

Preserve:
- role/layer/index
- input/output SHA
- module/backend
- timing.

## B4. Run-aligned decomposition consumer

Compute exactly:
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

Use same-run D1-D3 raw rows.

No median-of-medians substitution.

Ratios unclamped.

## B5. Decomposition qualification

Implement:
abs(median UNEXPLAINED_RESIDUAL) <=0.10 ms

as frozen measurement-closure rule.

Do not silently force incomplete decomposition to PASS.

## B6. NCU consumer

Freeze exact 8-profile primary matrix:

16 MiB:
- L0 up CONTROL/FAIR
- L0 self_attn CONTROL/FAIR

Full:
- L0 up CONTROL/FAIR
- L0 self_attn CONTROL/FAIR

Require runtime metric query and complete policy history.

Preserve per-kernel non-additive metrics.

## B7. Stage decision

Implement STAGE_DECISION_PRECONTRACT exactly.

No simulator auto-authorization.

## B8. Synthetic tests

Cover at least:
- wrong budget
- runtime query-back drift
- wrong hitRatio
- missing reset
- top-level overlap
- missing self_attn/mlp occurrence
- FFN child missing
- token/SHA drift
- run-aligned accounting bug
- nested double-counting
- residual sign
- >0.10 ms unexplained residual
- NCU multi-pass mismatch.

# Part C — prep review pack

Create:

`docs/vm_tlb/review_packs/C16_E1_RESIDENCY_COST_BENEFIT_CLOSURE_CONSUMER_174NEW_V1/`

At minimum:

- UPSTREAM_OPERATOR_FAMILY_CLOSURE_AUDIT.json
- OPERATOR_FAMILY_RESIDUAL_AUDIT.json
- BUDGET_CONSUMER_CONTRACT.json
- TOPLEVEL_SEMANTIC_CONSUMER_CONTRACT.json
- FFN_CHILD_CONSUMER_CONTRACT.json
- DECOMPOSITION_CONSUMER_CONTRACT.json
- REPRESENTATIVE_NCU_CONSUMER_CONTRACT.json
- CONSUMER_TESTS.tsv
- INDEPENDENT_BUDGET_EFFECT_ANALYSIS.json when producer ready
- INDEPENDENT_RESIDUAL_LOCALIZATION.json when producer ready
- INDEPENDENT_CRITICAL_PATH.json when producer ready
- PRODUCER_MATCH_CHECK.json
- FINAL_DECISION.json
- NEXT_STEP_AUTHORIZATION.json
- SHA256SUMS.

# Part D — one-shot producer fetch

Expected:
`hrl/c16-e1-residency-cost-benefit-closure-109-v1`

After prep/tests fetch once.

If producer complete:
- consume raw evidence;
- independently close;
- update scientific log;
- commit/push/verify/clean;
- STOP_FOR_CHATGPT_REVIEW.

If absent/incomplete:
- commit/push prep;
- verify/clean;
- STOP:

`READY_FOR_E1_RESIDENCY_COST_BENEFIT_109`

No polling.

# Boundary

No GPU.
No Accel-Sim.
No GPGPU-Sim mutation.
No NVBit.
No trace capture.
No mechanism implementation/simulation.

Routine parser/schema/Git issues:
solve-and-continue.

Small correctness-preserving fixes:
repair inside this Goal.

Stop early only for a true scientific authority/identity contradiction.
