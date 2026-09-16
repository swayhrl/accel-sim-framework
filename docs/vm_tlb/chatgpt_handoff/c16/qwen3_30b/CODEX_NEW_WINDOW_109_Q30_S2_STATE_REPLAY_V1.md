# New Codex Window Launcher — Node109 Q30 S2/T2048 State Replay V1

This launcher is for a new Codex window on node109.

Do not assume prior chat context.

## Fetch

```text
branch:
hrl/c16-qwen3-30b-s2-state-expansion-v1
```

Verify branch HEAD contains:

```text
docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
Q30_S2_STATE_EXPANSION_CURRENT_STATE_V1.md
Q30_S2_T2048_STATE_REPLAY_GOAL_V1.md
CODEX_NEW_WINDOW_109_Q30_S2_STATE_REPLAY_V1.md
```

## Scientific base

Create a fresh execution branch/worktree from accepted S0 target qualification commit:

```text
acbda39f5714cedb0e8b88ec32b07b4db2845885
```

Suggested branch:

```text
hrl/c16-qwen3-30b-s2-state-replay-109-v1
```

Do not rewrite accepted S0 semantic/replay or qualification branches.

## Read order

Read:

```text
1. Q30_S2_STATE_EXPANSION_CURRENT_STATE_V1.md
2. Q30_S2_T2048_STATE_REPLAY_GOAL_V1.md
3. accepted S0 semantic/replay pack:
   docs/vm_tlb/review_packs/C16_QWEN3_30B_GPU_STREAMING_REPLAY_109_V1/
4. accepted S0 qualification pack:
   docs/vm_tlb/review_packs/C16_QWEN3_30B_S0_TARGET_QUALIFICATION_109_V1/
5. accepted Q30 input authority pack:
   docs/vm_tlb/review_packs/C16_QWEN3_30B_CONTROL_PREP_174NEW_V1/
```

Verify relevant `SHA256SUMS` before GPU execution.

## Preserved authorities

Use the existing local model and runtime when they revalidate:

```text
/data/c16/models/qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/

/data/c16/env/c16-qwen3-30b-hf451-gpu
```

Do not recopy/reinstall unnecessarily.

## S2 input

Use only:

```text
Q30_S2_TEXT
B1/T2048/D32 parent binding
```

Token IDs SHA256:

```text
00d47e2312fb3db3585b5396ebc7484507356148019a845c8253c6d58d56d4f5
```

Receipt SHA256:

```text
e3368d01dc311d134e1f62c6412a3c05b2a2fb1de527f1947f3b7502af28c99a
```

Do not retokenize.

This Goal executes only:

```text
full T2048 Prefill
+ Decode steps 0..3
```

Classify the bounded slice as:

```text
Q30_S2_TEXT_PREFIX_D4
parent_binding = Q30_S2_TEXT B1/T2048/D32
```

## GPU ownership

Before CUDA:

```text
inspect nvidia-smi
verify RTX4080 UUID
inspect /data/c16/locks/c16_gpu_campaign.lock
acquire lock normally
```

Never kill another workload or bypass a live lock.

## Fixed replay states

Freeze exactly:

```text
PREFILL layer 24 at T2048
DECODE step 3 layer 24 after T2048 Prefill
```

Do not choose a different layer after seeing results.

## Required work

Execute in GOAL MODE:

```text
docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
Q30_S2_T2048_STATE_REPLAY_GOAL_V1.md
```

Main sequence:

```text
revalidate model/runtime
→ provision exact frozen S2_TEXT input
→ T2048 48-layer Prefill
→ freeze Prefill L24 state
→ Decode steps 0..3
→ freeze Decode3 L24 state
→ fresh-process complete-layer replay x2 per state
→ S0-vs-S2 semantic scaling summary
→ node164 replay-state provenance archive
→ STOP
```

Do NOT run in this Goal:

```text
NSYS
NCU
NVBit
formal target qualification
formal capture
S2_CODE
S2_STRUCTURED
Decode steps 4..31 unless debugging correctness
```

Do not assume S0 launch ordinal/static-MREF identities remain valid for S2.

## Expected final state

```text
Q30_S2_T2048_STATE_REPLAY_PASS
FORMAL_CAPTURE_NOT_YET_AUTHORIZED
```

Required review pack:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_S2_T2048_STATE_REPLAY_109_V1/
```

After completion:

```text
commit
push
release GPU lock
verify GPU baseline/no Q30 process
report branch/SHA/status/review-pack
STOP
```
