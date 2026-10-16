# Trace producer receipt and admission boundary

VERIFIED_RUN: bounded full producers captured using the existing unmodified NVBit1.7.5 / Accel-Sim tracer5 binary (`14891b...` full SHA in CAPTURE receipts), producer commit `147b8a0c`. No tracer rebuild, toolchain upgrade or simulator run.

The initial CUDA_INJECTION64_PATH attempt returned native PASS but no tracer output. Loader repair retained three additional attempt namespaces: LD_PRELOAD alone diagnosed missing `cuGetExportTable`; explicit existing `libcuda.so.1` resolved that dependency and exposed missing PATH; binding existing CUDA12.8 nvdisasm completed both captures. These are launcher/environment repairs within one bounded phase, not repeated replacement selection. Every original failure log/return code is retained. Working environment: `LD_PRELOAD=<tracer_tool.so>:libcuda.so.1`, PATH includes `/usr/local/cuda-12.8/bin`, NVDISASM points to that installed nvdisasm. No shared environment was changed.

`TRACE_AUDIT.json` verifies all declared instruction records in all warps/CTAs against complete grid/block geometry, SHA-closes each ordered member, records actual cubin version, dynamic opcodes and memory widths, and preserves terminal opcodes. This producer-format check is not simulator timing/semantic qualification.

## SpMV

Four complete `spmv_jds` instances: three warmups and the final measured-operator counterpart, every one36 CTAs/36 warps/2,927 warp instruction records. Cubin version89; kernel binary/input match native producer. Input HtoD and constant-copy records are retained in `SpMV_kernelslist.g.txt`. No skipped-CALL warning. Source output comparison also passes under instrumentation. This is the complete fixed small input, with no prefix or favorable-component slicing. It is a produced SASS input pending174's opcode/trace/config admission; no simulated speedup is asserted.

## LayerNorm

Six complete kernels: two affine initialization fills, three complete LayerNorm warmups, final complete LayerNorm counterpart. All four LayerNorm instances have1024 CTAs/4096 warps/2,324,480 warp instruction records each; actual kernel name/resources match the native operator audit. The capture process exits0 and its all-element FP64 correctness check passes with the same input/output SHA as uninstrumented qualification.

**NOT ADMITTED for DTC simulation.** Actual PyTorch cubin version is86, executing legally on the SM89 RTX4080 device. Device architecture is not evidence of an SM89 cubin. In addition the unmodified tracer explicitly skips `CALL.REL.NOINC` (29 static discovery warnings), and the native LayerNorm SASS contains that instruction. Therefore a successful file/grid audit does not prove a complete instruction/dependency contract. No permission is inferred to omit its cost, map an SM86 trace to an unqualified target, rewrite the operator or search replacements. The valid baseline-native LayerNorm results remain; the trace is retained as a diagnostic artifact for support-domain review, not a main-table DTC row.

## Cache/predecessor scope

ACTIVE_FROM_START=1 preserves every captured initialization/warmup kernel rather than only the last favorable kernel. Final operator ordinal is fixed. No arbitrary prefix is represented as full-operator performance. The tool's kernels list records synchronous HtoD copies for SpMV; LayerNorm's list has no HtoD record although its native producer copies CPU input to GPU (asynchronous transport is outside the recorded callback list). Memset/allocator/driver traffic is not comprehensively represented. Thus predecessor kernels are available, but exact initial cache state is not proven. A simulator must replay the documented prefix and explicitly scope initial-state approximation; a cold final-kernel-only replay is a separate counterfactual, not the paired warm native measurement.

No new family or shape was selected after these outcomes. Only the primary LayerNorm shape was traced; its single native sensitivity size is not another program. No complete LLM, weights or simulator scan was launched. Scientific trace admission stops at the stated support boundary; ordinary packaging and durable verification continue.
