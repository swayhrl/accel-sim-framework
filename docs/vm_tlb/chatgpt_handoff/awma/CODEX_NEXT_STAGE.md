# CODEX_NEXT_STAGE

Status: **ACTIVE**

Stage:

```text
AWMA_Q05_TRANSLATION_TIMELINE_CLOSURE_AND_KERNEL_TARGET_SELECTION_V1
```

This is a two-track parallel pre-mechanism stage.

## Objective

Before any new TLB/PTW mechanism experiment:

1. close the missing cycle/key translation timeline for the complete Q05 kernel with timing-neutral diagnostic telemetry;
2. use the accepted full S2 kernel-call inventory to select the next representative kernel candidates, without capturing them yet.

## Coordination branch

```text
hrl/awma-q05-translation-timeline-handoff-v2
```

Codex must fetch this coordination branch and read in order:

```text
docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/awma/DISCUSSION_REFERENCE.md
docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE.md
```

Then execute exactly one node-specific specification.

## Accepted previous results

### 174-new

```text
branch = hrl/awma-q05-full-translation-174new-v1
HEAD   = 6415d3f1
status = AWMA_Q05_FULL_KERNEL_TRANSLATION_BEHAVIOR_V1_COMPLETE_WITH_SCOPE
```

### 109

```text
branch = hrl/awma-qwen25-s2-census-109-v1
HEAD   = 678d7b491d4788369ca0c22717453b20846ab195
status = AWMA_QWEN25_S2_KERNEL_CENSUS_V1_COMPLETE_WITH_SCOPE
```

## Track A — 174-new

Node:

```text
174-new / port 2239
```

Execute:

```text
docs/vm_tlb/chatgpt_handoff/awma/
CODEX_NEXT_STAGE_174NEW_Q05_TRANSLATION_TIMELINE_CLOSURE_V1.md
```

Recommended execution branch:

```text
hrl/awma-q05-translation-timeline-174new-v1
```

Create it from the previous 174-new result commit `6415d3f1`, after first reading the ChatGPT coordination branch.

Expected completion marker:

```text
AWMA_Q05_TRANSLATION_TIMELINE_CLOSURE_V1_COMPLETE_WITH_SCOPE
```

## Track B — 109

Node:

```text
109 / RTX4080
```

This track is **offline only**. Do not consume GPU for profiling/capture.

Execute:

```text
docs/vm_tlb/chatgpt_handoff/awma/
CODEX_NEXT_STAGE_109_KERNEL_TARGET_SELECTION_V1.md
```

Recommended execution branch:

```text
hrl/awma-kernel-target-selection-109-v1
```

Create it from the previous 109 census commit `678d7b491d4788369ca0c22717453b20846ab195`, after first reading the ChatGPT coordination branch.

Expected completion marker:

```text
AWMA_KERNEL_TARGET_SELECTION_V1_COMPLETE_WITH_SCOPE
```

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
scenario   = S2_TEXT
```

Current accepted Q05 target:

```text
Q05_PREFILL_ATTN_FLASH
function occurrence = 0
pytorch_flash::flash_fwd_kernel<...>
```

## Shared execution policy

Routine engineering problems are solve-and-continue:

- build plumbing;
- parser/log formatting;
- diagnostic output volume;
- Python analysis;
- source navigation;
- Git/worktree handling;
- node164 indexing;
- demangling/grouping;
- deterministic occurrence mapping.

Stop for scientific review only if a task would require changing:

- frozen workload identity;
- Q05 target identity;
- accepted SIM_INPUT identity;
- translation/TLB/PTW functional or timing semantics;
- accepted counter semantics;
- evidence provenance contract;
- an explicit node-specific STOP boundary.

## Explicitly forbidden scope

Neither track may start:

- L2-TLB lookup-latency sweep;
- PTW fixed-latency experiment;
- walker-count sweep;
- TLB-capacity sweep;
- translation-MSHR-capacity sweep;
- page-size sweep;
- Segment;
- early outstanding-translation/coalescing mechanism;
- new cache mechanism;
- new simulator-native selected-kernel capture.

Track B additionally must not run NSYS/NCU/NVBit/C16WARP1 or any other GPU profiling/capture in this stage.

## Deliverables

Codex owns stage-specific reports under:

```text
docs/vm_tlb/codex_handoff/awma/
```

and evidence under:

```text
docs/vm_tlb/review_packs/
```

Large raw telemetry remains on node164 with path/hash manifests.

`chatgpt_handoff/` remains ChatGPT-owned.

## Global STOP boundary

For each track:

```text
finish required analysis
→ review pack
→ report
→ hashes
→ commit
→ push
→ remote verify
→ clean worktree
→ STOP
```

After both tracks complete, ChatGPT must review them together before any new capture or mechanism experiment starts.
