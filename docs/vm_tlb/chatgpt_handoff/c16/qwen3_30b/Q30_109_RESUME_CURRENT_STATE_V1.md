# Qwen3-30B-A3B — Node109 Resume State V1

Status: `PRE_SEMANTIC_CHECKPOINT_ACCEPTED / GPU_WORK_RESUMABLE`

This document is the authoritative resume context for continuing Qwen3-30B-A3B work on node109 after the clean pre-semantic pause.

## Accepted checkpoint

Execution branch:

```text
hrl/c16-qwen3-30b-gpu-streaming-replay-109-v1
```

Accepted checkpoint commit:

```text
d87d7726bc9d5a142519cae95a081b94018c71a2
```

Accepted checkpoint status:

```text
Q30_PRE_SEMANTIC_GPU_BRINGUP_CHECKPOINT_PASS
```

Checkpoint review pack:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_PRE_SEMANTIC_CHECKPOINT_109_V1/
```

The checkpoint explicitly froze the following state:

```text
Q30_WORKING_COPY_PASS
Q30_GPU_RUNTIME_PREP_PASS
Q30_META_INDEX_CLOSURE_PASS
Q30_LAYER0_MATERIALIZATION_CANARY_PASS
Q30_S0_INPUT_LOCAL_AUTHORITY_PASS
```

and explicitly left:

```text
Q30_SEMANTIC_STREAMING_S0 = NOT_STARTED
Q30_TARGET_LAYER_STATE = NOT_STARTED
Q30_EXACT_LAYER_REPLAY_CANARY = NOT_STARTED
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING = NOT_CLAIMED
```

Do not reinterpret the pause checkpoint as semantic/replay validation.

---

## Model / local working copy

Model identity:

```text
Qwen/Qwen3-30B-A3B
revision:
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
```

Node109 local model path:

```text
/data/c16/models/qwen3-30b-a3b/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Accepted local payload:

```text
26 regular payload files
61,084,187,391 bytes
working-copy inventory SHA256:
20b21f889daf61d7362d4e0042ff7f3b2517cc1f0a917d3e0667654ded8cb30a
working-copy receipt SHA256:
f49a40631ceac11fda5378ec18ed35eb5da3b3e6e24bc667a77994eed0631f25
```

The local working copy already passed exact symmetric regular-file set / size / SHA verification against the node164 canonical model. Do not recopy 61 GB unless this local authority is invalidated.

On resume, perform a local integrity recheck against the frozen local inventory/receipt before GPU execution. A full local payload SHA recheck is preferred. There is no need to transfer the model again from node164 when the local copy is intact.

---

## Runtime authority

Preserved runtime path:

```text
/data/c16/env/c16-qwen3-30b-hf451-gpu
```

Accepted baseline identity:

```text
Python:        3.10.12
Torch:         2.5.1+cu124
Torch CUDA:    12.4
Transformers:  4.51.0
Safetensors:   0.8.0
Accelerate:    1.1.1
Tokenizers:    0.21.0
attention:     SDPA
GPU:           NVIDIA GeForce RTX 4080
GPU UUID:      GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59
driver:        580.178.04
CUDA toolkit:  12.8
```

Deployment identity:

```text
qwen3_30b_a3b_hf451_bf16_sdpa_qwen3moe_sparse_expert_loop
```

Runtime authority SHA256 from checkpoint:

```text
8feb468251b3dda5c37229f962ae9f2f4f6773efb64fd9b62949190a43c7add7
```

Qwen3 runtime source fingerprint was frozen by the checkpoint. Do not upgrade/reinstall/change this runtime merely because another version is available. Any runtime repair must preserve the deployment identity or be treated as a new deployment and separately reviewed.

---

## Meta/index closure and capacity canary

Accepted exact closure:

```text
archive index keys: 18,867
runtime state keys: 18,867
missing: 0
unexpected: 0
layers: 48
experts: 128
top-k: 8
```

Accepted real Layer-0 CUDA materialization canary:

```text
layer: 0
393 tensors
1,246,241,280 weight bytes
torch.bfloat16
peak allocated: 1,246,241,792 bytes
peak reserved:  1,382,023,168 bytes
post-release allocated: 0
PASS
```

Do not rerun this canary unless resume preflight indicates the runtime/model authority has changed.

---

## Frozen S0 input authority

Only resume with:

```text
Q30_S0_TEXT
B1 / context 128 / decode 4
```

Local token IDs:

```text
/data/c16/inputs/qwen3-30b-a3b/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
Q30_S0_TEXT.token_ids.json
```

Token IDs SHA256:

```text
5800e1ffaa5546dd2d4331fff1c6687fe46e3b58fe95b1f768405244da3908d6
```

Local input receipt:

```text
/data/c16/inputs/qwen3-30b-a3b/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
Q30_S0_TEXT.receipt.json
```

Receipt SHA256:

```text
4b69d23ecce9925569b299c28af17de553f416730c9b57552b3f561dd12e05b6
```

Do not retokenize or regenerate this scenario.

---

## Upstream code / implementation authority

Accepted CPU hardening commit:

```text
6034071c76279952c1476626552a9eaaaab6ef0b
```

It established:

```text
strict state_dict key/shape/dtype injection
shard-aware safetensors materialization
explicit release back to meta
exact symmetric provisioning verification
TARGET_LAYER_STATE identity validation
tiny Prefill/Decode/KV/replay equivalence
real canonical Layer-0 CPU materialization canary
```

The node109 execution branch already contains the bring-up implementation/state needed up to the pause checkpoint.

---

## GPU ownership at pause

The checkpoint ended with:

```text
no Q30 CUDA/Python process
no compute app
~35 MiB driver baseline only
no live holder of /data/c16/locks/c16_gpu_campaign.lock
Q30_GPU_AND_LOCK_RELEASED
```

The user now authorizes node109 to resume this Q30 work.

Nevertheless, before every GPU stage:

```text
inspect nvidia-smi
inspect /data/c16/locks/c16_gpu_campaign.lock
acquire the lock normally
never kill or bypass another workload
```

---

## Exact next stage

Resume from:

```text
Q30_S0 semantic layer streaming
    -> freeze real Prefill Layer-24 target state
    -> perform four Decode steps with exact per-layer KV
    -> freeze real Decode step-3 Layer-24 target state
    -> independent RTX4080 complete-layer replay
    -> replay determinism
```

The fixed validation canaries remain:

```text
Prefill: layer 24, immediately before complete layer forward
Decode:  step 3, layer 24, immediately before complete layer forward
```

Do not post-hoc choose easier layers.

Only after both semantic streaming and both exact replay canaries pass may the stage claim:

```text
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING
```

Even then, stop before formal NCU/NVBit/NSYS or S1/S2 expansion.
