# Novelty and claim boundary

## Classification

`NEAREST_NEIGHBOR_CROWDED` for the **generic capability/story** “multiple warps revisit a weight line, therefore add a cache mechanism.” The literature/source already exposes GEMV-oriented output mapping, packed/coalesced warp weight loads, CTA shared-memory operand staging, warp-K and split-K reductions, Stream-K/striped CTA assignment, offline weight reordering, and MoE expert tile selection. This classification does **not** assert that the exact DeepSeek kernel has no remaining inefficiency or that any alternative wins on its frozen semantic target; those facts are unmeasured here.

## Claim ladder

1. `SAME_LINE_DIFFERENT_SECTOR`: ordinary spatial partition is a sufficient explanation; **zero duplicate-sector evidence**. No cache-mechanism claim.
2. `SAME_SECTOR_DUPLICATE`: potential extra requests, but useful bytes may be disjoint, same sector may already be in L1/L2, and independent warp requests need not become repeated DRAM fills. An address-event count is **not** a cache miss counter.
3. `SAME_BYTE_DUPLICATE`: strict operand overlap, but removing loads may introduce communication/synchronization or reduce parallelism. Need exact warp/CTA/timing and a semantics-matched software baseline.
4. `EXPOSED_SYSTEM_COST`: only measured lower-level traffic or scoreboard/critical-path cost after the above controls could create a residual *research problem*. No current literature-only inference reaches this step.

## Nearest strong capability before hardware

For a future separately authorized evaluation (not an instruction to run it), compare: (a) frozen current DeepSeek path; (b) a same-format output/K work partition that removes strict duplicate byte/sector requests without changing math; (c) cooperative CTA staging where consumers are co-resident; (d) grouped/persistent/split-K variants where reduction and scratch are charged; and (e) a precise cache-service bound. The same input, expert routing, quantization scales/zeros, output tolerance, launch scope and whole-target metric must be fixed. [MARLIN §3.4](https://arxiv.org/html/2408.11743v1), [CUTLASS design](https://github.com/NVIDIA/cutlass/blob/0b55a2f691d69981583568fd9eb69687b1f0de8a/media/docs/cpp/efficient_gemm.md), [AWQ GEMV source](https://raw.githubusercontent.com/mit-han-lab/llm-awq/d6e797a42b9ef7778de8ee2352116e0f48a78d61/awq/kernels/csrc/quantization/gemv_cuda.cu) and [vLLM MoE source](https://raw.githubusercontent.com/vllm-project/vllm/bcee730b1a9d25f0fd283a0ef6c19133ebeebf4f/vllm/model_executor/layers/fused_moe/experts/marlin_moe.py) bound the software space.

The residual architecture question, **if** all gates later pass, is not “can a cache hold the same line?” It is whether independent CTAs necessarily issue costly duplicate sector/byte service despite all legal software placement/staging and existing L1/L2 behavior, with enough exposed end-to-end time to outweigh metadata, capacity, admission and scheduling costs. This is a conditional novelty test, not a proposed mechanism.

## Negative controls / non-claims

- Do not treat an aligned 128 B line as four mandatory 32 B transactions per warp when only one sector is addressed; [CUDA coalescing](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html#coalesced-access-to-global-memory) operates at the needed sector granularity.
- Do not attribute a line revisit to weight without exact operand/PC and address namespace; inputs/scales/zeros can share a similar shape of repetition.
- Do not call CUTLASS's Hopper TMA warp specialization an SM89-ready implementation. Do not claim cuBLAS/GEMVX internal warp policy from an exported API name.
- Do not transplant MARLIN symmetric INT4, FLUTE LUT or QUICK prepacked formats into a DeepSeek quantized target without semantic qualification.
- Do not assume “fewer global loads” means speedup: shared staging, barriers, reduced occupancy, extra reduction and compiler scheduling can dominate. MARLIN itself reports an instance where reloading scales from shared memory is faster than avoiding that reload.
- Do not rename the already closed C16 broad replacement/residency/split branches as active based on this literature guard. LR12 terminal decision remains separate and unchanged.

No author artifact was run. No new GPU/NCU/NVBit/SASS/Accel-Sim/trace/mechanism work is authorized here.
