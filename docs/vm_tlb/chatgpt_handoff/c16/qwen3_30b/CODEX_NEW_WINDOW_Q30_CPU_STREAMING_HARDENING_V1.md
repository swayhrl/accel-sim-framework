# New Codex Window Launcher — Q30 CPU Streaming Hardening V1

This launcher is for a completely new 174-new Codex window.

Do not assume prior Codex chat context.

## Fetch

```text
branch:
hrl/c16-qwen3-30b-cpu-streaming-hardening-v1
```

Read in order:

```text
docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
Q30_CPU_STREAMING_PREP_AUDIT_AFTER_B988.md

then

docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
Q30_CPU_STREAMING_INTEGRATION_HARDENING_GOAL_V1.md
```

Consume accepted upstream review packs for:

```text
asset archive d048d1a5348ff3ace248d1e62cdd8e071a82d5d1
control prep 674d7acda0aaf072b7cd12cac84da9264b559cb2
CPU prep b988e4052b5b92a0c46d658fdfa6c8c5102be739
```

## Execution

Execute in GOAL MODE:

```text
docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
Q30_CPU_STREAMING_INTEGRATION_HARDENING_GOAL_V1.md
```

Suggested fresh execution branch:

```text
hrl/c16-qwen3-30b-cpu-streaming-hardening-174new-v1
```

Suggested worktree:

```text
/root/workspace/accel-sim-framework-q30-cpu-streaming-hardening-v1
```

## Critical boundary

Node109 is still occupied by another GPU scientific campaign.

This entire Goal is CPU-only on 174-new.

DO NOT:

```text
write to node109
copy the 61 GB model to node109
run CUDA/GPU workloads
run NCU/NVBit/NSYS
touch node109 GPU lock
modify canonical node164 model files
modify frozen Q30 prospective inputs
```

Reading canonical model files from node164 for exact headers/tensors and a bounded real-layer CPU materialization canary is authorized.

## Main requirement

Do not treat the existing tiny equivalence result as proof that the production streaming path is complete.

The hardening must actually exercise:

```text
sharded safetensors
-> production Materializer
-> meta exact runtime module
-> tensor injection
-> exact runtime forward
-> KV/state handling
-> tensor/module release
-> next layer
```

and an independent full-layer replay from frozen state.

The tiny streaming side must not simply call an already fully resident tiny model.

Also fix exact-set provisioning verification: destination extra files must fail.

Strengthen `TARGET_LAYER_STATE` to the full identity/state contract in the Goal.

## Real-authority canary

After checking available host memory, perform one bounded real canonical Qwen3 layer materialization in a subprocess if safe. Do not load the whole model into RAM.

No real-model CPU performance claims are needed.

## Expected final state

```text
Q30_CPU_STREAMING_INTEGRATION_HARDENING_PASS
GPU_VALIDATION_NOT_STARTED
```

Required review pack:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_CPU_STREAMING_HARDENING_174NEW_V1/
```

Do NOT claim:

```text
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING
```

That still requires real node109 S0 semantic streaming and RTX4080 exact-layer replay canaries.

Commit, push, report branch/SHA/status/review-pack/tests/real-layer-canary/open GPU-only issues, then STOP.