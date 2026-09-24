# CODEX 109 — C16 E1 Operator-Family Expansion Full Goal V1

## Mode

GOAL MODE / solve-and-continue

Suggested branch:

`hrl/c16-e1-operator-family-expansion-109-v1`

Recommended execution parent:

`hrl/c16-e1-coverage-scaling-109-v1@18acd7dcc10118c68b450d226a8e7ca80c51ad72`

## Read first

Fetch and verify:

`hrl/c16-e1-operator-family-expansion-handoff-v1`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_operator_family_expansion_v1/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/e1_operator_family_expansion_v1/COVERAGE_PRODUCER_PRE_RESUME_AUDIT.md`
3. `docs/vm_tlb/chatgpt_handoff/c16/e1_operator_family_expansion_v1/DESIGN.md`
4. `docs/vm_tlb/chatgpt_handoff/c16/e1_operator_family_expansion_v1/CONDITION_MATRIX_PRECONTRACT.json`
5. `docs/vm_tlb/chatgpt_handoff/c16/e1_operator_family_expansion_v1/STAGE_DECISION_PRECONTRACT.json`
6. this file
7. `docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

## Goal

Execute one complete real-hardware operator-family expansion Goal.

No Accel-Sim.
No GPGPU-Sim mutation.
No trace capture.
No mechanism implementation.

Complete:

1. natural FFN call-order authority;
2. 14-condition role/pair/all-family matrix;
3. all-84 FFN timing in every condition;
4. run-aligned residual decomposition;
5. bounded representative NCU;
6. conditional GUD84 FULLHINT;
7. stage closure.

Do not STOP between ordinary stages.

---

## Stage 1 — freeze natural call order

Using the accepted Qwen2.5-7B AWQ full-model path:

- accepted S2_TEXT 2048 prefix;
- four deterministic greedy decode steps;
- tokens must remain `[23578,11,323,3950]`.

Run a no-policy authority probe.

Record the exact natural call sequence of all FFN projections for:

- PREFILL
- D0
- D1
- D2
- D3

across:
- 28 layers
- gate_proj
- up_proj
- down_proj.

Require the sequence to reproduce across fresh processes.

Do not impose a manually sorted order if runtime order differs.

Persist:
`NATURAL_FFN_CALL_ORDER.json`

---

## Stage 2 — exact module/qweight authority

Reuse/revalidate all 84 modules.

For every layer/role:
- module class/backend;
- qweight shape/dtype/bytes;
- pointer;
- storage offset;
- contiguity;
- exact address span.

All selected policy windows must be the exact qweight tensor interval.

No min/max span over multiple tensors.

---

## Stage 3 — frozen condition matrix

Use exactly:

`CONDITION_MATRIX_PRECONTRACT.json`

Conditions:

Role-only:
- CONTROL_GATE28 / FAIR_GATE28
- CONTROL_UP28 / FAIR_UP28
- CONTROL_DOWN28 / FAIR_DOWN28

Pairwise:
- CONTROL_GU56 / FAIR_GU56
- CONTROL_GD56 / FAIR_GD56
- CONTROL_UD56 / FAIR_UD56

All FFN:
- CONTROL_GUD84 / FAIR_GUD84

No condition may be selected/dropped after seeing timing data.

---

## Stage 4 — fixed-budget policy

For every condition:

requested set-aside:
`33947648 B`

runtime query-back must remain:
`37748736 B`

For K selected modules:

CONTROL:
- exact selected qweight window
- hitRatio=1/K
- NORMAL/NORMAL
- non-persisting

FAIR:
- exact same update point/window
- hitRatio=1/K
- PERSISTING/STREAMING
- persisting

Policy update happens immediately before selected module's natural invocation.

Do not reorder model execution.

No reset between selected-module updates.

Reset only before/after the entire condition.

CUDA hitRatio is a policy hint, not exact protected-line fraction.

---

## Stage 5 — native repetitions

For all 14 conditions:

- 7 fresh processes;
- exact prefix/token identity;
- preserve all 84 FFN projection input/output SHA values;
- CUDA-event timing around all 84 FFN projections, selected and unselected;
- D0-D3 decode-step timing;
- complete ordered policy receipt;
- CPU duration for every policy update.

All 84 FFN events must be present in every condition so timing instrumentation is constant.

No inner-loop synchronize.

---

## Stage 6 — run-aligned accounting

Use same-repetition, same-decode raw rows.

For every condition and stable D1-D3 compute:

- SELECTED_SHARE
- DIRECT_SELECTED_SAVING
- UNSELECTED_FFN_SAVING
- TOTAL_FFN_SAVING
- OBSERVED_DECODE_SAVING
- OUTSIDE_FFN_RESIDUAL
- SELECTED_REALIZATION
- FFN_REALIZATION

Use DESIGN formulas exactly.

Do not use independent median subtraction as formal authority.

Do not clamp realization ratios.

Report gate/up/down contributions separately.

Critical interpretation:

negative OUTSIDE_FFN_RESIDUAL is an accounting residual outside measured FFN timing.
Do not automatically call it cache collateral slowdown.

---

## Stage 7 — local and system materiality

Per selected D3 module:

MATERIAL_LOCAL:
- >=5% timing benefit
- and > combined dispersion.

For whole stable D1-D3:

MATERIAL_SYSTEM:
- >=2% benefit
- and > combined dispersion.

Also report positive-beyond-dispersion sub-2% points.

Apply:

`STAGE_DECISION_PRECONTRACT.json`

exactly.

---

## Stage 8 — host policy overhead

For every CONTROL/FAIR condition report:

- per-update CPU duration;
- total CPU policy duration per run;
- FAIR - CONTROL host overhead delta.

Do not subtract host time from GPU timing.

Preserve it as a diagnostic because policy API calls can affect enqueue cadence.

---

## Stage 9 — representative NCU

Re-query installed NCU metrics/version.

Profile exactly the frozen 12-point matrix:

L0 gate:
- CONTROL_GATE28
- FAIR_GATE28
- CONTROL_GUD84
- FAIR_GUD84

L0 up:
- CONTROL_UP28
- FAIR_UP28
- CONTROL_GUD84
- FAIR_GUD84

L0 down:
- CONTROL_DOWN28
- FAIR_DOWN28
- CONTROL_GUD84
- FAIR_GUD84

D3 only.

Use:
- application replay
- cache-control none
- exact semantic range
- complete natural policy history.

Collect base L1/L2/DRAM metrics and the already qualified critical-path categories when still available.

Non-additive stall/utilization/occupancy metrics remain per-kernel.

---

## Stage 10 — conditional FULLHINT GUD84

Evaluate predeclared trigger only after primary matrix closes:

- GUD84 selected MATERIAL_LOCAL fraction >=0.50
- GUD84 whole-decode benefit <2%

If false:
do not run FULLHINT.

If true run:

- CONTROL_FULL_GUD84
- FULLHINT_GUD84

Both:
- same 84 module update locations
- same fixed requested/actual set-aside
- hitRatio=1.0

CONTROL_FULL:
NORMAL/NORMAL

FULLHINT:
PERSISTING/STREAMING

7 fresh processes each.

If FULLHINT changes whole-decode benefit by >=0.5 percentage points versus FAIR_GUD84, profile L0 gate/up/down D3 CONTROL_FULL vs FULLHINT.

Otherwise no additional FULLHINT NCU.

---

## Stage 11 — answer the scientific questions

Explicitly answer:

1. How much of decode is gate/up/down/all-FFN under matched controls?
2. Which role-only policy gives direct local benefit?
3. Does protecting one role slow/help the other two FFN roles?
4. How large is OUTSIDE_FFN_RESIDUAL for UP28?
5. Does GU/GD/UD reduce or worsen that residual?
6. Under GUD84, how much direct FFN saving is measured?
7. How much of it realizes at whole-decode level?
8. Does GUD84 or any predeclared condition cross 2%?
9. If not, is the limiting factor lack of local FFN benefit or negative residual outside FFN accounting?
10. Does FULLHINT change the conclusion if triggered?
11. Does the evidence now justify bounded trace + first simulator mechanism?

Do not auto-authorize simulator work.

---

## Stage 12 — review pack

Create:

`docs/vm_tlb/review_packs/C16_E1_OPERATOR_FAMILY_EXPANSION_109_V1/`

with all DESIGN-required artifacts and raw evidence.

Update scientific log.

Then:

SHA256SUMS
-> commit
-> push
-> fetch-back/remote verify
-> clean
-> release GPU lock
-> STOP_FOR_CHATGPT_REVIEW

## Boundary

Forbidden:
- Accel-Sim execution
- GPGPU-Sim mutation
- NVBit
- trace capture
- mechanism implementation
- mechanism simulation

Routine CUDA/PyTorch/NCU/parser/Git issues:
solve-and-continue.

Small correctness-preserving repairs:
fix in this Goal.

STOP early only for real model/backend/token/policy identity failure, GPU/runtime corruption, or scientific contract change.
