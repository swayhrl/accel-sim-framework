# C16 AI Workload 2239 Analysis / Storage Handoff V2B

## Purpose

This branch corrects the execution topology after V1 destination acceptance.

Docker `2239` is intentionally CPU-only. It is **not** the GPU execution destination and must not be modified to expose or emulate the RTX4080.

The actual GPU execution node is `109`.

## Long-term topology

- **109 — GPU execution plane**
  - Llama / later model execution
  - bounded NVBit capture
  - NCU profiling
  - GPU-side runtime and toolchain qualification
  - generation of raw GPU evidence

- **2239 — AI workload control / storage / analysis plane**
  - Git control plane
  - provenance / receipt / manifest management
  - CPU-side parsing and characterization
  - Cache/TLB/AI-workload analysis
  - organization of large artifacts on the external storage root
  - no requirement for local GPU, CUDA, NVBit, NCU, or PyTorch GPU execution

- **164 — long-term data plane**
  - accepted root from V1: `/root/share/mnt164/huangrulin/c16_ai_workload_2239`
  - model assets, frozen inputs, raw traces, profiler reports, manifests, derived datasets, analysis products

- **old Docker 2233 — architecture work + migration source**
  - continues decouple-L1, L2, and other GPU-memory architecture work
  - is not retired
  - remains a source for explicitly approved historical artifact recovery until migration closeout

## Authority boundaries

Historical RTX4080 R5 remains:

```text
branch: hrl/c16-4080-u5-u9-r5-clean
commit: b75f26674a09705659e770ab2134351414aa3c93
status: READY_FOR_MULTIMODEL_REVIEW
```

Historical RTX3090 closeout remains:

```text
branch: hrl/vm-c16-g-3090-campaign-closeout-v0
commit: 649af1b9d65a774d4aa8c32a15f9b6f4da0dd4d9
```

V1 destination acceptance remains immutable:

```text
branch: hrl/c16-ai-workload-2239-destination-acceptance-v1
commit: 43212af0de0eef1cd72d905e11bfdeb2fe0e6d37
```

V1 observations are not rewritten. `NEW_DESTINATION_RUNTIME_NON_EQUIVALENT_TO_R5` remains historically correct, but lack of GPU/CUDA in 2239 is now expected and is not a blocker for the corrected 2239 role.

## Current blocker

The remaining role-independent blocker is frozen-input identity. V2A is currently recovering the historical Llama S0/B1/T128/Decode4/TEXT bundle on:

```text
hrl/c16-ai-workload-frozen-input-recovery-v2a
```

Do not regenerate token IDs. The required historical four-hash contract remains authoritative.

## Next execution ordering

1. Let V2A finish and push its final commit.
2. Review V2A result.
3. Continue the 2239 analysis/storage phase from a commit that includes the accepted V2A result.
4. Only then create the 109 GPU execution/preflight branch from that accepted state.

This avoids manually merging frozen-input identity into the GPU execution lane.

## 2239 V2B allowed scope after V2A acceptance

CPU/storage only:

- establish the final external storage namespace;
- publish an immutable storage-layout manifest;
- copy-not-move exact admitted model assets into the long-term 164 root with source/destination size+SHA closure;
- admit the recovered frozen-input bundle into the 164 root with exact bytes and hashes;
- create placeholders/namespaces for future 109-produced raw NVBit and NCU artifacts;
- reconcile known historical R5/N1/U8 artifacts if located;
- prepare CPU-only parsers / workload characterization outputs;
- keep RTX3090 historical comparison data in a separate namespace and import only an explicitly approved minimum subset.

## Forbidden on 2239

- GPU passthrough work;
- CUDA runtime bootstrap solely for GPU execution;
- PyTorch CUDA model execution;
- NVBit capture;
- NCU profiling;
- pretending a 2239 CPU-only environment is equivalent to R5;
- copying the entire RTX3090 recovery root;
- authority merge between 3090 and 4080;
- regeneration of frozen input with a tokenizer.

## 109 future handoff

The 109 GPU execution branch must be created **after V2A review** so it can inherit the frozen-input closure. It must independently record GPU model/UUID, driver, CUDA/runtime, PyTorch/transformers, NVBit, NCU, model path, frozen input, and raw-output storage/copyback contract. No historical 4080 static map or runtime identity may be assumed equivalent without requalification on 109.