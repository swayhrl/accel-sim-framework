# Retry570 NVBit compatibility discriminator V2

Status: `NVBIT_RETRY570_MEMORY_TRACE_PATH_QUALIFIED`.

This was a bounded compatibility diagnostic only.  It did not transfer a
model, change or inspect a C target outcome, execute a frozen target, or emit
scientific timing/capture evidence.

On the unchanged RTX3090 / SM86, driver `570.124.04`, CUDA 12.4.131, and
PyTorch `2.5.1+cu124` environment, NVBit 1.7.6 `instr_count_bb` and
`mem_trace` each timed out before a PyTorch workload kernel for both
elementwise and GEMM (60-second caps).  Under the same runtime, fixed NVBit
1.8 archive `72a2b827f9531dcb86b6be13844f267640fb440929d92944177029da6da2b9e1`
passed baseline, per-basic-block `instr_count_bb`, per-instruction
`instr_count`, and official per-memory-instruction `mem_trace` for both
workloads in 2--3 seconds.  The two official memory-trace canaries emitted
real memory records.

After that direct official-path pass, the unchanged C16 tracer source was
rebuilt against NVBit 1.8.  Its elementwise and GEMM canaries completed in
3--4 seconds and produced real trace files.  This qualifies a memory-trace
path on this node; it does not qualify a C target, model deployment, timing
result, or selector outcome.

The controlled comparison makes the prior failure an NVBit-version/tool-path
compatibility boundary under this runtime, rather than evidence that PyTorch,
the RTX3090, or driver 570 alone is causally defective.  No claim is made
about any untested workload.

Formal frozen-target execution remains blocked because 37,780,586,496 bytes
are available remotely, below the 100 GiB storage gate.  The node is retained
idle and awaits an explicit user decision on trace-storage expansion.  All
retained discriminator artifacts are dual-endpoint SHA-closed and remain
outside Git.
