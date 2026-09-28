# Replica patch semantic isolation

The patch is based on AutoAWQ kernels `c7b0e88c327694c715b0a758d9ce8fd414a1fa21`, generator blob `98f49efac8626388039912e6aabc8a84d9f8303b`. It creates a new independent extension and does not replace either accepted binary.

Inside `gemm_forward_4bit_cuda_m16n128k32`, the only data-path additions are a runtime `replica_mask`, branch-free `replica_id=(blockIdx_y/j_factors1)&replica_mask`, three frozen per-replica strides, and those three offsets in the qweight, qzeros, and scales base pointers. SHARED uses mask 0; PER_MTILE uses mask 15. Both states execute the same compiled kernel and instruction path.

The input/A pointer formula and output/scratch/C pointer formula are byte-for-byte unchanged. K bound, Ktile interleave, loop count, synchronization, global load count, dequantization, shared-memory layout, MMA, writeback, tile, grid, and block formulas are unchanged. Static token-count checks for loops, barriers, dequant calls, MMA statements, and `k_bound` are equal before and after the patch.

Host-only changes adapt inputs to contiguous `[16,...]` replica tensors, reject any non-frozen M/K/N/mask/layout, pass `replica_mask`, and use the already accepted split1 direct-plane return while retaining split8 `sum(0)`. These host differences do not vary between SHARED and PER_MTILE within a split. `pybind_awq.cpp` is unchanged because it already binds the function pointer from `gemm_cuda.h`.

Therefore the causal state contrast changes only which bit-identical weight-side replica base is addressed. It does not isolate qweight from qzeros/scales, so all conclusions must say “weight-side”.
