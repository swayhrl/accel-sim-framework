# Phase B — Qwen 0.5 capture handoff

Entry requires Phase A status `IDENTITY_AND_LOCAL_ASSET_RECOVERED` for `qwen_0p5`.

Do not infer the exact Qwen generation from the label. The Phase A identity is authoritative.

Execute the reusable `MODEL_CAPTURE_S0_S6_TEMPLATE_HANDOFF.md` with a dedicated deployment such as:

```text
c16_nvbit175_recovery_qwen0p5_v1
```

## Qwen-specific checks

- Freeze the exact tokenizer/input contract from authoritative project evidence.
- Record whether attention uses eager/SDPA/flash-style backend; do not silently change it between S1 and S5.
- Record KV-cache implementation and whether decode uses distinct kernels from prefill.
- Expect shape-dependent dispatch; do not require the Llama `indexSelectLargeIndex` path.
- If the model uses fused attention/MLP kernels, target discovery must report their exact function identity rather than a high-level operator name.

## Required phase outputs

```text
QWEN0P5_PREFILL_TARGET_MANIFEST
QWEN0P5_DECODE_TARGET_MANIFEST
QWEN0P5_S3_CANARY
QWEN0P5_S4_REPRO
QWEN0P5_S5_PREFILL
QWEN0P5_S5_DECODE
QWEN0P5_S6_PUBLICATION
```

A zero for one target in one phase is allowed only with an independent census proving `STRUCTURAL_ZERO_TARGET_NOT_LAUNCHED` and another decode target considered where required by the scientific consumer.
