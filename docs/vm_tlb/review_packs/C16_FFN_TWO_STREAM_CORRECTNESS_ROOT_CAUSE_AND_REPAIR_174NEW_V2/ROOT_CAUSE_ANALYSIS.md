# FFN two-stream V1 correctness root cause and V2 repair

## Confirmed failure stage

V1 installs `make_concurrent_mlp_forward` on all 28 layers before the model prefill call. Its `concurrent_forward` has no `active_decode` guard, so B1 changes prefill as well as D0-D3. The first recorded generated token is computed directly as `argmax(prefill.logits[:, -1, :])` before the decode loop. B0 produces `23578`; B1 produces `143907`. Therefore prefill output drift is already proven and the classification is `PREFILL_SCOPE_CONTAMINATION_CONFIRMED`.

This does not uniquely identify the low-level defect. The exact AutoAWQ Python wheel chooses a different prefill backend (`dequantize_weights_cuda` plus `torch.matmul`) from the M=1 decode backend (`gemm_forward_cuda`). The compiled 109 `awq_ext` binary/version/source was not recorded, so default-stream, workspace, or concurrency assumptions remain possible rather than proven causes.

## Minimal repair

V2 adds one scope guard as the first statement of the bound concurrent wrapper:

```python
if active_decode["value"] is None:
    return original_forward(hidden_state)
```

`original_forward` is the bound method saved before replacement. During prefill it bypasses all gate/up concurrency. D0-D3 set `active_decode` before invoking the model and therefore retain the complete V1 two-stream/event DAG. The resulting runner SHA256 is `0297e142457ea5ac4ed3d6c37889993fda4168bfcca8392b41d74ba4b698fc0b`.

`scientific_target_change = NONE`. `execution_scope_correction = PREFILL_RESTORED_TO_ACCEPTED_BASELINE`. Model, input, D0-D3 scenario, kernels, quantization, layout, two streams, event dependencies, ABBA protocol, oracle, and held-out target are unchanged.

## V1 preservation

Commit `ef517d8e5a0e3659abe71b49beeba1559cd5f2ce` remains `CORRECTNESS_MISMATCH_STOP`. Its 10 observed overlap windows remain quarantined and have no scientific performance use. V2 is canary-first; any remaining token/hash mismatch becomes `CORRECTNESS_MISMATCH_AFTER_PREFILL_REPAIR` and stops without a second on-site repair.
