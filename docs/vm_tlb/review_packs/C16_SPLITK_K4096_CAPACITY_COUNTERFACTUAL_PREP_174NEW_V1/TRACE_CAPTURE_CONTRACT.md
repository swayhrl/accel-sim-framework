# K4096 GEMM-only SASS capture contract

This is a design contract only. The current gate is `SIM_PLATFORM_NOT_ADMITTED_STOP` and authorizes no capture.

## Frozen identity

- Shape: M=256, K=4096, N=49152, W4 group size=128.
- Arm A: split8, GEMM grid `[49152,1,1]`, block `[32,2,1]`, 16 K-loop iterations per CTA.
- Arm B: split1, GEMM grid `[6144,1,1]`, block `[32,2,1]`, 128 K-loop iterations per CTA.
- Kernel family: `gemm_forward_4bit_cuda_m16n128k32` from `c7b0e88c327694c715b0a758d9ce8fd414a1fa21` / blob `98f49efac8626388039912e6aabc8a84d9f8303b`.
- A and B must use the same `GPT3_SHAPE_SYNTH_V1` tensor bytes and the hashes in `AUTHORITY_AUDIT.json`.

## Mandatory GEMM-only harness

A future, separately authorized capture must build a trace-only wrapper from the exact source above. The wrapper may only expose and return `_out_feats` (the GEMM scratch) before `.sum(0)`; it must not alter the GEMM kernel body, launch arguments, compile flags, or SM89 target. It then performs `scratch.sum(0)` only after `cudaProfilerStop()` to obtain the final output hash. For split1, the returned `[1,M,N]` scratch and its plane-0 output share storage.

Before capture, extract the target kernel SASS from the accepted A binary, accepted B binary, and trace-only wrapper. Canonical target-kernel SASS digests must match exactly. Any mismatch is a STOP. This wrapper removes the reduction launch from the active trace region and makes the scratch VA/range/hash observable without mixing reduction traffic into the mechanism trace.

## Two-pass selection

1. Discovery only: set `DYNAMIC_KERNEL_RANGE=1000000`; emit `stats.csv` without a trace and close the exact dynamic ID/name/grid/block.
2. Capture: intersect the exact ID with an anchored regex for `gemm_forward_4bit_cuda_m16n128k32`, set `ACTIVE_FROM_START=0`, `C16_EXACT_ROOT_FUNCTION_ONLY=1`, and bracket exactly one GEMM launch with `cudaProfilerStart/Stop` plus synchronization.
3. Require exactly one kernel in `kernelslist.g`, the frozen grid/block, binary version 89, zero unsupported opcodes, and no `reduce_kernel` trace or memory records.

## Object binding

Record half-open 64-bit VA ranges, sizes, dtype/shape, and SHA256 for input, qweight, qzeros, scales, scratch, and post-region output while all tensors are live. Reject overlaps, zero pointers, size/hash mismatch, or any qweight/qzeros/scales trace address outside its recorded range. Trace addresses are suitable for object coverage joins; current simulator telemetry is not suitable for per-object L2 hit/miss claims.

## Mandatory size pilot after platform re-admission

Full M256 capture is forbidden until an M16/K4096/N49152 pilot is captured for each arm. The pilot is only for records/bytes/time extrapolation and carries no scientific result. Apply the stop thresholds in `TRACE_SIZE_ESTIMATE.json`; exceeding any threshold requires a reduced mechanism proxy and a new gate.

## Failure rules

Stop on authority/hash drift, SASS mismatch, more than one traced kernel, any reduction record, missing scratch binding, parser rejection, unsupported opcode, address-width truncation, dropped/overflowed records, incomplete CTA count, or failed output equality. Do not expand to a full model or another K/M/N.
