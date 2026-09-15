# New Codex Window Launcher — Q30 CPU Streaming Implementation Prep V1

This launcher is for a completely new 174-new Codex window.

Do not assume access to prior Codex chat context.

## Fetch

```text
branch:
hrl/c16-qwen3-30b-cpu-streaming-impl-prep-v1
```

Read the branch HEAD after fetch and verify it contains this launcher plus:

```text
docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
Q30_CPU_STREAMING_PREP_CURRENT_STATE_V1.md

and

docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
Q30_CPU_STREAMING_IMPLEMENTATION_PREP_GOAL_V1.md
```

Also read the accepted upstream review pack:

```text
docs/vm_tlb/review_packs/C16_QWEN3_30B_CONTROL_PREP_174NEW_V1/
```

Especially:

```text
README.md
Q30_EXECUTION_PREP_PLAN.json
Q30_MODEL_LAYOUT.tsv
Q30_LAYER_SUMMARY.tsv
Q30_EXPERT_SUMMARY.tsv
Q30_COMPONENT_SUMMARY.tsv
Q30_INPUT_BINDINGS.tsv
Q30_INPUT_BINDING_RECEIPTS.tsv
Q30_RUNTIME_REQUIREMENTS.json
Q30_NODE109_PROVISIONING_MANIFEST.tsv
SHA256SUMS
```

## Execution mode

Execute in GOAL MODE:

```text
docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
Q30_CPU_STREAMING_IMPLEMENTATION_PREP_GOAL_V1.md
```

Create a fresh execution branch/worktree.

Suggested branch:

```text
hrl/c16-qwen3-30b-cpu-streaming-impl-prep-174new-v1
```

Suggested worktree:

```text
/root/workspace/accel-sim-framework-q30-cpu-streaming-impl-prep-v1
```

## Critical boundary

This is CPU-only work on 174-new.

Node109 is currently busy with another GPU capture campaign.

Therefore:

```text
DO NOT write to node109
DO NOT copy the 61 GB model to node109
DO NOT run CUDA/GPU workloads
DO NOT run Qwen3-30B on GPU
DO NOT run NCU/NVBit/NSYS
DO NOT touch the node109 GPU lock
DO NOT delete/modify canonical assets or frozen Q30 inputs
```

You are authorized to:

```text
create an isolated CPU-only Python environment on 174-new
install a pinned compatible Transformers/runtime stack if needed
read exact canonical config/index/safetensors headers
use small synthetic safetensors/tiny Qwen3-MoE fixtures
add production code and CPU tests to the repository
prepare node109 bootstrap/provisioning scripts without executing them there
```

Do not use `latest` package versions without justification. Derive runtime compatibility from the exact archived Qwen3 authority and pin exact versions used by the CPU/meta compatibility tests.

## Main objective

Move engineering/debug work off the future RTX4080 critical path.

By the end of this Goal, node109 should later need mainly:

```text
1. exact 61 GB local provisioning
2. create/finalize isolated Q30 GPU runtime
3. run bounded Q30_S0_TEXT semantic streaming
4. freeze real Prefill/Decode TARGET_LAYER_STATE
5. run real exact full-layer replay canaries
```

The CPU stage should already have prepared and tested:

```text
exact tensor/runtime mapping
48 layer materialization plans
shard-aware materializer
semantic streaming orchestration
KV/state interfaces
TARGET_LAYER_STATE serializer/validator
full-layer replay harness
runtime bootstrap
working-copy provisioner
tiny Qwen3-MoE Prefill/Decode/replay equivalence regression
```

## Expected final state

```text
Q30_CPU_STREAMING_IMPLEMENTATION_PREP_PASS
GPU_VALIDATION_NOT_STARTED
```

Required review pack:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_CPU_STREAMING_IMPL_PREP_174NEW_V1/
```

Do not claim:

```text
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING
```

because real node109 semantic/replay validation has not happened yet.

## Completion

When complete:

```text
commit
push
report execution branch
report final commit SHA
report final status
report review-pack entry point
summarize code/tests and any remaining GPU-only open issues
STOP
```
