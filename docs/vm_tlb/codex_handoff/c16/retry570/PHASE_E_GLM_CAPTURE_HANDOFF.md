# Phase E — GLM capture handoff

Entry requires Phase A status `IDENTITY_AND_LOCAL_ASSET_RECOVERED` for `glm`.

The exact GLM/ChatGLM generation and revision must be recovered from authoritative project evidence. Do not infer the variant from the generic label.

Execute `MODEL_CAPTURE_S0_S6_TEMPLATE_HANDOFF.md` with a dedicated deployment such as:

```text
c16_nvbit175_recovery_glm_v1
```

## GLM-specific checks

- Freeze exact architecture/config/tokenizer implementation and any `trust_remote_code`-style local code snapshot or equivalent custom model code used by the frozen asset.
- Hash-close custom modeling code in addition to weights/config when present.
- Record attention backend, rotary/position handling, KV-cache representation, dtype/quantization and device-map/offload.
- Do not assume GLM kernel identities resemble Llama/Qwen.
- Use separate prefill/decode census and phase-target manifests.
- If custom kernels or JIT/extension modules are built at runtime, record source/hash/build outputs and keep them fixed between S3/S4/S5.

## Required outputs

```text
GLM_RUNTIME_RECEIPT
GLM_CUSTOM_CODE_RECEIPT
GLM_PREFILL_TARGET_MANIFEST
GLM_DECODE_TARGET_MANIFEST
GLM_S3_CANARY
GLM_S4_REPRO
GLM_S5_CAPTURE_SUMMARY
GLM_S6_PUBLICATION
```

Any structural zero must be backed by a phase kernel census, never inferred from an empty trace alone.
