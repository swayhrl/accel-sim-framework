# CODEX 109 — C16 E1 Fixed-Budget Protected-Coverage Scaling Full Goal V1

## Mode

GOAL MODE / solve-and-continue

Suggested branch:

`hrl/c16-e1-coverage-scaling-109-v1`

## Read first

Fetch and verify:

`hrl/c16-e1-coverage-scaling-handoff-v1`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_coverage_scaling_v1/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/e1_coverage_scaling_v1/DESIGN.md`
3. `docs/vm_tlb/chatgpt_handoff/c16/e1_coverage_scaling_v1/LAYER_SELECTION_PRECONTRACT.json`
4. `docs/vm_tlb/chatgpt_handoff/c16/e1_coverage_scaling_v1/STAGE_DECISION_PRECONTRACT.json`
5. this file
6. `docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

Accepted upstream shared-hardware producer:

`hrl/c16-e1-shared-residency-feasibility-109-v1@1e701f013fc174b5b4df9febb5c33500f9ea586e`

Accepted shared design/consumer prep:

`hrl/c16-e1-shared-residency-design-review-174new-v1@547e9263a8d0c12bb34d96e27134a120b83fb6d0`

## Goal

Execute the complete fixed-budget protected-coverage scaling stage in one Goal.

This stage is real-hardware RTX4080 only.

Do not run Accel-Sim.
Do not capture NVBit/full traces.
Do not implement a simulator mechanism.

The Goal must complete:

1. full FFN opportunity census;
2. frozen up_proj layer-set coverage scaling;
3. Amdahl/realization accounting;
4. N14 composition holdout;
5. bounded NCU scaling profiles;
6. conditional FULLHINT controls if predeclared trigger fires;
7. final stage closure.

Do not STOP between ordinary stages.

---

## Stage 1 — recover/freeze accepted full-model authority

Reuse accepted:

- Qwen2.5-7B AWQ deployment;
- S2_TEXT 2048-token prefix;
- four greedy decode steps;
- expected tokens `[23578,11,323,3950]`;
- accepted target backend/kernel family.

Fresh-process replay must preserve token and occurrence identity.

No package/backend/dtype/model revision change.

---

## Stage 2 — full FFN opportunity census

Runtime-inspect all 28 layers.

For every layer 0..27 census:

- mlp.gate_proj
- mlp.up_proj
- mlp.down_proj

Record:

- module class
- qweight dtype
- qweight shape
- bytes
- data_ptr
- storage offset
- contiguity.

If one requested role is not a valid accepted AWQ qweight-backed family, mark that role unsupported and continue supported roles; do not substitute another operator.

Run condition:

`CENSUS_FFN_NO_PERSIST`

- no persisting set-aside;
- no access-policy window;
- 7 fresh processes;
- exact accepted tokens;
- CUDA events around every supported FFN projection occurrence;
- no inner-loop synchronize;
- D0-D3 decode-step timing.

From raw run-aligned rows compute for stable D1-D3:

- 28-up_proj share
- 28-gate_proj share
- 28-down_proj share
- all supported FFN-projection share

as:
sum module event time / same-run decode-step time.

Report per-role:
- min/median/max layer timing
- P25/P75
- top-1 share
- top-4 share

No speedup extrapolation from these shares.

---

## Stage 3 — frozen layer manifest

Use exactly:

`LAYER_SELECTION_PRECONTRACT.json`

Do not change layer sets after timing is observed.

Primary:

N1
N2
N4
N8
N14A
N28

Composition holdout:

N14B

Primary operator family:
`up_proj` only.

---

## Stage 4 — FAIR fixed-budget coverage scaling

For every set S of N selected layers, run two conditions.

### CONTROL_S

Fixed requested set-aside:

`33947648 B`

Runtime actual query-back must remain:

`37748736 B`

Before each selected up_proj occurrence in:

- PREFILL
- D0
- D1
- D2
- D3

perform one full exact qweight-window update:

- hitRatio = 1/N
- hitProp = NORMAL
- missProp = NORMAL
- persisting = false

### FAIR_S

Exactly the same update points/order/window sizes, except:

- hitRatio = 1/N
- hitProp = PERSISTING
- missProp = STREAMING
- persisting = true

No reset is allowed between selected-module updates.

Reset only before and after the whole condition.

Important:
CUDA hitRatio is a policy hint.
Do not describe 1/N as an exact protected-line fraction.

---

## Stage 5 — native evidence for every CONTROL/FAIR point

For every CONTROL_S and FAIR_S:

- 7 fresh processes;
- exact prefix;
- exact tokens;
- all 28 up_proj input/output SHA identities;
- time all 28 up_proj calls, selected and non-selected;
- time D0-D3 decode steps;
- preserve policy update receipts;
- preserve CPU policy update duration.

All 28 up_proj events are recorded in every condition so event instrumentation remains constant across coverage points.

Policy calls must occur before target-event timing starts.

No inner-loop synchronize.

---

## Stage 6 — coverage/Amdahl analysis

Compute everything from raw run-aligned samples, not from ratio-of-independent-medians alone.

For every S and D1-D3:

### selected target share

sum selected CONTROL_S up_proj time / same-run CONTROL_S decode-step time.

### summed local saving

sum(CONTROL_S selected up_proj time - FAIR_S selected up_proj time).

### observed decode saving

CONTROL_S decode-step time - FAIR_S decode-step time.

### realization ratio

observed decode saving / summed local saving

when denominator > 0.

Do not clamp.

Also compute:

- selected material-layer count/fraction
- selected layer benefit distribution
- non-selected aggregate up_proj effect
- CPU API overhead
- stable D1-D3 mean effect.

Material local:
>=5% timing benefit
AND
benefit > hypot(CV_control,CV_fair).

Use STAGE_DECISION_PRECONTRACT exactly for N28 final classification.

---

## Stage 7 — N14 composition holdout

Independently compare:

N14A
N14B

Each has its own matched CONTROL and FAIR pair.

Report:

- target share
- material-layer fraction
- median selected-layer benefit
- whole-decode benefit
- realization ratio.

Do not select a preferred half for later claims.

This is a layer-composition robustness check only.

---

## Stage 8 — bounded critical-path NCU scaling profiles

Re-query installed NCU metric availability/version first.

Use the same category/aggregation rules accepted in the shared-residency stage.

Required base metrics:

l1tex__t_bytes.sum
lts__t_bytes.sum
dram__bytes.sum

Also collect the already qualified critical-path categories when still available:

- gpu duration
- L2 read hit sectors
- L2 read miss sectors
- DRAM read bytes
- long scoreboard stall
- LSU utilization
- active warps

Profile D3 only:

L0 up:
CONTROL_N1 / FAIR_N1
CONTROL_N8 / FAIR_N8
CONTROL_N28 / FAIR_N28

L14 up:
CONTROL_N2 / FAIR_N2
CONTROL_N8 / FAIR_N8
CONTROL_N28 / FAIR_N28

L27 up:
CONTROL_N4 / FAIR_N4
CONTROL_N28 / FAIR_N28

Maximum 16 primary profiles.

Use:
- application replay
- cache-control none
- exact selected semantic range
- complete policy update history before selected occurrence.

Percent/stall/utilization metrics remain per-kernel.
Do not sum them.

Question:
does the quantized-GEMM critical-path benefit dilute as N grows?

---

## Stage 9 — conditional FULLHINT control

Evaluate the exact predeclared trigger after primary FAIR closure:

- N28 selected MATERIAL_LOCAL fraction >= 0.50
- N28 whole-decode benefit < 2%

If false:
do not run FULLHINT.
Record why.

If true, run:

CONTROL_FULL_N8
FULLHINT_N8
CONTROL_FULL_N28
FULLHINT_N28

All retain the same fixed requested/actual set-aside.

CONTROL_FULL:
- same selected-layer update schedule
- hitRatio=1.0
- NORMAL/NORMAL

FULLHINT:
- same selected-layer update schedule
- hitRatio=1.0
- PERSISTING/STREAMING

Interpretation:
this intentionally oversubscribes persisting intent under one fixed set-aside.
It does not imply all selected qweights fit.

Native:
7 fresh processes/condition.

If FULLHINT_N28 whole-decode benefit differs from FAIR_N28 by >=0.5 percentage points, additionally NCU-profile:

L0 D3 CONTROL_FULL_N28 / FULLHINT_N28
L14 D3 CONTROL_FULL_N28 / FULLHINT_N28

using the same critical-path metric contract.

---

## Stage 10 — final scientific interpretation

Answer directly:

1. What fraction of stable decode is spent in all 28 up_proj?
2. What fraction is gate/down/all-FFN projection time?
3. At N=1/2/4/8/14/28, how much decode time is actually covered?
4. Does per-layer local benefit dilute as N increases?
5. Does whole-decode benefit track summed local savings?
6. What is the realization ratio across N?
7. Does N14A vs N14B materially change the conclusion?
8. Does FULLHINT alter the FAIR coverage curve if triggered?
9. Does N28 cross the 2% system-relevance gate?
10. Is the next step simulator implementation, broader operator-family coverage, or stopping the residency mechanism case?

Do not auto-authorize the next step.

---

## Stage 11 — review pack

Create:

`docs/vm_tlb/review_packs/C16_E1_COVERAGE_SCALING_109_V1/`

with all DESIGN-required files and raw evidence.

Update:
`docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

Then:

SHA256SUMS
-> commit
-> push
-> fetch-back/remote verify
-> clean worktree
-> release GPU lock
-> STOP_FOR_CHATGPT_REVIEW

---

## Boundaries

Forbidden:

- Accel-Sim execution
- GPGPU-Sim source mutation
- NVBit capture
- full address trace
- mechanism implementation
- mechanism simulation

Routine PyTorch/CUDA/NCU/parser/Git issues:
solve-and-continue.

Small correctness-preserving fixes:
repair inside the Goal; do not create a separate repair round.

STOP early only if:
- accepted model/backend identity cannot be preserved;
- token/SHA determinism fails and cannot be repaired without changing contract;
- fixed requested/actual persistence budget cannot be preserved;
- policy history becomes ambiguous;
- GPU/runtime corruption;
- a scientific contract change outside DESIGN is required.
