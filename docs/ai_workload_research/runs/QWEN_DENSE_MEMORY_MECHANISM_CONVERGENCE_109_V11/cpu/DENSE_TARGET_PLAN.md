# Dense target plan

Existing V9 timeline, reused through V10's compressed node ledger, shows gate_up/down account for about78% of dense time in B1/B2. O-proj adds about5.5%. Representative layer0/layer17 counters do not measure all layer instances.

Disable kernel renaming explicitly. With demangled regex .* (gemv|gemm) .* (without spaces), global filter counting and only the first true decodeGraph, launch-skip1/count3 selects layer0 O/gate_up/down. Skip69/count3 selects layer17. The V10 counter worker provides a first-graph profiler-start/stop precedent after two warmups.

Do not include cutlass alone in the filter: FlashAttention parameter types contain that word, shifting ordinals. Do not use launch-skip-before-match or per-launch-config counting for the dense ordinals.

Dense ordinals0-based: layer0=1/2/3; layer17=69/70/71. Without a name filter but inside decodeGraph, individual target skips are B1 layer0=6/8/10, layer17=193/195/197; B2 layer0=8/10/12, layer17=229/231/233, each count1. Whole-step ordinals include8pre-graph kernels. Numeric graphNodeId is not a launch ordinal. All-kernel count3 from O would include norm and miss down.

One contiguous triplet requires one NCU invocation per batch condition. Mid-layer validation is a separate matched pair. No verified selector for six disjoint global ordinals in one invocation is established; kernel-id invocation counting also depends on matching kernel and launch configuration.

B2 O/down have identical names and grid/block. Their compiled K differs2048vs11008, so preserve order and compiled-source evidence. All matrix shapes and weight sizes are static contracts plus runtime descriptor evidence, not captured launch arguments.

Request only the established DRAM-read/duration metric pair with disable-extra-suffixes. Audit exactly three matching results and actual onepass for each node. V10 QKV onepass does not guarantee new kernels use onepass; missing backup counters remain unknown.

Only CPU standard libraries were used. JSON records input hashes, compressed/decompressed sizes, process RSS high-water and thread counts. No GPU/CUDA/NVML operation, torch/vllm import, source modification or duplicate large raw archive occurred.
