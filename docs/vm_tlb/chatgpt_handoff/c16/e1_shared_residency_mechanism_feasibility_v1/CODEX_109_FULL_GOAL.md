# CODEX 109 — C16 E1 Shared-Residency Mechanism Feasibility Full Goal V1

## Mode

GOAL MODE / solve-and-continue

Suggested branch:

`hrl/c16-e1-shared-residency-feasibility-109-v1`

## Read first

Fetch and verify:

`hrl/c16-e1-shared-residency-mechanism-feasibility-handoff-v1`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_shared_residency_mechanism_feasibility_v1/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/e1_shared_residency_mechanism_feasibility_v1/DESIGN.md`
3. this file
4. `docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

Accepted upstream producer:
`4c0e6b998528e425578cacf5912bbcc4ff3bfaf6`

Accepted independent consumer:
`1dcab9c8d932973399c5811dc817802bfb3b9dfe`

## Goal

Execute the complete shared-residency mechanism-feasibility hardware stage in one Goal:

1. critical-path NCU diagnosis;
2. rotating-window qualification;
3. fixed-total-budget multi-target natural experiment;
4. shared-policy NCU;
5. whole-decode and local-target analysis;
6. closure.

Do not start NVBit/full trace/simulator implementation.

## Stage 1 — critical-path metric discovery

Use installed NCU only.

Query exact available metrics and units for:
- kernel duration / elapsed cycles;
- L2 read lookup hit sectors or hit rate;
- L2 read misses;
- DRAM read sectors/bytes;
- memory-dependency / long-scoreboard stalls;
- LSU or memory-pipe utilization;
- active warps / occupancy.

Do not hard-code names from another NCU version.

Persist:
- query command;
- exact metric name;
- exact unit;
- category;
- availability.

Unavailable category = explicit unavailable, not invented.

## Stage 2 — critical-path profile matrix

Profile:

L0 up D3:
- BASELINE
- SETASIDE_ONLY
- PERSIST_L0_UP
- PERSIST_L14_UP

L14 up D3:
- SETASIDE_ONLY
- PERSIST_L14_UP
- PERSIST_L0_UP

L0 down D3:
- SETASIDE_ONLY
- PERSIST_L0_DOWN
- PERSIST_L0_UP

Maximum 10 profiles.

Use:
--replay-mode application
--cache-control none

Preserve exact semantic/policy identity.

For AWQ GEMM+reduction:
- keep per-kernel results;
- sum only additive metrics;
- never sum percentage/stall-rate metrics without valid documented aggregation.

Answer:
- which kernel carries the timing change?
- does target persistence change L2 hit/miss behavior?
- does long-scoreboard/memory-stall behavior move with timing?
- is aggregate DRAM byte change a poor proxy for the critical-path effect?

No stronger causal claim than the controlled policy intervention.

## Stage 3 — rotating-window isolated qualification

Use:
A = L0 up
B = L14 up

One fixed full-qweight persisting-L2 set-aside.

Qualification sequence:

1. reset
2. set A exact qweight window, hitRatio=0.5
3. execute A twice
4. switch to B exact qweight window, hitRatio=0.5, NO reset
5. execute B twice
6. switch back to A, hitRatio=0.5, NO reset
7. measure/profile A

Matched API-switch control:

- same number/order of stream policy updates
- same set-aside
- but no qweight is marked persisting.

First inspect local CUDA runtime/header semantics.

If hitRatio=0 persisting control is not a clean no-persist control, extend the helper to use a normal/non-persisting access property.

Do not fake a control.

Record:
- every window transition
- CPU host duration of policy update
- requested/actual set-aside
- no reset between A/B/A
- exact qweight pointer/bytes
- target timing
- target traffic

NCU:
base L1/L2/DRAM metrics plus bounded qualified critical-path metrics.

If rotating-window semantics cannot be qualified:
STOP stage result as ROTATING_WINDOW_POLICY_UNQUALIFIED.
Do not proceed to natural SHARE conditions.

## Stage 4 — natural shared-budget conditions

Fixed requested set-aside:
33947648 B

Preserve runtime actual query-back.

Run:

SETASIDE_ONLY

ROTATE_CONTROL_3
- same update points/order as SHARE3
- no selected qweight marked persisting

SINGLE_L0_UP
- L0 up hitRatio=1.0
- use rotating harness so API structure is comparable

SHARE2_UP
- L0 up hitRatio=0.5
- L14 up hitRatio=0.5

SHARE2_L0
- L0 up hitRatio=0.5
- L0 down hitRatio=0.5

SHARE3
- L0 up hitRatio=1/3
- L14 up hitRatio=1/3
- L0 down hitRatio=1/3

Important:

- one total set-aside only;
- no reset between selected target switches in one model execution;
- exact full qweight window each time;
- reset before and after each fresh-process condition;
- policy calls happen before target event timing starts;
- preserve host update overhead separately.

For every condition:
- 7 fresh processes
- accepted S2_TEXT prefix
- 4 greedy decode tokens exactly unchanged
- all 12 occurrence input/output SHA unchanged
- target timing
- D0-D3 decode-step timing
- policy transition receipts
- API update overhead.

## Stage 5 — shared-policy semantic NCU

D3 targets only.

L0 up:
- SETASIDE_ONLY
- ROTATE_CONTROL_3
- SINGLE_L0_UP
- SHARE2_UP
- SHARE2_L0
- SHARE3

L14 up:
- SETASIDE_ONLY
- ROTATE_CONTROL_3
- SHARE2_UP
- SHARE3

L0 down:
- SETASIDE_ONLY
- ROTATE_CONTROL_3
- SHARE2_L0
- SHARE3

Max 14 profiles.

Use:
application replay
cache-control none
exact target range.

Collect:
base L1/L2/DRAM byte metrics
plus critical-path metrics qualified in Stage 1 if bounded.

Profile replay must establish the complete natural policy-switch history before selected D3.

## Stage 6 — independent producer-side analysis

For each target/shared condition:

local timing benefit vs ROTATE_CONTROL_3.

Material local:
>=5% lower
and > combined dispersion.

Whole stable decode D1-D3:
compare shared condition vs:
- ROTATE_CONTROL_3
- SETASIDE_ONLY

MATERIAL_DECODE_BENEFIT:
>=2% lower than ROTATE_CONTROL_3
and > combined dispersion.

MULTI_TARGET_RETAINED:
>=2 selected targets retain material local timing benefit in the same shared condition.

Also record:
- absolute decode-step ms change;
- policy update CPU overhead;
- whether ROTATE_CONTROL_3 itself perturbs decode.

Do not hide overhead.

## Stage 7 — stage decision

Only:

SHARED_RESIDENCY_END_TO_END_SUPPORTED

SHARED_RESIDENCY_LOCAL_ONLY

SHARED_RESIDENCY_SINGLE_TARGET_ONLY

ROTATING_WINDOW_POLICY_UNQUALIFIED

SHARED_RESIDENCY_NOT_SUPPORTED

Use DESIGN definitions exactly.

Do not overwrite:
producer_scoped_state
strict_consumer_state
decision_rule_divergence
from the previous stage.

## Stage 8 — review pack

Create:

docs/vm_tlb/review_packs/
C16_E1_SHARED_RESIDENCY_FEASIBILITY_109_V1/

with all DESIGN-required files and raw evidence.

Update scientific log.

Then:
SHA256SUMS
-> commit
-> push
-> fetch-back/remote verify
-> clean
-> release GPU lock
-> STOP

## Boundary

Forbidden:
- NVBit
- full address trace
- Accel-Sim mechanism implementation
- mechanism simulation

Routine CUDA-helper/NCU/PyTorch/parser/Git issues:
solve-and-continue.

Small correctness-preserving repairs:
fix inside this Goal; do not STOP just for review.

STOP early only for:
- rotating-window policy semantics cannot be qualified
- semantic/token identity changes
- policy state cannot be attributed unambiguously
- GPU/runtime corruption
- scientific contract change outside DESIGN.
