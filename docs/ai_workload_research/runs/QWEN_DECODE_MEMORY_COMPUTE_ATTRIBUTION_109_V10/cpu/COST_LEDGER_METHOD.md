# CPU cost ledger method

Inputs are existing V9 Nsight Systems SQLite, cached compiled Python and JSON receipts. SQLite was opened read-only. No GPU/CUDA/NVML call, torch/vllm import, new profiler run or V9 write was made.

B1 is A00_N32; B2 is the A00+A01 batch B2_N32. Output length32 contains31 actual incremental decode steps. N1 output-length runs contain prefill only. Kernel attribution follows correlationId to CPU CUDA API, then same-thread request and FORWARD/SAMPLE NVTX containment; it never assumes asynchronous GPU activity falls inside the host NVTX window.

COST_LEDGER.tsv has one row per batch decode step. GPU step span means the first-to-last assigned kernel hull. Dense, non-dense and total kernel busy time use interval unions; summed durations and overlap are separate fields. CPU marker spans, copies, bandwidth models and NCU measurements must not be added to kernel times. Kernel-hull gaps are not proven CPU cost.

COST_LEDGER_KERNELS.tsv preserves every decode kernel's name, grid/block, resources, SQLite row identity, graph node, phase and timing. Layer/op and M/N/K columns are compiled-contract/order inferences, not raw launch arguments. The JSON catalog groups identical names and launch resources and reports per-step group union/sums.

The first true decode dense node is strongly matched to layer0 packedQKV: cached submod_0 binds the exact named weight [2560,2048], compiled addmm uses input [s72,2048] and output [s72,2560], runtime manager descriptors have s72-compatible token counts1/2, and observed kernel order is embedding+RMSNorm -> GEMV/GEMM -> RoPE/cache/attention. SQLite does not preserve GEMM parameter structs; grid alone cannot prove dimensions.

Only a separate seven-pass B1 single-node NCU result measured DRAM bytes. Whole-step/application DRAM and B2 counters remain unmeasured. Logical dense BF16 weight bytes per batch step are a conditional traffic model with within-step reuse, not measured traffic. The existing trace warns of possible missing events and CUDA13/12.8 collection fallback; timeline timing is profiled and is not formal native timing.
