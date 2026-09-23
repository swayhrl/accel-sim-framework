# CODEX 109 — C16 E1 Targeted L2 Persistence Intervention Full Goal V1

## Mode

GOAL MODE / solve-and-continue

Suggested branch:

`hrl/c16-e1-l2-persistence-intervention-109-v1`

## Read first

Fetch and verify:

`hrl/c16-e1-l2-persistence-intervention-handoff-v1`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_l2_persistence_intervention_v1/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/e1_l2_persistence_intervention_v1/DESIGN.md`
3. this file
4. `docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

Accepted latest consumer:

`hrl/c16-e1-natural-reuse-residency-consumer-174new-v1@4f9242d177220721cb9e669aad5dd9e29f04407d`

## Goal

Execute the complete targeted CUDA persisting-L2 intervention in one Goal.

Do not stop between capability qualification, isolated positive control, natural full-model condition matrix, conditional budget sweep, and mechanism-requirement extraction unless a true scientific contract failure occurs.

No NVBit/full trace/Accel-Sim mechanism implementation.

## Stage 1 — query and freeze CUDA capability

From local CUDA headers/runtime/device query:

- CUDA runtime version
- device name
- L2 bytes
- max persisting-L2 set-aside bytes
- max access-policy-window bytes
- exact supported API for:
  - setting persisting-L2 limit
  - setting stream access-policy window
  - resetting persisting state

Cross-check accepted values:
- L2 67108864 B
- max persisting 46137344 B
- max window 134213632 B

If runtime query differs, preserve both and treat runtime as execution authority; do not silently overwrite accepted history.

## Stage 2 — exact qweight region census

For:
- layer0 up_proj
- layer14 up_proj
- layer0 down_proj

record:
- tensor name
- dtype
- shape
- numel
- element size
- bytes
- data_ptr
- storage offset
- contiguity
- storage span

Require each target qweight to be one exact contiguous region.

Do not use a min/max span across disjoint qweight/qzeros/scales.

If one target qweight is non-contiguous or cannot be represented by one exact access-policy interval, STOP only that target and continue remaining qualified targets if the scientific matrix still remains meaningful.

## Stage 3 — implement policy helper

Implement a minimal audited helper using the locally supported CUDA runtime/driver path.

It must support:

- reset persisting state
- set persisting-L2 budget
- set current/default stream access-policy window
- configure:
  base_ptr
  num_bytes
  hit_ratio
  hit property
  miss property
- query/record requested and accepted settings where possible

No package upgrade or driver change.

Before every fresh condition:
reset previous persisting state.

After every condition:
reset again.

## Stage 4 — isolated policy qualification

Accepted TEXT layer0 up_proj M1 AWQ replay.

Run:

ISO_BASELINE_DENSE
- reset
- no persisting window
- 2 target warmups
- accepted 256MiB dense pressure
- target

ISO_QWEIGHT_PERSIST_DENSE
- reset
- qweight-sized persisting budget
- exact layer0 up qweight window
- hitRatio=1
- 2 target warmups
- dense pressure
- target

Native:
9 reps/condition.

NCU:
application replay
cache-control none
exact target semantic range

metrics:
l1tex__t_bytes.sum
lts__t_bytes.sum
dram__bytes.sum

Preserve raw evidence and policy receipt.

Engineering qualification requires exact identity/policy/selector closure, not a performance win.

## Stage 5 — natural full-model condition matrix

Use the accepted deterministic Qwen2.5-7B AWQ natural decode:
- 2048-token accepted S2_TEXT prefix
- 4 greedy decode steps
- expected tokens [23578,11,323,3950]

Conditions:

BASELINE
SETASIDE_ONLY
PERSIST_L0_UP
PERSIST_L14_UP
PERSIST_L0_DOWN

All persistence conditions use the same qweight-sized persisting budget.

BASELINE:
- reset
- no set-aside/window

SETASIDE_ONLY:
- reserve same persisting budget
- no target address marked persisting

PERSIST_L0_UP:
- reserve same budget
- exact L0 up qweight window

PERSIST_L14_UP:
- reserve same budget
- exact L14 up qweight window

PERSIST_L0_DOWN:
- reserve same budget
- exact L0 down qweight window

For every condition:
- 7 fresh processes
- preserve generated tokens
- preserve all 12 occurrence input/output SHA
- target CUDA-event timing
- decode-step timing
- policy receipt

Any token or occurrence identity change is a scientific STOP for that condition.

## Stage 6 — natural NCU

Primary matrix:

L0 up D1/D3 under:
- BASELINE
- SETASIDE_ONLY
- PERSIST_L0_UP
- PERSIST_L14_UP

L14 up D3 under:
- BASELINE
- SETASIDE_ONLY
- PERSIST_L14_UP
- PERSIST_L0_UP

L0 down D3 under:
- BASELINE
- SETASIDE_ONLY
- PERSIST_L0_DOWN
- PERSIST_L0_UP

Maximum 16 profiles.

Use:
--replay-mode application
--cache-control none

Required metrics:
l1tex__t_bytes.sum
lts__t_bytes.sum
dram__bytes.sum

Optional additional L2 hit-rate/counter metric only if exact installed metric name/unit is queried and adding it does not materially expand replay complexity.

Preserve:
BASE
SESSION
PROFILE
policy receipt
kernel inventory
replay passes
target identity.

## Stage 7 — independent producer-side analysis

For each target compare:

target persistence:
PERSIST_TARGET / SETASIDE_ONLY

matched unrelated:
PERSIST_OTHER / SETASIDE_ONLY

reservation effect:
SETASIDE_ONLY / BASELINE

Native target timing material benefit:
>=5% lower than SETASIDE_ONLY
and greater than combined dispersion.

Target DRAM material benefit:
>=20% lower than SETASIDE_ONLY
and >=4MiB absolute reduction.

TARGET_SPECIFIC:
target-persist benefit materially exceeds matched unrelated-persist effect.

Do not collapse controls.

## Stage 8 — conditional budget sensitivity

Only if L0 up natural D3 shows material target DRAM or timing benefit under PERSIST_L0_UP.

Budgets:
8,16,24,32 MiB, full-qweight budget.

For each budget:
- persisting limit = tested budget
- access-policy window remains exact full qweight tensor
- hitRatio = min(1,budget/qweight_bytes)
- 7 fresh-process natural runs
- L0 up D3 primary timing

NCU:
D3 one profile per budget
same three byte metrics.

Report first TESTED budget with material benefit.
Do not claim exact threshold.

If full-qweight condition is non-material:
do not run this sweep.

## Stage 9 — mechanism requirements

If natural target persistence shows material and target-specific benefit, produce an abstract requirement document only.

Cover:
- protected object class
- line/address granularity
- inter-token lifetime
- measured budget sensitivity
- selectivity need
- interference resistance
- fallback normal policy
- candidate identity sources

Do not choose/implement a final classifier or replacement algorithm.

Allowed final state:
MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW

If only DRAM changes materially without timing:
TARGETED_PERSISTENCE_TRAFFIC_ONLY

If no material natural benefit:
TARGETED_PERSISTENCE_MECHANISM_PRECONDITION_NOT_SUPPORTED

If CUDA policy itself cannot be qualified:
CUDA_PERSISTENCE_POLICY_UNQUALIFIED

## Stage 10 — review pack closure

Create:

`docs/vm_tlb/review_packs/C16_E1_L2_PERSISTENCE_INTERVENTION_109_V1/`

with all DESIGN-required deliverables and raw evidence.

Update scientific log.

Then:
SHA256SUMS
-> commit
-> push
-> fetch-back/remote verify
-> clean
-> release GPU lock
-> STOP

## Boundaries

Do not start:
- NVBit
- full address trace
- Accel-Sim mechanism implementation
- cache/TLB mechanism simulation

Routine CUDA helper/PyTorch/NCU/parser/Git issues:
solve and continue.

STOP early only for:
- unsupported CUDA persistence capability that invalidates the intervention
- target qweight interval cannot be represented safely
- target/backend/token/SHA identity drift
- application replay cannot preserve policy/semantic identity
- GPU/runtime corruption
- scientific contract change outside DESIGN.
