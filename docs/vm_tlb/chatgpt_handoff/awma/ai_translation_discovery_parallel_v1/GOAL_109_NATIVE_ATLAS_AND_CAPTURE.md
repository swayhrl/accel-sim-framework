# Goal 109 — AI Translation Native Atlas + Qualified Trace Batch V1

Stage:
`AWMA_AI_TRANSLATION_NATIVE_ATLAS_CAPTURE_109_V1`

Execution branch:
`hrl/awma-ai-translation-native-atlas-capture-109-v1`

Node:
109 / RTX4080

## 0. Purpose

Broaden the scientific question, not the mechanism.

Characterize and capture a minimal set of kernels from AI dimensions not already represented by the Qwen2.5 strong-baseline set.

This Goal is continuous:
asset audit -> Native scenario runs -> kernel selection -> targeted page-behavior capture -> simulator-native capture -> qualification -> durable handoff.

Do not stop between phases for ordinary engineering issues.

## 1. GPU lock

All real GPU execution must hold:
`/data/c16/locks/c16_gpu_campaign.lock`

Release at closure.

## 2. No downloads / bounded scenario pool

Use only already-present, runnable assets.

Predeclared dimensions and fallback order:

### DENSE_OTHER_FAMILY
Primary: Llama-3.2-1B
Fallback: an already-finalized dense model present locally (e.g. Gemma-3-12B) only if it fits and runs without new downloads or environment redesign.

### MOE_FAMILY
Primary: OLMoE-1B-7B-0125-Instruct
Fallback: already-present DeepSeek-V2-Lite or another already-present MoE asset.

### IMPLEMENTATION_CHANGE (optional, only if both sides already runnable)
Existing Qwen2.5 raw vs AWQ pair.

Do not add a fourth dimension.
Do not download or repair an unavailable model for this Goal.
If only two dimensions are runnable, proceed with two.

## 3. Scenario contract

For each selected model family, use one bounded deterministic inference scenario suitable for 16GB RTX4080.

Preferred target:
- batch 1
- prompt approximately 256-512 model tokens
- decode 8 tokens

If a model cannot fit this exactly, choose the nearest smaller prompt length BEFORE profiling and record it.
Do not compare raw runtime across model families as if inputs were identical.

Use the same source text where tokenizers permit; record:
- exact text SHA
- tokenizer/model revision
- actual prompt token count
- generated token count
- dtype/quantization
- attention implementation
- runtime/library revisions.

No hidden warm-history claim.

## 4. Native census first

For every runnable scenario:
- 1 warmup
- 1 authoritative Native census/profiling run
- obtain per-kernel/function:
  - launch count
  - GPU time
  - grid/block
  - phase (prefill/decode where determinable)
  - implementation identity

Reuse existing census infrastructure where possible.

Do not run NCU over the whole model.

## 5. Target selection BEFORE address-behavior results

Select at most TWO kernels per scenario, max SIX total.

Selection criteria in order:
1. Native GPU time relevance within scenario;
2. structural/family diversity;
3. translation-relevant execution diversity.

Do not select based on simulator result or page metric result.

Desired family coverage across the total batch:
- at least one attention-like kernel if present,
- at least one GEMM/GEMV-like kernel,
- at least one MoE dispatch/expert/reduction-like kernel for MoE if present.

If a category is absent, do not fabricate it.

Freeze selection to:
`KERNEL_SELECTION_PREREG.tsv`
before targeted address collection/capture.

## 6. Targeted Native page-behavior characterization

For the selected kernels only, collect source-supported per-access virtual-address behavior.

Prefer existing trusted tracer infrastructure.
If existing trace already contains enough address provenance, derive offline.
Only add a read-only targeted NVBit observer if necessary.

Required metrics where source-supported:
- memory references / active-lane refs
- requested bytes
- read/write
- unique 4KB virtual pages
- unique 64KB virtual regions
- unique 2MB virtual regions
- dynamic memory-instruction histogram of unique 4KB pages
- max unique 4KB pages per dynamic memory instruction
- temporal unique-page count over bounded event windows (e.g. 1K and 10K memory refs)
- new-page arrival burstiness / interarrival quantiles
- page revisit-distance quantiles
- same-load-PC concentration within 2MB VIRTUAL chunks

Explicit boundary:
- these are virtual-address observations;
- do NOT infer physical contiguity, PPN stability, Avatar speculation accuracy, or TLB hit rate from them.

Optional minimal NCU:
only for selected kernels and only source-supported metrics needed to contextualize data-cache behavior:
- L1/L2 hit/sector traffic
- DRAM traffic
No broad metric sweep.
No TLB metric claims unless the exact counter meaning is verified.

## 7. Simulator-native capture

Capture exactly the preregistered selected kernels using accepted Route-B producer authority.

Authorities:
- producer source: `5143b4e10aaf2fc47bb60492155d2464b0b726fd`
- historical scaffold: `c17df93f9c44aa35d2942ae696bc2bd2a30b3643`
- bridge semantics from `c8549227a7c581a6f32c1fb63087ea117134fddc`

For each target:
scientific identity -> fresh Route-B census -> ordinal/navigation -> formal capture.

No NSYS global index as cross-tool identity.

Qualification:
- drop=0
- overflow=0
- terminal PASS
- grammar PASS
- exact function/grid/block/phase identity where available
- trace integrity/hash
- runner/index provenance

Do not capture extra alternatives "just in case" after seeing behavior.

## 8. Durable storage

Store under a new node164 authority directory, e.g.
`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/ai_translation_native_atlas_capture_20260926/`

Include:
- scenario receipts
- Native census
- page-behavior metrics
- selection preregistration
- raw/captured traces
- traceg
- bridge manifests
- grammar receipts
- SHA256SUMS

## 9. Decision / handoff

This Goal does NOT decide a mechanism.

Produce:
`NATIVE_ATLAS_CONSUMER_HANDOFF.json`

For each target include:
- workload dimension
- model/revision/scenario
- Native role/time share
- family/identity/grid/block
- virtual-page behavior summary
- durable trace path/SHA
- qualification status

Also produce a scenario-level summary answering only:
- which workload dimensions materially change virtual-page divergence/burstiness/working-set behavior?
- which do not?
- what cannot be inferred about physical mapping/TLB behavior?

Status:
`READY_FOR_AI_TRANSLATION_RESIDUAL_174NEW`

If no new dimension is runnable or no selected target can be qualified:
report exact blocker and STOP; do not download anything.

## 10. Deliverables

- README.md
- ASSET_AND_RUNTIME_AUDIT.tsv
- SCENARIO_CONTRACT.tsv
- NATIVE_CENSUS.tsv
- KERNEL_SELECTION_PREREG.tsv
- VIRTUAL_PAGE_BEHAVIOR.tsv
- TEMPORAL_PAGE_BEHAVIOR.tsv
- OPTIONAL_NCU_CONTEXT.tsv
- CAPTURE_BRIDGE.tsv
- CAPTURE_QUALIFICATION.tsv
- NATIVE_ATLAS_CONSUMER_HANDOFF.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Commit/push/fetch-back/remote tree+hash/clean and STOP.
