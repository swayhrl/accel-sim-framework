# New Codex Window Launcher — Node109 Q30 S2 Target Requalification V1

This launcher is for a new Codex window on node109.

Do not assume previous Codex chat context.

## Fetch

```text
branch:
hrl/c16-qwen3-30b-s2-target-requalification-v1
```

Read in order:

```text
1. docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/Q30_S2_REQUAL_CURRENT_STATE_V1.md
2. docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/Q30_S2_TARGET_REQUALIFICATION_GOAL_V1.md
3. this launcher
```

Accepted scientific upstream commits:

```text
S0 semantic/replay:
ba4358b8059be4fb5756f49852e50ecfe7dea9a3

S0 target qualification:
acbda39f5714cedb0e8b88ec32b07b4db2845885

S2/T2048 state/replay:
ee67225edc8fc5868de585d38e0391cbeb755d9f
```

Verify upstream review-pack SHA256SUMS before qualification.

## Execution branch

Create a fresh execution branch/worktree from:

```text
ee67225edc8fc5868de585d38e0391cbeb755d9f
```

Suggested branch:

```text
hrl/c16-qwen3-30b-s2-target-requalification-109-v1
```

Do not rewrite accepted S0 or S2 semantic/replay branches.

## Execution mode

Execute in GOAL MODE:

```text
docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
Q30_S2_TARGET_REQUALIFICATION_GOAL_V1.md
```

## Important boundaries

Node109 GPU actions still require normal ownership of:

```text
/data/c16/locks/c16_gpu_campaign.lock
```

Before profiler/CUDA work:

```text
inspect nvidia-smi
verify expected RTX4080 UUID
inspect lock
acquire lock normally
never kill/bypass another workload
```

Reuse accepted local model/runtime and accepted S2 replay states. Do not recopy 61 GB, retokenize, upgrade runtime, or rerun the complete S2 48-layer semantic stream if accepted state authorities remain intact.

## Main task

Use the exact accepted S2 Layer24 replay states to perform:

```text
S2 Prefill complete replay kernel census
S2 Decode3 complete replay kernel census
→ semantic launch attribution
→ bounded candidate selection
→ occurrence stability
→ bounded NCU characterization
→ S2 RTX4080-local static GLOBAL-MREF maps
→ one-MREF reachability canaries
→ direct S0-vs-S2 qualification delta
→ final 4–6 target formal capture portfolio
→ STOP
```

Do not assume S0 ordinals, function identity, or static MREF sets carry over to S2.

## Explicitly authorized

```text
diagnostic NSYS/NVTX census
bounded NCU on candidate occurrences
NVBit static/no-payload map
one-MREF reachability canary
short exact layer replays needed for qualification
```

## Explicitly forbidden in this Goal

```text
full MREF_SHARDED_COMPLETE_SET dynamic traces
large NVBit payload capture
broad formal NCU campaign
Pipeline raw/catalog admission
S2_CODE / S2_STRUCTURED
new full semantic scenario generation
```

## Required final decision

Successful completion requires:

```text
Q30_S2_LAYER_LOCAL_TARGET_REQUALIFICATION_PASS
Q30_FORMAL_LAYER_LOCAL_CAPTURE_PLAN_READY
FORMAL_CAPTURE_NOT_STARTED
```

Create:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_S2_TARGET_REQUALIFICATION_109_V1/
```

Then:

```text
commit
push
release lock
confirm GPU baseline/no profiler process
report branch/SHA/status
report S2 exact target matrix
report S0-vs-S2 differences
report final 4–6 selected formal targets
report per-target static MREF counts and formal shard-cost estimate
STOP
```

Do not automatically start formal capture.