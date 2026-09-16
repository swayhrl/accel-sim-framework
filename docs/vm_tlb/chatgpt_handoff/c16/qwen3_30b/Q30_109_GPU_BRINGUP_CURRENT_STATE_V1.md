# Qwen3-30B-A3B — Node109 GPU Bring-up Current State V1

## Status

The Q30 asset/control/CPU-preparation chain is accepted. The RTX4080 validation stage has not started yet.

Accepted upstream authority:

```text
asset archive:
d048d1a5348ff3ace248d1e62cdd8e071a82d5d1
QWEN3_30B_A3B_CANONICAL_ARCHIVE_PASS

control prep:
674d7acda0aaf072b7cd12cac84da9264b559cb2
Q30_CONTROL_PREP_PASS

CPU streaming prep:
b988e4052b5b92a0c46d658fdfa6c8c5102be739
Q30_CPU_STREAMING_IMPLEMENTATION_PREP_PASS

CPU streaming hardening:
6034071c76279952c1476626552a9eaaaab6ef0b
Q30_CPU_STREAMING_INTEGRATION_HARDENING_PASS
```

Current GPU state:

```text
GPU_VALIDATION_NOT_STARTED
```

Do not claim `QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING` until the GPU gates pass.

## Canonical model authority

```text
Qwen/Qwen3-30B-A3B
revision: ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
```

Canonical node164 asset:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Accepted payload:

```text
26 files
61,084,187,391 bytes total
16 weight shards
61,066,575,648 weight bytes
18,867 index tensor keys
18,867 safetensors-header tensor keys
missing = 0
unindexed = 0
payload inventory SHA256 =
20b21f889daf61d7362d4e0042ff7f3b2517cc1f0a917d3e0667654ded8cb30a
```

Node164 canonical is the provisioning authority. Do not execute from the original download root.

Node109 should consume the canonical model through the existing `hrl174new` SSH route and create a local working copy at:

```text
/data/c16/models/qwen3-30b-a3b/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Use sibling `.partial`, resume-capable copy, independent exact file-set/size/SHA verification, then no-overwrite promotion.

## Frozen input authority

Prospective pinned-tokenizer inputs live under node164:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/prospective_inputs/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Initial GPU bring-up scenario only:

```text
Q30_S0_TEXT
B1
context = 128
decode = 4
```

Accepted token-id SHA256:

```text
5800e1ffaa5546dd2d4331fff1c6687fe46e3b58fe95b1f768405244da3908d6
```

Accepted receipt SHA256:

```text
4b69d23ecce9925569b299c28af17de553f416730c9b57552b3f561dd12e05b6
```

GPU execution must consume the frozen token IDs directly. Do not retokenize in this Goal.

## CPU-prepared implementation

Production code is under:

```text
util/vm_tlb/c16/qwen3_30b/
```

Accepted CPU hardening proved:

```text
48-layer materialization planning
18,867 exact runtime/index state closure
shard-aware safetensors loading
strict state_dict key/shape/dtype injection
explicit release to meta
TARGET_LAYER_STATE identity validation
symmetric provisioning verification
CPU tiny Prefill equivalence
CPU tiny Decode/KV equivalence
CPU tiny complete-layer replay equivalence
router/expert identity equivalence
bounded real canonical Layer-0 exact-runtime materialization
```

These are CPU-only engineering gates, not GPU evidence. Fix engineering bugs if CUDA exposes them, but do not weaken model/runtime/input semantics to get a PASS.

## Node109 platform authority

Expected platform:

```text
RTX4080 16 GB
GPU UUID: GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59
driver: 580.178.04
CUDA toolkit: 12.8
CPython: /data/c16/env/cpython-3.10.12
```

Do not modify `/data/c16/env/c16-py310` in place. Create a dedicated Q30 GPU environment.

CPU compatibility reference:

```text
Torch 2.5.1+cpu
Transformers 4.51.0
Safetensors 0.5.2
Accelerate 1.3.0
```

On node109 use the CUDA-capable Torch authority compatible with this host, while keeping Q30 isolated. Freeze exact package versions and the actual attention/MoE implementation path.

Do not silently enable a different fused/grouped expert implementation or attention backend merely because it is available.

## GPU serialization

All GPU actions must acquire:

```text
/data/c16/locks/c16_gpu_campaign.lock
```

Do not delete or bypass the lock blindly. If another scientific workload appears, wait rather than kill it.

## Scientific gate for this stage

Required accepted states:

```text
Q30_WORKING_COPY_PASS
Q30_GPU_RUNTIME_AUTHORITY_PASS
Q30_SEMANTIC_STREAMING_S0_PASS
Q30_TARGET_LAYER_STATE_PASS
Q30_EXACT_LAYER_REPLAY_CANARY_PASS
```

Only after all five pass may the final status be:

```text
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING
```

Large NCU/NVBit/NSYS profiling is not part of this stage.