# New Codex Window Launcher — Node109 Q30 GPU Bring-up V1

This launcher is for a completely new Codex window operating on node109.

Do not assume access to prior Codex chat context.

## Fetch

Fetch/pull:

```text
hrl/c16-qwen3-30b-gpu-bringup-v1
```

Read branch HEAD after fetch and verify it contains:

```text
docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
Q30_109_GPU_BRINGUP_CURRENT_STATE_V1.md

and

docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
Q30_109_GPU_STREAMING_REPLAY_GOAL_V1.md
```

Also consume accepted review packs from these upstream commits:

```text
d048d1a5348ff3ace248d1e62cdd8e071a82d5d1
674d7acda0aaf072b7cd12cac84da9264b559cb2
b988e4052b5b92a0c46d658fdfa6c8c5102be739
6034071c76279952c1476626552a9eaaaab6ef0b
```

especially the Q30 asset archive, control prep and CPU hardening packs.

## Execute

Execute in GOAL MODE:

```text
docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
Q30_109_GPU_STREAMING_REPLAY_GOAL_V1.md
```

Create a fresh execution branch/worktree.

Suggested execution branch:

```text
hrl/c16-qwen3-30b-gpu-streaming-replay-109-v1
```

Use the existing node109 repository clone as authority for worktree creation; do not disturb another worktree/branch.

## User authorization

The user has explicitly stated node109 is idle and available for this Q30 stage.

That authorization does not waive scientific serialization. Before each GPU phase, acquire and hold:

```text
/data/c16/locks/c16_gpu_campaign.lock
```

Verify the GPU is actually idle; do not kill another process if the situation changed.

## First actions

Before GPU execution:

```text
1. platform/lock/disk preflight
2. provision exact canonical 61.08 GB working copy locally
3. copy and SHA-close frozen Q30_S0_TEXT input authority
4. create isolated Q30 GPU runtime
5. meta/index/runtime-state closure
6. real Layer-0 CUDA materialization/release canary
```

Only then run real S0 semantic streaming.

## Fixed scope

Run only:

```text
Q30_S0_TEXT
B1
T128
Decode 4
```

Canary target states are fixed at:

```text
Prefill: layer 24
Decode: step 3, layer 24
```

These are validation canaries, not final representative profiling targets.

## Critical rules

Do not:

```text
retokenize S0
change BF16 precision
prune experts
change top-k
change revision
change batch/context
use quantization as substitute
use Unified Memory oversubscription as formal evidence
run formal NCU/NVBit/NSYS
start S1/S2
make full-model-resident performance/cache/TLB claims
```

Use exact runtime modules and the hardened production materializer/state code. Do not replace the full-layer acceptance canary with a standalone GEMM.

Large hidden/KV/target-state artifacts belong on the data plane, not in Git.

## Expected success

The following must all PASS:

```text
Q30_WORKING_COPY_PASS
Q30_GPU_RUNTIME_AUTHORITY_PASS
Q30_SEMANTIC_STREAMING_S0_PASS
Q30_TARGET_LAYER_STATE_PASS
Q30_EXACT_LAYER_REPLAY_CANARY_PASS
```

Only then report:

```text
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING
```

Required review pack:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_GPU_STREAMING_REPLAY_109_V1/
```

## Completion

When complete:

```text
commit
push
report execution branch
report final commit SHA
report final status
report working-copy closure
report runtime/deployment identity
report S0 Prefill+Decode completion
report target-state paths/hashes
report exact replay equivalence
report peak GPU memory
report review-pack path
STOP
```

Do not proceed automatically into NCU/NVBit profiling after the PASS.