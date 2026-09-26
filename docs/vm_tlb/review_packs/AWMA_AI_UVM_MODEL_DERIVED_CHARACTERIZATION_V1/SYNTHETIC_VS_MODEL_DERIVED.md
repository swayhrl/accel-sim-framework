# Synthetic versus model-derived boundary

The accepted feasibility pilot used invented dense, growing-prefix, and rotating-expert laws at four artificial VRAM ratios. This continuation replaces sizes and ordering with local model authorities, but remains a replay rather than framework execution.

- D1 uses every Qwen3-8B tensor byte size and the frozen safetensors inventory order (399 tensors, 16,381,470,720 bytes). It does not execute Qwen operators.
- D2 uses the exact Llama-3.2-1B KV dimensions and exact byte accounting at fixed context 4096 while changing concurrency only. Access is a 256-token-block sequential prefix replay, so layout is exact and access timing is approximate.
- D3 uses the actual OLMoE decode route sequence, exact top-8 expert IDs, exact expert tensor regions, and exact non-expert pressure. It replays memory touches and does not execute expert GEMMs.
- The bounded PyTorch managed-tensor bridge did not compile because the extension compile command lacked a CUDA runtime header include path. Per preregistration it was not retried.

Therefore these results support model-derived UVM replay claims only. They are not measurements of end-to-end LLM serving, real framework allocation, GPU faults, TLB misses, PPN continuity, or migration page size.
