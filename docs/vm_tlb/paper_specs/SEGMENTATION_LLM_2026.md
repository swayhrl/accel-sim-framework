# Paper specification — Towards Segmentation-Based Address Translation for LLM Inference

Status: extracted reproduction notes from the user-provided IEEE Computer Architecture Letters PDF.

Citation:
Youngjoon Cheon, Yunho Oh, and Jeongseob Ahn, “Towards Segmentation-Based Address Translation for LLM Inference,” IEEE Computer Architecture Letters, Vol. 25, No. 1, Jan.–Jun. 2026. DOI: `10.1109/LCA.2026.3693796`.

The copyrighted PDF itself is intentionally not committed to this public repository.

## Evidence labels

Facts explicitly stated in the paper are `PAPER_SPEC`.
Details not explicitly available in the paper are marked `UNKNOWN` and must not be upgraded to `PAPER_EXACT` without artifact/source evidence.

## Problem / motivation

`PAPER_SPEC`:

- LLM inference repeatedly reuses model weight pages across token generations.
- The paper reports that 99% of accessed weight pages are revisited across iterations.
- Growing KV-cache footprint competes for shared TLB capacity and can evict weight translations.
- These misses trigger page-table walks and can stall many active GPU threads/warps.
- The proposed mechanism isolates model weights from conventional page-based translation.

## Weight-memory properties used by the proposal

`PAPER_SPEC`:

- model weights are read-only during inference;
- weights remain resident for the serving-instance lifetime;
- weights are separated from KV-cache and activation regions;
- the serving framework is modified so all model weights are placed in one large virtually contiguous buffer instead of many layer-granularity allocations;
- the operating assumption is that this monolithic allocation is backed by a sufficiently/mostly physically contiguous region when weights are loaded once at startup on a largely free GPU.

The scheme requires both virtual and physical contiguity for a segment to fully bypass paging.

## Segment translation mechanism

`PAPER_SPEC`:

- small segment table stores descriptors for contiguous memory;
- each descriptor contains segment `base`, `limit`, and `offset`;
- on segment hit, physical address is computed using the descriptor offset/base relationship;
- conventional page-table walk is bypassed;
- L1 TLB lookup may occur in parallel, but its result is masked/discarded on segment hit so segment lookup does not add serial timing to the critical path;
- on segment miss, e.g. activation/KV accesses, the request follows conventional paging;
- with 49-bit virtual addresses and 64KB pages, the paper states the lower 16 bits are page offset, leaving 33 bits per descriptor field;
- typical single-model serving requires one weight segment;
- multiple co-located models can use additional descriptors; the paper discusses a typical small number of models such as 2–8.

The paper also notes that a preallocated monolithic KV pool could potentially be segmented if physical contiguity is provided, but this is future direction rather than the evaluated mechanism.

## Experimental workload

`PAPER_SPEC`:

- model: Llama-3.2 1B;
- the model is scaled down using tensor parallelism by a factor of 4;
- one partition is evaluated on a downscaled NVIDIA RTX 3070 configuration;
- batch size: 8;
- base input sequence length: 64;
- generated output tokens: 3;
- evaluation focuses on prefill and the first decoding phase because weight access is repetitive across decode iterations;
- long-context pressure is emulated using synthetic KV translation-request injection rather than full long-sequence instruction simulation;
- KV footprint is scaled up to an equivalent sequence length of 12K in the reported long-context study.

## Simulated GPU configuration — Table I

`PAPER_SPEC`:

- Number of SMs: **35**
- Clock frequency: **1500 MHz**
- L1 cache: **128 KB per SM**
- L2 cache: **3 MB, 16-way**
- Memory: **GDDR6, 12 channels**
- L1 TLB: **32 entries, fully associative**
- L2 TLB: **768 entries, 16-way**
- Page-table walkers: **16**
- Total simulated instructions: **19.1B**

The paper states that it implements segmentation-based translation and L2-TLB sub-entry support in Accel-Sim and leverages the detailed TLB modeling component of its reference [4].

## Page size / TLB reach scaling

`PAPER_SPEC`:

- baseline page size in the evaluation is **64KB**;
- the authors state that directly simulating the reach limitation of 2MB pages over hundreds of GB would exceed realistic Accel-Sim timescales;
- they proportionally scale down TLB reach relative to the working set to emulate the capacity pressure of large-page/sub-entry architectures in expanded-memory systems;
- L2 TLB sub-entry support is part of the paging baseline and must not be omitted when comparing against Segmentation.

## Reported results useful as reproduction references

`PAPER_SPEC`, not automatic pass/fail targets:

- short-context weight L2 TLB hit rate reported at sequence length 64: **95.9%**;
- at equivalent long-context pressure, weight translations are increasingly evicted;
- the paper reports up to **62.9% IPC loss** from translation at sequence length 12K in the motivation experiment;
- Segmentation IPC: **2.51x** normalized to the 64KB paging baseline;
- ideal no-TLB-miss IPC shown in Fig. 4: **2.69x** baseline;
- baseline L2-TLB miss rate in Fig. 5: **91.5%**;
- after weight traffic is intercepted by Segmentation, the remaining conventional TLB working set reports **17.0% miss rate**.

These values are reference points only. First-pass reproduction acceptance should prioritize the causal chain and configuration fidelity over exact numeric equality.

## Reproduction causal chain

The later reproduction should be able to establish:

`KV translation footprint grows -> weight translation eviction grows -> weight PTWs / translation stall grow -> IPC falls`

and then:

`weight Segment hit -> weight TLB/PTW traffic bypassed -> conventional TLB capacity freed for KV/activation -> translation stall falls -> IPC improves`.

## Important UNKNOWN details requiring M4A audit

The four-page letter does not fully specify all implementation details required for a cycle-accurate reproduction. Treat the following as `UNKNOWN` until artifact/reference evidence is found:

- exact L1/L2 TLB lookup latency and port/throughput model;
- exact sub-entry entry format, coverage factor, fill/coalescing trigger, replacement granularity, and lookup timing;
- exact page-table organization used in this paper's Accel-Sim implementation beyond the statement that it leverages the detailed TLB modeling component of reference [4];
- exact page-walk-cache organization, if any;
- exact synthetic KV translation-request injection rate, temporal distribution, VPN distribution, reuse distribution, lookup-port interaction, MSHR/PTW interaction, and whether each synthetic miss creates full PTE traffic;
- exact method used to obtain/emulate the 1/4 tensor-parallel partition trace;
- exact model dtype/quantization used in the simulated workload;
- exact source patch for the single-buffer contiguous-weight allocator;
- public exact trace/artifact availability.

M4A must search for artifacts/source evidence. If these remain unavailable, later work must explicitly request approval before using `DOCUMENTED_APPROX` implementations.
