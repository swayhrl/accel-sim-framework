# FFN strong software baseline audit

## Current accepted runtime

All 560 semantic activities in the formal trace execute on CUDA stream `7`. Every one of the 112 layer×decode windows follows gate → SiLU → up → multiply → down, and gate/up overlap is zero in all 112 windows. The accepted source performs these calls synchronously in that order; gate/up are logically independent siblings sharing `hidden`, but the current strong `WQLinear_GEMM` runtime serializes them.

## Minimal strong software baseline

A two-stream baseline is source-feasible without changing W4 kernels, quantization, tensor layout, or the numerical DAG. Both streams first wait for the original stream's hidden-ready event. One stream executes gate then SiLU; the other executes up. The original stream waits for both branch events before the unchanged multiply and down projection. Cross-stream tensor lifetimes must be recorded. Every run must retain the four generated tokens and all 336 projection input/output hashes and shapes.

This is only a feasibility result. Two W4 GEMMs may compete for SM, register, L2, and DRAM resources, so real overlap or speedup is not assumed. The accepted gap-preserving no-contention ceiling is `7.732849` ms, not a prediction.

## Related-work boundary

LR10 (blob `d479680123abab8b4e3e462a55f9aa0312ef1258`, SHA256 `aa948d7a58f1e743e52021128850e1885d2eb53afa10cdca5bdd7193ff7133fc`) separates generic fusion, sibling-operator concurrency, cross-tile handoff, and layout-preserving pipelines. Kitsune provides queue-based spatial dataflow, VTC virtualizes mapped tensors but can hurt the compute kernel, ComFuse exposes fill/drain and stage-balance limits, and NVIDIA's Rubin description already discusses tile-ready producer/consumer triggers. These neighbors prevent claiming either “fusion” or “tile-ready” as novel by name alone; they do not eliminate the value of measuring the exact unchanged-kernel two-stream baseline first.
