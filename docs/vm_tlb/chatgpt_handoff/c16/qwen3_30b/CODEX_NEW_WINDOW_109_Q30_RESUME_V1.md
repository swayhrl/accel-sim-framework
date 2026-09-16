# New Codex Window Launcher — Node109 Q30 Resume V1

This launcher is for a new Codex window on node109 resuming the paused Qwen3-30B-A3B GPU bring-up.

Do not assume any previous Codex chat context.

## Coordination authority

Fetch:

```text
hrl/c16-qwen3-30b-gpu-resume-v1
```

Verify this launcher and the following files are present:

```text
docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
Q30_109_RESUME_CURRENT_STATE_V1.md
Q30_109_S0_STREAMING_REPLAY_RESUME_GOAL_V1.md
```

The resume coordination branch is documentation authority only.

The actual execution history to continue is:

```text
branch:
hrl/c16-qwen3-30b-gpu-streaming-replay-109-v1

checkpoint commit:
d87d7726bc9d5a142519cae95a081b94018c71a2
```

Do not discard/rewrite this execution history.

If the existing worktree for that branch is still clean and usable, continue in it. Otherwise create a new worktree from the exact checkpoint commit/branch without deleting the old one until its state is understood.

## Read order

Read:

```text
1. Q30_109_RESUME_CURRENT_STATE_V1.md
2. Q30_109_S0_STREAMING_REPLAY_RESUME_GOAL_V1.md
3. accepted checkpoint review pack:
   docs/vm_tlb/review_packs/C16_QWEN3_30B_PRE_SEMANTIC_CHECKPOINT_109_V1/
```

Also inspect `RESUME_POINTERS.json` and verify every preserved local path before GPU execution.

## Execution mode

Execute in GOAL MODE:

```text
docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
Q30_109_S0_STREAMING_REPLAY_RESUME_GOAL_V1.md
```

Continue the existing execution branch:

```text
hrl/c16-qwen3-30b-gpu-streaming-replay-109-v1
```

Do not make a new scientific execution branch unless the existing branch is technically unusable; if that happens, bind the new branch explicitly to checkpoint `d87d7726...`.

## User authorization

The user reports node109 is available again for this work.

This does not override lock/process checks. Before GPU work:

```text
inspect nvidia-smi
inspect /data/c16/locks/c16_gpu_campaign.lock
verify the expected GPU UUID
acquire the campaign lock normally
```

Never kill another workload or bypass a live lock.

## Preserved resources — do not rebuild unnecessarily

Expected preserved model:

```text
/data/c16/models/qwen3-30b-a3b/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Expected preserved runtime:

```text
/data/c16/env/c16-qwen3-30b-hf451-gpu
```

Expected frozen input:

```text
/data/c16/inputs/qwen3-30b-a3b/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
Q30_S0_TEXT.token_ids.json
Q30_S0_TEXT.receipt.json
```

Do not:

```text
recopy 61 GB when local SHA closure passes
upgrade/reinstall the runtime when authority passes
retokenize S0
change attention implementation
change MoE implementation
change BF16/expert count/top-k/context/batch
rerun Layer-0 canary unless resume validation requires it
```

## Main work now

The new work starts at:

```text
real Q30_S0 Prefill semantic layer streaming
→ 48 exact original layers
→ freeze Prefill layer-24 call-boundary state
→ four exact Decode forwards with per-layer KV
→ freeze Decode step-3 layer-24 state
→ fresh-process complete-layer replay x2 per state
→ archive replay-state provenance
```

The fixed canaries are not negotiable/post-hoc selectable:

```text
PREFILL layer 24
DECODE step 3 (zero-based fourth Decode forward), layer 24
```

## Acceptance boundary

Inherited from checkpoint:

```text
Q30_WORKING_COPY_PASS
Q30_GPU_RUNTIME_PREP_PASS
Q30_META_INDEX_CLOSURE_PASS
Q30_LAYER0_MATERIALIZATION_CANARY_PASS
Q30_S0_INPUT_LOCAL_AUTHORITY_PASS
```

New required gates:

```text
Q30_SEMANTIC_STREAMING_S0_PASS
Q30_TARGET_LAYER_STATE_PASS
Q30_EXACT_LAYER_REPLAY_CANARY_PASS
```

Only then:

```text
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING
```

If layer replay is not bitwise identical, do not silently relax tolerance and pass. Diagnose and leave the stage blocked for review.

## Explicit stop boundary

Even after PASS, do not start:

```text
NCU
NVBit
NSYS
S1/S2
formal kernel census/target qualification
```

Create final review pack:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_GPU_STREAMING_REPLAY_109_V1/
```

Then:

```text
commit
push
release GPU lock
confirm GPU baseline/no Q30 process
report branch/SHA/status/review-pack
STOP
```
