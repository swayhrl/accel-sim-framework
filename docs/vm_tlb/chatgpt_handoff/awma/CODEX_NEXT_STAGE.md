# CODEX_NEXT_STAGE

Status: **ACTIVE**

Stage:

```text
AWMA_Q05_REPRESENTATIVENESS_AND_TRANSLATION_BEHAVIOR_V1
```

This is a two-track parallel characterization stage. It is not a new TLB/PTW mechanism stage.

## Objective

Resolve two questions before any further architecture sweep or mechanism design:

1. Inside the complete Q05 FlashAttention kernel, determine whether the observed translation pressure is cold-first-touch, streaming/low-reuse, outstanding-translation fanout, persistent post-fill reuse, or a mixture; also locate the existing 10k/50k windows within the complete kernel.
2. Across the complete frozen Qwen2.5 B1/T2048/Decode32 run, determine how frequent and representative the Q05 FlashAttention implementation is relative to all kernels and Attention-related kernels.

## Coordination branch

ChatGPT handoff branch:

```text
hrl/awma-q05-representativeness-handoff-v1
```

Base scientific characterization anchor:

```text
bb92e5a1559dd7e2b2520e9a7a4937262664512c
```

Codex must first fetch the coordination branch and read, in order:

```text
docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/awma/DISCUSSION_REFERENCE.md
docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE.md
```

Then select exactly one node-specific specification below.

## Track A — 174-new

Node role:

```text
174-new / port 2239
Simulation-plane analysis owner
```

Execute:

```text
docs/vm_tlb/chatgpt_handoff/awma/
CODEX_NEXT_STAGE_174NEW_Q05_FULL_TRANSLATION_BEHAVIOR_V1.md
```

Expected completion marker:

```text
AWMA_Q05_FULL_KERNEL_TRANSLATION_BEHAVIOR_V1_COMPLETE_WITH_SCOPE
```

Codex execution branch recommendation:

```text
hrl/awma-q05-full-translation-174new-v1
```

Create the execution branch/worktree from the coordination branch. Do not modify the frozen accepted characterization worktree.

## Track B — 109 / RTX4080

Node role:

```text
109 / RTX4080
Native producer / real-GPU workload owner
```

Execute:

```text
docs/vm_tlb/chatgpt_handoff/awma/
CODEX_NEXT_STAGE_109_QWEN25_S2_KERNEL_CENSUS_V1.md
```

Expected completion marker:

```text
AWMA_QWEN25_S2_KERNEL_CENSUS_V1_COMPLETE_WITH_SCOPE
```

Codex execution branch recommendation:

```text
hrl/awma-qwen25-s2-census-109-v1
```

Create the execution branch/worktree from the coordination branch. Do not modify the frozen simulator-native producer worktree.

## Shared frozen workload

```text
model      = Qwen/Qwen2.5-0.5B-Instruct
revision   = 7ae557604adf67be50417f59c2c2f167def9a775
batch      = 1
input      = TEXT
prefill    = 2048 tokens
decode     = 32 tokens
dtype      = FP16
backend    = SDPA
scenario   = S2_TEXT  # internal AWMA label only
```

Q05 target:

```text
Q05_PREFILL_ATTN_FLASH
function occurrence = 0
pytorch_flash::flash_fwd_kernel<...>
```

## Shared execution policy

Routine engineering issues are `solve-and-continue`:

- paths;
- parsers;
- scripts;
- build plumbing;
- log formats;
- Python dependencies;
- Git transport;
- large-file indexing;
- NSYS export/parsing;
- demangling;
- diagnostic telemetry plumbing that is proven timing-neutral.

Stop for scientific review only if execution would require changing one of:

- frozen workload identity;
- Q05 target identity;
- accepted SIM_INPUT identity;
- translation/TLB/PTW timing or functional semantics;
- accepted scientific counter semantics;
- evidence classification/provenance contract;
- a stated stop boundary in the node-specific spec.

## Explicitly forbidden scope

Neither track may automatically enter:

- L2-TLB latency sweep;
- PTW fixed-latency experiment;
- walker-count sweep;
- TLB-capacity sweep;
- translation-MSHR-capacity sweep;
- page-size sweep;
- Segment experiments;
- early-outstanding-translation mechanism;
- new cache mechanism;
- broad new simulator-native capture campaign.

Track B additionally must not run NCU/NVBit/full SASS tracing unless the node-specific specification is later revised by ChatGPT.

## Deliverable ownership

`chatgpt_handoff/` is ChatGPT-owned. Codex must not rewrite the task definition.

Codex owns:

```text
docs/vm_tlb/codex_handoff/awma/<stage-specific-report>.md
docs/vm_tlb/review_packs/<stage-specific-pack>/
```

Because the two tracks run in parallel branches, each must produce a stage-specific report rather than assuming a shared `LATEST_REPORT.md` can be edited without conflict.

Large raw data remains on node164 and is referenced through manifests/hashes, not committed directly to Git.

## Global STOP boundary

When a track reaches its completion marker:

```text
report
review pack
hashes
commit
push
remote verification
clean worktree
STOP
```

Do not continue to the next experiment.

After both tracks finish, ChatGPT must review both reports together and issue the next scientific stage.
