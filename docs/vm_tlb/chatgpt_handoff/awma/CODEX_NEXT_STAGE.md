# CODEX_NEXT_STAGE

Status: **ACTIVE — TRACK A ONLY; TRACK B COMPLETE/ACCEPTED**

Stage:

```text
AWMA_Q05_TRANSLATION_TIMELINE_CLOSURE_AND_KERNEL_TARGET_SELECTION_V1
```

This is a two-track parallel pre-mechanism stage. Track B on node109 has completed and is accepted within scope. Track A on 174-new remains active. Do not restart Track B unless ChatGPT issues a new stage.

## Objective

Before any new TLB/PTW mechanism experiment:

1. close the missing cycle/key translation timeline for the complete Q05 kernel with timing-neutral diagnostic telemetry;
2. use the accepted full S2 kernel-call inventory to select the next representative kernel candidates, without capturing them yet.

Objective 2 is now complete. Objective 1 remains open.

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

Then execute only an ACTIVE node-specific specification.

## Accepted previous results

### 174-new previous stage

```text
branch = hrl/awma-q05-full-translation-174new-v1
HEAD   = 6415d3f1
status = AWMA_Q05_FULL_KERNEL_TRANSLATION_BEHAVIOR_V1_COMPLETE_WITH_SCOPE
```

### 109 census

```text
branch = hrl/awma-qwen25-s2-census-109-v1
HEAD   = 678d7b491d4788369ca0c22717453b20846ab195
status = AWMA_QWEN25_S2_KERNEL_CENSUS_V1_COMPLETE_WITH_SCOPE
```

## Track A — 174-new — ACTIVE

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

## Track B — 109 — COMPLETE / ACCEPTED

Accepted result:

```text
branch = hrl/awma-kernel-target-selection-109-v1
HEAD   = e90fd76d3704df4a367bb04de09aee42d0cab803
status = AWMA_KERNEL_TARGET_SELECTION_V1_COMPLETE_WITH_SCOPE
```

ChatGPT review disposition:

```text
PASS_WITHIN_SCOPE
```

No GPU profiling or capture ran in this stage.

Accepted `CANDIDATE_ONLY_NOT_CAPTURED` targets:

```text
PREFILL_GEMM_PRIMARY_1
  exact family: CUBLAS_GEMM / CUTLASS Kernel2
  grid/block: 128,3,1 / 256,1,1
  reference launch: 285
  phase-function-shape occurrence: 12
  recurrence count: 20
  share: 57.31% of Prefill GEMM-family GPU time
         38.10% of total Prefill GPU time

DECODE_GEMV_PRIMARY_1
  exact family: CUBLAS_GEMV / internal::gemvx int6
  grid/block: 1216,1,1 / 16,4,1
  reference launch: 1244
  phase-function-shape occurrence: 10
  recurrence count: 1,536 across 32 decode steps
  share: 40.64% of Decode GEMV-family GPU time
         20.22% of total Decode GPU time

DECODE_FLASH_PRIMARY_1
  exact implementation: flash_fwd_splitkv_kernel
  grid/block: 1,9,14 / 128,1,1
  reference launch: 1748
  recurrence count: 768 across 32 decode steps
  share: 82.10% of Decode Flash GPU time
         8.10% of total Decode GPU time

DECODE_FLASH_PRIMARY_2
  exact implementation: flash_fwd_splitkv_combine_kernel
  grid/block: 2,1,1 / 128,1,1
  reference launch: 1018
  recurrence count: 768 across 32 decode steps
  share: 17.90% of Decode Flash GPU time
         1.77% of total Decode GPU time
```

Important identity rule for any future capture:

> `reference_launch_index` is only a navigation aid from the accepted census. Scientific target identity must close on frozen workload + phase + exact kernel function + grid/block + deterministic occurrence. Do not treat a dynamic launch number by itself as a stable identity across reruns.

Additional accepted boundary:

```text
NATIVE PREFILL_HEAVY_GEMM exact alignment = NATIVE_TARGET_MATCH_NOT_PROVEN
```

Duration or family similarity alone must not be used to claim the old Native heavy-GEMM target is identical to `PREFILL_GEMM_PRIMARY_1`.

Selection caveat for later broad Decode coverage:

The selected `DECODE_GEMV_PRIMARY_1` is the high-frequency primary GEMV subfamily. Another GEMV shape (`grid=18992,1,1 / block=8,8,1`) occurs only once per decode step (32 total) but contributes about 21.5% of Decode GEMV-family GPU time because each invocation is roughly 409 us. It remains a secondary candidate if later work aims to cover Decode runtime comprehensively rather than only the dominant recurring shape.

Track B is now frozen. Do not capture any candidate until ChatGPT reviews Track A and issues a new capture stage.

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

The remaining active Track A may not start:

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

Node109 must remain idle for this stage unless ChatGPT explicitly issues a new instruction.

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

For Track A:

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

After Track A completes, ChatGPT must review Track A together with the now-accepted Track B before any new capture or mechanism experiment starts.
