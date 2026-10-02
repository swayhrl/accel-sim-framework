# Frozen B0/S1/S2 arm contract

Frozen before GPU qualification/timing. All arms use the exact accepted model,
255-position token input, BF16 tied W, full Qwen backbone, CCE exact/no-filter
math, fixed CCE meta, and the common explicit AdamW contract.

## Shared forward and CCE primitives

- All non-W model parameters have `requires_grad=False`; tied W remains trainable.
- `use_cache=False`, no gradient checkpointing, DDP/FSDP, scaler, accumulation,
  clipping, or architecture/config change.
- CCE forward produces the exact loss and full-vocabulary LSE.
- Accepted first-store CCE backward is invoked through the exact patched
  `cce_backward_kernel`; `CCE_DC_FIRST_STORE=1` and `CCE_AUTOTUNE=0`.
- dH is propagated manually through the autograd-connected final hidden state.
- B0/S1 use normal PyTorch input embedding; S2 uses an opt-in custom embedding
  backward that stores sorted unique token IDs plus their accumulated BF16 rows
  and returns no dense W gradient.
- The same row-tile AdamW function consumes every arm's total gradient.

## B0_STRONG

CCE generates dH and a complete classifier dW before backbone backward. The full
classifier dW is retained while dH propagates and the normal dense lookup
contribution is produced. The two contributions are merged into one complete
BF16 W gradient, consumed by AdamW, and released.

## S1_LATE_FULL

CCE first generates dH only. After full backbone backward creates the normal
dense lookup-side W gradient, CCE generates one complete classifier dW. It is
merged into the full gradient, consumed by AdamW, and released. S1 therefore
still materializes full VxH gradients but delays their lifetime.

## S2_LATE_TILED

CCE first generates dH only. Backbone backward produces only compact unique-row
lookup gradients. Classifier dW is then generated in deterministic vocabulary
row macro-tiles; compact rows in the current range are merged, the same AdamW
consumer updates that W/m/v tile exactly once, and all tile temporaries are
released before proceeding. Formal S2 never allocates a full VxH gradient or
shadow gradient.

The classifier accumulation dtype is FP32. A 32 MiB limit yields the largest
positive multiple of `BLOCK_V=128`:

`rows_per_tile = floor(32 MiB / (896 * 4 bytes), multiple of 128) = 9344`

The FP32 classifier-gradient tile is 33,488,896 bytes and the 151,936 vocabulary
rows require 17 tiles. This value is fixed; there is no tile sweep.
