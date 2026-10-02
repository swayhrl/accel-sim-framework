# Arm contract

- `B0_DENSE_STRONG`: normal dense embedding backward plus accepted full classifier gradient; two full VxH contributions may coexist.
- `C1_COMPACT_FULL`: sorted unique compact lookup rows, native compact-domain embedding reducer, then exactly one full classifier/total gradient merged in place. No dense lookup W.grad.
- `S2_TILED`: the same compact lookup rows, deterministic 32 MiB FP32-budget row tiles, tilewise AdamW, and no formal full VxH gradient or shadow.

All arms use the same BF16 tied W, FP32 m/v, AdamW contract, CCE first-store lineage, loss math, and point-specific fixed CCE meta. CPU restore copies are outside measured regions.
