# Strong-kernel nearest-neighbor audit

## Decision table

| Neighbor | Primary-source capability | Relevance to this exact Ada/AWQ case | Guard decision |
|---|---|---|---|
| Marlin | FP16xINT4 tensor-core kernel designed for near-ideal weight-only speedups through medium batch sizes, with striped partitioning and reduced global reduction | Direct W4A16 small-batch projection neighbor on Ampere/Ada, but its original symmetric/GPTQ representation is not automatically bit-equivalent to the accepted zero-point AWQ checkpoint | **STOP** a new generic W4 flat-GEMM or reduction kernel story until an exact-format strong baseline is shown missing |
| QUICK | Offline quantization-aware interleaving removes the dequantized-weight shared-memory write-back/bank-conflict path and directly compares against AutoAWQ | Directly covers the current kernel's dequant/layout family; reported benefit emphasizes larger batches, so it does not prove this exact M1 result | **STOP** offline interleaving/bank-conflict as a new idea; not evidence that gate/up scheduling is solved |
| FLUTE | LUT-quantized low-bit GEMM combines offline packing, lookup/vectorization, Stream-K and shape/GPU specialization | Strong utilization/dataflow neighbor, including explicit M=1 tuning, but the LUT/NF format is not the affine zero-point AWQ format | **STOP** generic Stream-K/load-balance novelty; not a drop-in exact-checkpoint baseline |
| FlashDecoding++ | Separately attacks decode attention synchronization, flat-GEMM zero-padding, double buffering and resource-adaptive dataflow | Direct method neighbor for attention and flat GEMM, not an exact AutoAWQ kernel replacement | **STOP** attention split/combine or generic adaptive flat-GEMM as the remaining C16 problem |
| vLLM AutoAWQ/Marlin | Current vLLM source converts compatible AWQ checkpoints to its Marlin representation and selects Marlin on supported CUDA hardware; tile-misaligned layers are padded during weight preparation | Most direct production-software guard for Qwen AWQ on Ada; exact Qwen checkpoint compatibility/correctness was not executed in this CPU-only screen | **STOP** kernel-selection work as a new 109 task; first use the existing production backend if later comparison is authorized |
| Hopper utilization paper | Eight-view method separates coverage, occupancy denominators, stalls, useful fragment fill, waves, service and kernel choice | Method transfers; H100/GMMA m64 values do not. This screen uses the real Ada m16 source and RTX 4080 geometry | **METHOD_ONLY**, no numeric transfer |

## Primary sources read

- AutoAWQ accepted historical source: `casper-hansen/AutoAWQ_kernels@c7b0e88c327694c715b0a758d9ce8fd414a1fa21`, `awq_ext/quantization/gemm_cuda_gen.cu` (accepted blob `98f49efac8626388039912e6aabc8a84d9f8303b`). The kernel maps `ceil(M/16) * ceil(N/128) * split_k`, launches 64 threads, zero-fills invalid M rows, executes `mma.sync ... m16...`, and predicates output stores.
- [Marlin paper](https://arxiv.org/abs/2408.11743) and [author implementation](https://github.com/IST-DASLab/marlin).
- [QUICK paper](https://arxiv.org/abs/2402.10076) and [author implementation](https://github.com/SqueezeBits/QUICK).
- [FLUTE paper](https://arxiv.org/abs/2407.10960) and [author implementation](https://github.com/HanGuo97/flute).
- [FlashDecoding++ paper](https://arxiv.org/abs/2311.01282).
- [vLLM AutoAWQ source](https://github.com/vllm-project/vllm/blob/main/vllm/model_executor/layers/quantization/auto_awq.py).
- [Dissecting GPU Utilization for LLM Inference on Nvidia Hopper](https://arxiv.org/abs/2609.12923).
- [NVIDIA Ada Tuning Guide](https://docs.nvidia.com/cuda/ada-tuning-guide/) for the 48-warps/SM architectural ceiling. The accepted platform authority independently fixes RTX 4080 at 76 SMs.

No paper throughput, H100 occupancy, GMMA m64 fill, or different quantization format is imported as an Ada result.
