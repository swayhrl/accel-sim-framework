# Headroom analysis

All three arms passed the frozen full-gradient contract before timing. Each arm has
15 formal samples in three paired groups, with two warmups per group.

- B0 materialized PyTorch: 4.890624 ms median, 0.004736 ms MAD.
- B1 CCE exact/no-filter: 7.571456 ms median, 0.008192 ms MAD.
- B2 Liger Triton/Ada: 673.950745 ms median, 0.056458 ms MAD.

B1 is the fastest qualified no-full-logits arm, but it is 54.82%
slower than B0. B0 is only the materialized correctness/reference baseline; its
advantage is not called a hardware speedup.

B2 is stable but is a poor fit for this short real shape. At V=151936, H=896 and
the pinned source chunk-memory constant, its increment factor is 170, chunk size is
2, and it executes 128 chunks. With FP32 accumulation required by the frozen
numerical contract, repeated full classifier-gradient accumulation explains the large
runtime. This is an explained software-organization result, not instability.

## State/lifetime localization

B1 has no full T x V logits. Its peak allocated delta is
818872320 bytes; mandatory committed output is
272726276 bytes. The remaining 546146044 bytes
closely matches one full FP32 classifier-gradient accumulator (544538624
bytes).

The one permitted NSYS capture contains 7869598 ns of GPU kernels. Two exact
full-gradient-sized state operations have grid_x=132944, exactly (V*H)/1024:

- FP32 accumulator zero-fill: 751779 ns (9.55%).
- FP32-to-BF16 classifier-gradient copy/cast: 1318821 ns (16.76%).

The conservative residual uses only explicit full-accumulator zero initialization:
9.55% of the profiled kernel timeline, above the 5% screen.
The copy/cast is only a wider envelope because committing BF16 grad_weight is
mandatory. CCE backward and LSE kernels are not counted as removable loss math.

This is local operator evidence, not an end-to-end claim. Allocator and saved-tensor
bytes are logical state evidence, not DRAM traffic.

NSYS localized the residual; NCU was not run because profiling the mandatory CCE
backward kernel would not strengthen the state/lifetime identity.
