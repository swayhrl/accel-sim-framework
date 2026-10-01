# Merged gate/up strong-baseline guard

## Position

Pinned vLLM `df8fd42116f172b7a53bc10c8a680b05232edbed` implements Qwen2 MLP as `MergedColumnParallelLinear(hidden, [intermediate, intermediate])`, followed by `SiluAndMul` and `down_proj`. Its mapper loads the checkpoint's separate `gate_proj` and `up_proj` tensors into logical merged shards 0 and 1. This is a mature standard software capability, not a speculative C16 mechanism.

The exact accepted Qwen2.5 AWQ checkpoint is compatible without re-quantization. For each original projection, qweight/qzeros/scales occupy `33947648`, `265216`, and `1060864` bytes. Concatenating along logical output N gives the same `70547456` total quantized bytes. `group_size=128`, zero-point and scale semantics remain unchanged. A selected MP/Marlin backend may losslessly repack the physical bytes; that is not requantization, but it does make the comparison cross-backend.

## What the merged path changes

It structurally replaces two quantized-linear calls with one, presents hidden once at the operator interface, doubles logical N from 18944 to 37888, and replaces separate SiLU and multiply with `SiluAndMul`. Therefore it can also change W4 tiling and reduction. Exact CUDA kernel count, input memory transactions, and performance are deliberately left to native validation.

Two-stream B1 changes none of those properties: it retains both WQLinear_GEMM calls, both reduction paths, both hidden consumers, and both elementwise kernels. It only permits the sibling branches to overlap. A positive B1 result can support “recoverable scheduling headroom in the current separated AutoAWQ backend”; it cannot support first/novel gate-up fusion, first avoidance of the duplicate hidden input, best software baseline, or a need for new hardware.

## Guard decision

`PLAIN_GATE_UP_CONCURRENCY_NOT_NOVEL_MECHANISM`. The two-stream diagnostic remains useful as a characterization/control. The merged vLLM path is a semantically matched strong baseline, but not a strict one-variable A/B against C16 because current vLLM selects a different AWQ/MP kernel and fused activation path. QUICK/FLUTE are not needed to establish this guard; they remain alternate low-bit kernel neighbors rather than substitutes for this exact pinned Qwen2 loader path.
