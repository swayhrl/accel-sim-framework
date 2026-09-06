# M5.E1 — Parboil static trace-feature audit

Status: **STATIC_SOURCE_AUDIT_COMPLETE — NO V100 CAPTURE CLAIM**

Source: clean Parboil commit 4e0fc54866546efa44fe93af57c9cef62f6c8eb9.
This audit is source-only. It identifies work that must be checked against the
actual NVBit trace/frontend semantic contract after a clean CUDA-11.8/sm70
V100 build. It neither declares a trace exception nor promotes any row to
TRACE_CAPTURE_READY.

| workload | source evidence | static classification | V100 capture consequence |
| --- | --- | --- | --- |
| bfs | kernel.cu uses texture Node/Edge fetches, atomicAdd, atomicMin, atomicExch, atomicOr, and a global-barrier protocol | RUNTIME_AUDIT_ATOMICS_TEXTURE_GLOBAL_BARRIER | prove dynamic grouping/order/atomic/texture contract before trace capture |
| cutcp | cutoff6overlap.cu uses cudaStream, cudaMemcpyToSymbol and CUDA global kernels | RUNTIME_AUDIT_STREAM_CONSTANT | prove stream ordering and constant-memory representation before trace capture |
| histo | histo_prescan.cu uses atomicMin/atomicMax; histo kernels use multiple global phases | RUNTIME_AUDIT_ATOMICS | prove atomic lifecycle/order representation before trace capture |
| mri-q | computeQ.cu defines constant device kValues and main transfers with cudaMemcpyToSymbol | RUNTIME_AUDIT_CONSTANT | prove constant-memory representation before trace capture |
| sad | sad4.cu uses two-dimensional texture fetches through tex2D | RUNTIME_AUDIT_TEXTURE | prove texture/cache-control representation before trace capture |
| stencil | kernels.cu and main.cu show global-memory stencil kernels and ordinary copies; no atomic, texture, constant-memory or stream use found in the selected CUDA source scan | STATIC_TRACE_CANDIDATE | still requires clean V100 build, checker and dynamic trace contract before readiness |

The source scan is deliberately conservative. A feature is not treated as
unsupported merely because it appears; the runtime audit must show whether the
captured dynamic trace preserves the operation and ordering semantics required
by the validated DTC pipeline. Any workload-local unsupported outcome remains
local and cannot revert the formal trace path for other workloads.
