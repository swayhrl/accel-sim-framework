# Round18 | Engram serving source screen

Date: 2026-09-30

State: R18_ENGRAM_SERVING_PREP_CANDIDATE

Round17 stays closed after the FlowANN review. This pass screened a different workload family: the Engram conditional-memory component used by current DeepSeek serving stacks.

## Primary sources

The official Engram project describes deterministic n-gram lookup into large static tables and explicitly discusses moving those tables out of accelerator memory. Its standalone demo is documented as a demonstration that mocks surrounding model components, so it is not treated as workload authority.

Pinned source revisions used in this pass:
- deepseek-ai/Engram at fb7f84a21f91223715394a33a1dc24bbfb7f788e
- vllm-project/vllm at f28a5081629377c36cd219a35070555b72279109
- sgl-project/sglang at bd66ce343e4f6e2f2b75d7e820fe4d0718a8d824

Current vLLM source already supports host-resident Engram tables and asynchronous preparation of required rows. It also exposes an optional large-page backing control.

Current SGLang source independently supports host-resident Engram tables and a specialized gather path. SGLang issue 38856 further proposes batched row-only overlap and an optional hot-row cache.

Consequently, host placement, overlap, large pages, and hot-row caching are existing software capabilities or explicit upstream proposals. They are baselines, not AWMA novelty.

HugeCTR/HPS is a direct cache precedent from embedding systems. BOOST, arXiv:2609.13592, is a recent direct precedent for heterogeneous host/accelerator placement in LLM serving, though its workload and platform differ from sparse Engram lookup.

## Remaining scientific question

The only surviving question is whether a real Engram serving lookup on the available discrete platform retains a material lookup-path cost after mature overlap and page controls, once transfer cost, projection compute, and software runtime cost are separated.

This is a problem-qualification question. No specific cause is assumed.

## Input and platform boundary

Primary evidence still requires the official model configuration and tokenizer, the original Engram table representation, and natural text-derived lookup requests. The official mocked demo and reduced substitute tables are not equivalent scientific inputs.

The serving implementation describes tables large enough that a full layer is a substantial host-memory object. Node109 host-memory and storage feasibility have not yet been qualified, so this candidate remains preparation-only.

## Decision

Current status: R18_ENGRAM_SERVING_PREP_CANDIDATE.

Next preparation tasks are to bind the official model metadata to its Engram checkpoint shards without bulk download, qualify node109 capacity using CPU-only inventory when available, and finish the current-software nearest-neighbor audit.

No execution experiment or architecture mechanism was started in this pass.
