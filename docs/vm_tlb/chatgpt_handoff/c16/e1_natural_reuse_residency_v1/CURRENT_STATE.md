# C16 E1 Natural-Reuse / Residency Causal Closure — Current State V1

## Accepted upstream

Clean E1 producer:
`hrl/c16-e1-clean-baseline-109-v1@8988d6108ff8bdca180a14cec2fe769df45b09f1`

Independent clean consumer:
`hrl/c16-e1-clean-baseline-consumer-prep-174new-v1@59ddb8ba2a33ef12b73bfc859f3a994e0b4ef4ca`

Semantic NCU V2 producer:
`hrl/c16-e1-semantic-ncu-cache-state-repair-109-v1@8d1f62229cae15199793ba5569327cf1e83596f3`

Independent semantic NCU V2 consumer:
`hrl/c16-e1-semantic-ncu-v2-consumer-174new-v1@cdd3ec7afbb1611cc52a4b74d32b38a3edabd131`

Residency intervention producer:
`hrl/c16-e1-residency-intervention-109-v1@22d1b98d7f0c213950654fc754be4e7388836de3`

Independent residency consumer:
`hrl/c16-e1-residency-intervention-consumer-174new-v1@5b11dd41e98044fcad76da4a906c7ba8609eb828`

## Closed evidence

The tested memory-state intervention is independently classified:

`RESIDENCY_INTERVENTION_PARTIALLY_SUPPORTED`

Primary TEXT up_proj M1 AWQ:

- DENSE/WARM timing = 1.5364583
- SPARSE/WARM timing = 0.9765625
- WARM_B/WARM_A = 0.9375000
- DRAM WARM = 80,000 B
- DRAM SPARSE = 2,365,312 B
- DRAM DENSE = 35,368,192 B

Primary gates:
- MATERIAL_TIMING_PERTURBATION = true
- MATERIAL_DRAM_PERTURBATION = true
- DENSE_SPECIFIC = true
- REVERSIBLE = false

Important nuance:
- REVERSIBLE=false is caused by over-recovery/baseline drift: WARM_B is ~6.25% faster than WARM_A.
- It is not persistent DENSE slowdown.

Controls:
- TEXT down_proj recovery passes.
- CODE down_proj recovery passes and reproduces dense AWQ timing/DRAM perturbation.
- q_proj RAW/AWQ states both fit below L2 and show much smaller timing perturbation.
- up_proj M256 shows little timing sensitivity to dense pre-pressure.

Capacity census:
- q_proj RAW_FP16 = 25,697,280 B < L2
- q_proj AWQ = 6,680,576 B < L2
- down_proj RAW_FP16 = 135,790,592 B > L2
- down_proj AWQ = 35,273,728 B < L2
- up_proj RAW_FP16 = 135,790,592 B > L2
- up_proj AWQ = 35,273,728 B < L2
- device L2 = 67,108,864 B

Pressure-dose:
- up_proj M1 AWQ rises materially by 32 MiB and reaches ~1.64x by 64 MiB, then approximately plateaus.
- RAW response remains <0.8%.

## Why another stage is needed

The current intervention is still an isolated-module experiment.

For architecture relevance we now need to answer:

1. After eviction/pressure, how many target invocations are required to repopulate the compressed working set?
2. Does the apparent capacity knee align across q/down/up with nominal residual L2 capacity?
3. Most importantly: does the warm-residency state survive a **natural full-model decode reuse interval**, where many other model weights execute between consecutive invocations of the same target module?

This stage therefore combines:
- post-pressure refill dynamics;
- role-specific capacity-knee refinement;
- natural full-model decode occurrence profiling;
- one held-out layer validation.

Still no NVBit/full address trace/mechanism work.
