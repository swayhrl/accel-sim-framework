# Trace Acquisition Plan

A15 documents the remaining GPU and trace gap.

Use existing pretraces for smoke and pilot rows where a `kernelslist.g` is already available. For missing paper-candidate rows, acquire traces only on a GPU host with CUDA, NVBit, and `gpu-app-collection` available.

Trace generation is gated:

```bash
ACCELSIM_A15_ALLOW_TRACE_GENERATION=1 bash scripts/accelsim/a15_trace_gpu_gap_plan.sh
```

Without a visible GPU this is not a failure. A15 records `BLOCKED_NO_GPU_FOR_TRACER` and still emits the trace gap matrix and final review pack.
