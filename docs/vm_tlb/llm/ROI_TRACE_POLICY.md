# Route-E formal ROI policy

`prefill` and `decode1` are independent formal capture runs. Each run has its
own `m4a-llama-<region>-<UTC>` directory, sidecar, raw trace, manifest, and
archive. `decode_reuse` is optional diagnostic-only and never replaces either
formal route.

For the trace phase, the parent driver sets `ACTIVE_FROM_START=0`; the frozen
tracer's `cuProfilerStart`/`cuProfilerStop` handlers control activation. The
workload calls the CUDA profiler only around exactly one selected inference
operation. All of model load, TP sharding, flat-buffer binding, static metadata
preparation, and a warmup prefill occur before activation.

| Route | inactive preparation | sole profiler-delimited operation | later work |
|---|---|---|---|
| `prefill` | load/TP/bind/warmup | B=8, S=64 prefill | three decode tokens inactive |
| `decode1` | load/TP/bind/warmup + prefill | first decode | remaining two tokens inactive |
| `decode_reuse` | above + first decode | second decode | third token inactive |

The wrapper fails on missing/invalid region, absent `ACTIVE_FROM_START=0` in
trace phase, failed profiler API calls, or a decode route that did not execute
exactly one selected decode operation. Actual profiler/NVBit behavior is an
M4A-C conditional host gate.
