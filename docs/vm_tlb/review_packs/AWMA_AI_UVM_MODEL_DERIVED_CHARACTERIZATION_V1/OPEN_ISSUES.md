# Open issues

1. The bounded PyTorch managed tensor bridge is `NOT_READY`: the single extension attempt lacked `cuda_runtime_api.h` on its compiler include path. This is an integration gap, not evidence about PyTorch/UVM performance.
2. D2 has exact KV byte/layout accounting but an approximate 256-token-block sequential access replay. End-to-end scheduling, allocator, attention compute, and serving concurrency are not modeled.
3. OLMoE is naturally resident on this RTX 4080. A larger *runnable and already local* MoE would be required to study natural expert oversubscription without artificial scaling; this stage does not authorize that follow-up.
4. Fault/TLB/PPN/page-size telemetry remains unavailable and must not be inferred from migration memcpy records.
