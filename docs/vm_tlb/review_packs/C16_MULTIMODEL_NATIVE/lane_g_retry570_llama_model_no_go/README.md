# Retry570 Llama model-level NVBit NO-GO

Status: `NVBIT_RETRY570_LLAMA_MODEL_CANARY_NO_GO`.

The exact P0 Llama S0/TEXT baseline passed on CUDA with `float16`, `sdpa`,
eager/uncompiled execution, no CPU offload, and output checksum
`c5f81e7f…f6d65`.  It is diagnostic-only and is not native timing evidence.

NVBit 1.8's official `mem_trace` and the C16 tracer both loaded, but neither
materialized a model-level NVBit kernel-launch/memory-record event, C16 trace,
or C16 kernel catalog.  One bounded instruction-interval widening was used to
distinguish an empty first-instruction interval from this model-level failure;
it did not change the outcome.  The retained evidence supports a model CUDA
launch/NVBit callback-materialization boundary, not a driver-only claim.

Accordingly, Qwen0.5, Qwen7-AWQ, storage projection from a non-existent model
trace, and every frozen C target remain unexecuted.  No shape, context, dtype,
backend, offload, selector, or kernel-name substitution was attempted.
