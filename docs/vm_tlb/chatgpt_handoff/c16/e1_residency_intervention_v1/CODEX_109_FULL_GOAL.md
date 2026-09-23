# CODEX 109 — C16 E1 Residency Intervention Full Goal V1

## Mode

GOAL MODE / solve-and-continue

Suggested branch:

`hrl/c16-e1-residency-intervention-109-v1`

## Read first

Fetch and verify:

`hrl/c16-e1-residency-intervention-handoff-v1`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_residency_intervention_v1/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/e1_residency_intervention_v1/DESIGN.md`
3. this file
4. `docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

Accepted authorities:

- clean E1 producer:
  `8988d6108ff8bdca180a14cec2fe769df45b09f1`
- clean E1 independent consumer:
  `59ddb8ba2a33ef12b73bfc859f3a994e0b4ef4ca`
- semantic NCU V2 producer:
  `8d1f62229cae15199793ba5569327cf1e83596f3`
- semantic NCU V2 independent consumer:
  `cdd3ec7afbb1611cc52a4b74d32b38a3edabd131`

## Goal

Execute the complete bounded residency-intervention package in one Goal.

Do not stop between capacity census, harness qualification, native timing, NCU, dose sweep, CODE holdout, and closure unless a real scientific contract failure occurs.

No NVBit/full trace/cache-TLB mechanism.

## Stage 1 — capacity census

Using exact accepted modules, compute actual state bytes for:

- q_proj RAW_FP16
- q_proj AWQ
- down_proj RAW_FP16
- down_proj AWQ
- up_proj RAW_FP16
- up_proj AWQ

AWQ total must be derived from exact state_dict tensors actually used by the frozen module.

Record device L2 = accepted raw NCU device attribute.

Do not infer sizes only from nominal dimensions.

## Stage 2 — implement and qualify pressure harness

Allocate one 256 MiB FP32 CUDA buffer before target-state preparation.

Initialize once.

Implement:

WARM:
- 2 target warmups
- sync
- target

SPARSE_PAGE_PRESSURE:
- 2 target warmups
- sync
- execute buffer[::1024].sum() over same 256 MiB buffer
- sync
- target

DENSE_MEMORY_PRESSURE:
- 2 target warmups
- sync
- execute buffer.sum()
- sync
- target

WARM_RECOVERY:
- after dense test, 2 target warmups
- sync
- target

Pressure execution is outside target CUDA-event interval and outside target semantic NVTX range.

Do not call DENSE a guaranteed cache flush.

Qualify pressure operations once:
- exact buffer bytes
- dtype
- sparse byte stride = 4096
- sparse/dense selected element counts
- kernel inventory
- pressure duration
- lightweight traffic evidence proving DENSE has materially larger memory/cache-line traffic than SPARSE

Both use the same allocated buffer/range.

Do not claim identical TLB behavior.

## Stage 3 — native TEXT timing

Run:

M1:
- q_proj RAW/AWQ
- down_proj RAW/AWQ
- up_proj RAW/AWQ

Shape control:
- up_proj M256 RAW/AWQ

For every point:
- WARM_A
- SPARSE_PAGE_PRESSURE
- DENSE_MEMORY_PRESSURE
- WARM_B

Protocol:
- 7 measured repetitions/state
- 2 target warmups before each state construction as defined
- CUDA event timing around target only
- pressure excluded from target timing
- rotate target-point order across repetitions
- preserve all samples
- record pressure duration separately
- verify exact input/output SHA each state

Compute:
- SPARSE/WARM_A
- DENSE/WARM_A
- WARM_B/WARM_A
- CV/dispersion
- materiality gates from DESIGN

## Stage 4 — primary semantic NCU intervention

Use installed NCU and the accepted application-replay/cache-control-none contract.

Collect exactly:
- l1tex__t_bytes.sum
- lts__t_bytes.sum
- dram__bytes.sum

Exact runtime metric names/units only.

Required profiles:

For q/down/up M1 × RAW/AWQ:
- WARM
- SPARSE_PAGE_PRESSURE
- DENSE_MEMORY_PRESSURE

18 profiles.

For up_proj M256 × RAW/AWQ:
- WARM
- DENSE_MEMORY_PRESSURE

4 profiles.

Total primary maximum = 22.

Every profile must prove:
- accepted input/output SHA
- correct semantic range
- pressure outside target range
- correct kernel inventory
- application replay
- cache-control none
- replay pass count
- byte units

Preserve raw BASE/SESSION/report evidence.

Do not aggregate from a producer-authored summary without raw receipts.

## Stage 5 — pressure-dose timing

Only up_proj M1 RAW_FP16 and AWQ.

Reuse the same 256 MiB buffer.

Dense-touch prefix sizes:

0, 16, 32, 64, 128, 256 MiB.

For each:
- 2 target warmups
- dense-read prefix
- sync
- target
- 7 timing repetitions

Keep raw samples.

If timing dose response is material, NCU for 64 MiB is already authorized:

- up_proj M1 RAW 64MiB
- up_proj M1 AWQ 64MiB

0 and 256 endpoints are already profiled.

Do not add more dose NCU points.

## Stage 6 — CODE down_proj holdout

Use the already accepted common CODE down_proj M1 authority only if directly reusable.

Run:
- RAW WARM / DENSE / WARM_RECOVERY
- AWQ WARM / DENSE / WARM_RECOVERY

7 native timing repetitions.

If TEXT down_proj M1 has a material dense-pressure intervention:
profile CODE with NCU for:
- RAW WARM
- RAW DENSE
- AWQ WARM
- AWQ DENSE

If direct authority reuse fails:
record
`CODE_INTERVENTION_NOT_RUN_AUTHORITY_NOT_DIRECTLY_REUSABLE`
and continue.

No new input capture campaign.

## Stage 7 — evaluate pre-registered predictions

Use DESIGN P1–P4 exactly.

Primary up_proj M1 classifications:

- MATERIAL_TIMING_PERTURBATION
- MATERIAL_DRAM_PERTURBATION
- REVERSIBLE
- DENSE_SPECIFIC

Then assign only one scoped stage-level label:

- RESIDENCY_INTERVENTION_STRONGLY_SUPPORTED
- RESIDENCY_INTERVENTION_PARTIALLY_SUPPORTED
- RESIDENCY_INTERVENTION_NOT_SUPPORTED

Do not claim universal cache causality.

Important:
SPARSE is only a page-footprint-oriented control.
It does not fully exclude TLB effects.

## Stage 8 — close all evidence

Create:

`docs/vm_tlb/review_packs/C16_E1_RESIDENCY_INTERVENTION_109_V1/`

with all DESIGN-required artifacts.

Update:

`docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

NEXT_STEP_DECISION must not auto-authorize:
- NVBit
- full address trace
- cache/TLB mechanism

Then:

SHA256SUMS
-> commit
-> push
-> fetch-back/remote verify
-> clean worktree
-> release GPU lock
-> STOP.

## Solve-and-continue

Ordinary CUDA/PyTorch/NCU/parser/timing/Git issues:
solve and continue.

STOP early only if:
- accepted target input/output identity cannot be preserved;
- pressure operation contaminates target NVTX/timing boundary and cannot be repaired;
- accepted backend/runtime identity changes;
- NCU application replay cannot preserve semantic selection;
- GPU/runtime corruption;
- a scientific contract change outside DESIGN is required.
