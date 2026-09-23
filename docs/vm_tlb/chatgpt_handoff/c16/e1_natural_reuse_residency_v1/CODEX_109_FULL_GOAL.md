# CODEX 109 — C16 E1 Natural-Reuse / Residency Causal Closure Full Goal V1

## Mode

GOAL MODE / solve-and-continue

Suggested branch:

`hrl/c16-e1-natural-reuse-residency-109-v1`

## Read first

Fetch and verify:

`hrl/c16-e1-natural-reuse-residency-handoff-v1`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_natural_reuse_residency_v1/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/e1_natural_reuse_residency_v1/DESIGN.md`
3. this file
4. `docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

Accepted upstream:
- clean E1 producer: `8988d6108ff8bdca180a14cec2fe769df45b09f1`
- clean E1 consumer: `59ddb8ba2a33ef12b73bfc859f3a994e0b4ef4ca`
- semantic NCU V2 producer: `8d1f62229cae15199793ba5569327cf1e83596f3`
- semantic NCU V2 consumer: `cdd3ec7afbb1611cc52a4b74d32b38a3edabd131`
- residency intervention producer: `22d1b98d7f0c213950654fc754be4e7388836de3`
- residency intervention consumer: `5b11dd41e98044fcad76da4a906c7ba8609eb828`

## Goal

Execute the complete natural-reuse/residency causal-closure package in one Goal.

Do not stop between refill dynamics, capacity-knee refinement, natural full-model decode profiling, held-out layer validation, and final closure unless a true scientific contract failure occurs.

Do not start NVBit/full trace/mechanism work.

## Part A — refill dynamics

For TEXT M1:
- q_proj RAW/AWQ
- down_proj RAW/AWQ
- up_proj RAW/AWQ

Per point:
1. 2 exact target warmups
2. accepted 256 MiB DENSE_MEMORY_PRESSURE
3. synchronize
4. execute K1..K6 immediate target calls with identical input bytes

Native:
- 9 independent sequence repetitions
- CUDA event timing per Ki
- preserve all samples
- no pressure in target timing
- verify input/output SHA

NCU:
- K1/K2/K4 for every point
- application replay
- cache-control none
- metrics:
  l1tex__t_bytes.sum
  lts__t_bytes.sum
  dram__bytes.sum

The selected Ki semantic range must include only that call.
All preceding calls required to establish Ki state execute outside the selected range.

## Part B — capacity-knee refinement

AWQ M1 only.

q_proj doses MiB:
0,32,48,56,60,64,72,96

down_proj doses:
0,16,24,28,32,36,48,64

up_proj doses:
0,16,24,28,30,32,36,40,48,64

For each dose:
- 2 target warmups
- dense-read exact prefix of accepted 256 MiB buffer
- target
- 7 native timing repetitions

NCU:
- profile every dose
- collect only dram__bytes.sum
- application replay/cache-control none
- exact semantic selector

Record:
- nominal residual L2 budget
- first dose with target DRAM >1 MiB and >10% target packed bytes
- first material timing dose
- observed DRAM-knee minus nominal residual-L2 MiB

No hard theorem or pass/fail around exact equality.

## Part C — natural full-model AWQ decode

Use accepted Qwen2.5-7B AWQ.

Input:
accepted S2_TEXT 2048-token prefix.

Execute exactly 4 deterministic greedy decode steps.

Instrument:
- layer0 mlp.up_proj
- layer14 mlp.up_proj
- layer0 mlp.down_proj

Freeze:
- generated token IDs
- per-occurrence input SHA
- per-occurrence output SHA
- unique NVTX range

Fresh-process replay must reproduce token IDs and occurrence SHA sequence before profiling.

Native:
- 7 complete full-model runs
- CUDA events around target calls without inner-loop synchronize
- resolve after full run
- record full decode step duration

NCU profiles:
- layer0 up_proj D0,D1,D3
- layer14 up_proj D0,D3
- layer0 down_proj D0,D3

Total 7 natural profiles.

Metrics:
- l1tex__t_bytes.sum
- lts__t_bytes.sum
- dram__bytes.sum

Use application replay/cache-control none.

All non-target full-model work must execute naturally outside the selected semantic range.

## Part D — isolated-vs-natural comparison

For each natural profile compare against accepted isolated:
- WARM
- DENSE_MEMORY_PRESSURE

Compute descriptive:
warm_fraction = abs(natural-warm)/abs(dense-warm)

for DRAM and timing where denominator nonzero.

Do not clamp outside [0,1].

Interpret:
- near 0 warm-like
- near 1 dense-like
- outside bracket explicitly reported

No categorical threshold is required.

## Optional RAW natural full-model control

Attempt only if the accepted RAW Qwen2.5-7B model runs naturally on RTX4080 without:
- package changes
- offload
- backend/dtype change
- OOM workarounds that change execution

If cleanly runnable:
- layer0 up_proj D0/D3 native timing
- optional D0 NCU

Otherwise:
RAW_FULL_MODEL_NATURAL_CONTROL_NOT_RUN_RESOURCE_BOUND

Do not spend significant engineering time on this optional control.

## Identity and raw evidence

Preserve for every profile:
- raw BASE.csv
- SESSION.csv
- PROFILE.log
- exact profiler command
- input/output SHA
- kernel inventory
- replay pass count
- exact metric unit

Natural decode token sequence and occurrence bindings are first-class authority.

## Analysis

Answer independently:

1. Do AWQ q/down/up K1→K6 timing and DRAM show refill?
2. Do RAW down/up remain comparatively flat/high-DRAM?
3. Do observed DRAM knees align descriptively with nominal residual L2 budgets?
4. Does natural full-model decode look warm-like or dense-like?
5. Does layer14 reproduce layer0 up_proj behavior?
6. Does down_proj support the same natural reuse conclusion?
7. Are capacity and role both needed to explain behavior?

Use DESIGN Case A/B/C/D framing.

## Output

Create:

`docs/vm_tlb/review_packs/C16_E1_NATURAL_REUSE_RESIDENCY_109_V1/`

with all DESIGN-required artifacts.

Update:
`docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

NEXT_STEP_DECISION must not automatically authorize:
- NVBit
- full address trace
- cache/TLB mechanism
- mechanism simulation

Then:
SHA256SUMS
-> commit
-> push
-> fetch-back/remote verify
-> clean
-> release GPU lock
-> STOP

## Solve-and-continue

Ordinary PyTorch/CUDA/NCU/NVTX/parser/Git issues:
solve and continue.

STOP early only if:
- accepted target/backend identity cannot be preserved
- natural decode token/occurrence sequence is nondeterministic and cannot be repaired without changing contract
- NCU application replay cannot preserve selected occurrence state
- GPU/runtime corruption
- scientific contract change outside DESIGN is required.
