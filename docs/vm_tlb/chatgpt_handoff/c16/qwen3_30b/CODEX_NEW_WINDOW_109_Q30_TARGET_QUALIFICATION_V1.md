# New Codex Window Launcher — Node109 Q30 Target Qualification V1

This launcher is for a new Codex window on node109 after accepted Q30 S0 semantic streaming and exact full-layer replay.

Do not assume prior Codex chat context.

## Coordination authority

Fetch:

```text
hrl/c16-qwen3-30b-profiling-qualification-v1
```

Read:

```text
docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
Q30_PROFILING_QUALIFICATION_CURRENT_STATE_V1.md

and

docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
Q30_S0_LAYER_LOCAL_TARGET_QUALIFICATION_GOAL_V1.md
```

Scientific upstream execution authority:

```text
branch:
hrl/c16-qwen3-30b-gpu-streaming-replay-109-v1

commit:
ba4358b8059be4fb5756f49852e50ecfe7dea9a3
```

Accepted upstream review pack:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_GPU_STREAMING_REPLAY_109_V1/
```

Verify its SHA256SUMS before profiler work.

## Execution branch

Create a fresh qualification branch/worktree from the accepted scientific commit, for example:

```text
hrl/c16-qwen3-30b-s0-target-qualification-109-v1
```

Do not rewrite the accepted semantic/replay branch.

## GPU ownership

The user may make node109 available for this stage, but that never overrides normal ownership checks.

Before profiler/GPU actions:

```text
inspect nvidia-smi
inspect /data/c16/locks/c16_gpu_campaign.lock
verify RTX4080 UUID
acquire the lock normally
```

Never kill another workload or bypass a live lock.

## Preserved authorities

Do not rebuild or modify:

```text
/data/c16/models/qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
/data/c16/env/c16-qwen3-30b-hf451-gpu
/data/c16/inputs/qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Do not regenerate the 48-layer S0 semantic run.

Use the accepted exact Layer-24 replay states:

```text
/data/c16/qwen3_30b/bringup/Q30_S0_STREAM_V1_20260916T045044Z/target_states/prefill
/data/c16/qwen3_30b/bringup/Q30_S0_STREAM_V1_20260916T045044Z/target_states/decode3
```

Revalidate state manifests/SHA, then use complete-layer replay as the profiling vehicle.

## Main task

Execute in GOAL MODE:

```text
docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
Q30_S0_LAYER_LOCAL_TARGET_QUALIFICATION_GOAL_V1.md
```

The work sequence is:

```text
revalidate exact replays
-> full-layer kernel census (Prefill + Decode)
-> semantic classification
-> bounded memory-important candidate set
-> bounded NCU characterization
-> freeze exact occurrence identity
-> NVBit static GLOBAL-MREF map / reachability
-> freeze small qualified target portfolio
-> STOP
```

Diagnostic NSYS is authorized for launch census.

Bounded NCU is authorized for candidate qualification.

Static/no-payload NVBit and a tiny one-MREF reachability canary are authorized.

Do NOT run the large formal trace campaign in this Goal.

In particular, do NOT:

```text
run full MREF-sharded dynamic trace sets
collect large NVBit payloads
start broad formal NCU capture
run S1/S2 semantic streaming
change BF16/SDPA/MoE/expert/top-k identity
modify the frozen target-state bundles
```

## Target philosophy

Do not preselect CUDA kernel names from assumptions.

Use actual replay evidence to find stable target occurrences for semantic families such as:

```text
Prefill Attention
Prefill MoE expert-weight path
Decode Attention/KV
Decode MoE expert-weight path
```

Router/dispatch/combine only become targets if actual census/NCU/NVBit evidence shows distinct memory relevance.

Every final target must be bound by more than a kernel-name substring. Freeze launch ordinal, grid/block, runtime/replay-state identity and code-object/function identity where tooling permits.

## Expected final status

```text
Q30_S0_LAYER_LOCAL_TARGET_QUALIFICATION_PASS
```

Required review pack:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_S0_TARGET_QUALIFICATION_109_V1/
```

The pack must explicitly state whether a larger scenario such as S2/T2048 should be generated before formal capture.

After PASS:

```text
commit
push
release GPU lock
verify GPU baseline/no Q30 profiler process
report branch/SHA/status/qualified targets/review-pack
STOP
```

Do not automatically continue into formal NCU/NVBit capture.
