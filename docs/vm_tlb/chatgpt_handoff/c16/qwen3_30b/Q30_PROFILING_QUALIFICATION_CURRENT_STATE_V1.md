# Qwen3-30B-A3B profiling qualification — current state V1

Status at upstream scientific checkpoint:

```text
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING
```

Accepted execution branch/commit:

```text
hrl/c16-qwen3-30b-gpu-streaming-replay-109-v1
ba4358b8059be4fb5756f49852e50ecfe7dea9a3
```

Accepted review pack:

```text
docs/vm_tlb/review_packs/C16_QWEN3_30B_GPU_STREAMING_REPLAY_109_V1/
```

The accepted evidence scope is deliberately limited to:

```text
FORMAL_LAYER_LOCAL
FORMAL_KERNEL_LOCAL
```

It is not full-model-resident timing/cache/TLB evidence.

## Frozen deployment identity

Model:

```text
Qwen/Qwen3-30B-A3B
revision: ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
```

Local node109 model authority:

```text
/data/c16/models/qwen3-30b-a3b/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Local runtime:

```text
/data/c16/env/c16-qwen3-30b-hf451-gpu
```

Frozen baseline deployment facts from accepted checkpoint:

```text
Python 3.10.12
Torch 2.5.1+cu124
Torch CUDA runtime 12.4
Transformers 4.51.0
attention implementation: SDPA
Qwen3 MoE runtime: official Transformers Qwen3Moe implementation
128 experts
top-k 8
48 decoder layers
GPU: RTX4080 / GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59
driver 580.178.04
CUDA toolkit 12.8
```

Do not silently change any of these during qualification.

## Accepted S0 semantic run

Run ID:

```text
Q30_S0_STREAM_V1_20260916T045044Z
```

Scenario:

```text
Q30_S0_TEXT
B1 / T128 / Decode4
```

Accepted semantic outputs:

```text
Prefill greedy token: 304
Decode step 0: 2797
Decode step 1: 4128
Decode step 2: 13
Decode step 3: 576
```

Real semantic streaming completed all 48 Prefill layers and all four Decode forwards.

## Frozen exact replay states

Prefill fixed canary:

```text
phase: PREFILL
layer: 24
local:
/data/c16/qwen3_30b/bringup/Q30_S0_STREAM_V1_20260916T045044Z/target_states/prefill
```

Decode fixed canary:

```text
phase: DECODE
decode step: 3
layer: 24
local:
/data/c16/qwen3_30b/bringup/Q30_S0_STREAM_V1_20260916T045044Z/target_states/decode3
```

Node164 provenance authority:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/
qwen3_30b_replay_states/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
Q30_S0_STREAM_V1_20260916T045044Z/
```

Both Prefill and Decode complete-layer replay passed:

```text
source == replay bitwise
router evidence == exact
replay1 == replay2
```

The replay harness is therefore the execution vehicle for profiling qualification. Do not profile the 61 GB semantic-streaming pass itself unless a later Goal explicitly asks for it.

## Why the next stage is qualification, not immediate formal capture

The replay states prove semantic equivalence of the complete Layer-24 execution, but we have not yet frozen which concrete CUDA kernels are the scientifically useful trace targets.

The next stage must determine, from the actual replay execution:

```text
kernel launch census
semantic region
exact occurrence identity
function/code-object identity
grid/block
rough duration contribution
memory-traffic importance
static GLOBAL MREF set
NVBit instrumentation viability
```

Only after those facts are closed should we launch large NCU/NVBit capture.

## Scientific target families of interest

These are semantic families, not pre-selected CUDA kernel names:

```text
Prefill Attention
Prefill Router / dispatch / combine where material
Prefill MoE expert computation / expert-weight traffic
Decode Attention / KV path
Decode Router / dispatch / combine where material
Decode MoE expert computation / expert-weight traffic
```

Do not force every family to produce a formal target. If a family has negligible GPU-memory significance or no stable kernel identity, report that rather than choosing a weak target.

## Scenario boundary

This qualification stage uses only the already-closed S0 Layer-24 states.

Do not interpret S0/T128 as the final Q30 formal campaign. A later scenario-expansion stage may generate S2/T2048 and/or longer-context states to test context/expert-working-set scaling after target families are known.

Therefore the next Goal may establish:

```text
stable S0 target families and profiling procedure
```

but must not claim:

```text
S0 is globally representative of all Q30 Prefill/Decode behavior
```
