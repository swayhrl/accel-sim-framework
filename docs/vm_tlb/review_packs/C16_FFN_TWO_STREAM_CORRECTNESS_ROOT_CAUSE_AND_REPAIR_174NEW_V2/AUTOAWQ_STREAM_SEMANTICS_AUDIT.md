# AutoAWQ stream semantics audit

## Exact Python authority

The accepted environment binds AutoAWQ 0.2.7.post3 wheel SHA256 `02e09d71ca961ca131ac9963a2635fe8c34eb52d6b6a104b8574056aef8f2efe`. The exact wheel's `awq/modules/linear/gemm.py` SHA256 is `7cdf8fb01dabbfcd7f8be8bb58dcaf68a76073f2f91fc0e7c96881094e6a2913`. It prefers `awq_ext` when importable.

For decode M=1, the heuristic is false and Python calls `awq_ext.gemm_forward_cuda(..., 8)`. For prefill M=2048, the heuristic is true and Python calls `awq_ext.dequantize_weights_cuda(...)` followed by `torch.matmul`. Neither extension call receives an explicit CUDA stream argument at the Python interface.

## What is and is not established

`torch.matmul` is issued inside the active PyTorch stream context selected by the wrapper. However, correctness also requires the preceding dequantize output to be produced on a compatible stream with valid lifetime/workspace semantics. Decode contains the accepted GEMM plus reduction sequence, but both are behind the opaque extension call; their exact binary-level stream acquisition cannot be recovered from the Python wheel. The exact installed 109 `autoawq-kernels` distribution version, `awq_ext` path/SHA, compiled source commit, and C++ stream acquisition are absent from the accepted receipts and durable raw. They remain `UNKNOWN`; public upstream source is not substituted for the 109 binary.

The accepted M=1 trace observed some gate/up overlap, so at least part of the decode path can execute on different streams. That evidence is quarantined by correctness failure and does not establish prefill safety. No hash-closed source explicitly promises or forbids concurrent-stream use. Consequently the only confirmed root cause is accidental prefill scope expansion, not a unique `awq_ext` defect.

## Bound fields

```json
{
  "actual_109_extension": {
    "autoawq_kernels_distribution_version": "UNKNOWN",
    "awq_ext_binary_path": "UNKNOWN",
    "awq_ext_binary_sha256": "UNKNOWN",
    "awq_ext_presence": "INFERRED_FROM_ACCEPTED_KERNEL_IDENTITY",
    "compiled_source_commit": "UNKNOWN",
    "decode_reduction_stream_binding": "UNKNOWN_AT_BINARY_LEVEL",
    "default_stream_or_global_workspace_assumptions": "UNKNOWN",
    "dequantize_kernel_current_stream_binding": "UNKNOWN",
    "explicit_concurrent_stream_support_statement": "NOT_FOUND_IN_HASH_CLOSED_PYTHON_WHEEL; COMPILED_EXTENSION_UNBOUND",
    "gemm_kernel_current_stream_binding": "UNKNOWN_AT_BINARY_LEVEL",
    "torch_matmul_stream_binding": "PYTORCH_CURRENT_STREAM_CONTEXT_SOURCE_LEVEL"
  },
  "autoawq_version": "0.2.7.post3",
  "gemm_source_path": "awq/modules/linear/gemm.py",
  "gemm_source_sha256": "7cdf8fb01dabbfcd7f8be8bb58dcaf68a76073f2f91fc0e7c96881094e6a2913",
  "metadata_sha256": "a1507a39c59e1e76d2d782d8ea9846c8c02cfbb6ad2818b8a23a6a1b4eb02f4d",
  "python_source": {
    "decode_M1": "awq_ext.gemm_forward_cuda(..., split_k_iters=8)",
    "explicit_stream_argument_to_awq_ext": false,
    "prefill_M2048": "awq_ext.dequantize_weights_cuda(...) then torch.matmul",
    "threshold": "x.shape[0] * x.shape[1] >= 1024"
  },
  "wheel_sha256": "02e09d71ca961ca131ac9963a2635fe8c34eb52d6b6a104b8574056aef8f2efe"
}
```
