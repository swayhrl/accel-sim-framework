# Phase C — Qwen 7B AWQ capture handoff

Entry requires Phase A status `IDENTITY_AND_LOCAL_ASSET_RECOVERED` for `qwen_7b_awq`.

AWQ is part of the frozen scientific identity. Do not replace with FP16/BF16/GPTQ/GGUF or a different parameter scale.

Execute `MODEL_CAPTURE_S0_S6_TEMPLATE_HANDOFF.md` with a dedicated deployment such as:

```text
c16_nvbit175_recovery_qwen7b_awq_v1
```

## Qwen 7B AWQ-specific checks

- Record exact AWQ library/backend and version actually used.
- Record whether kernels are custom quantized GEMM/GEMV/dequant/fused ops rather than stock ATen kernels.
- Freeze backend selection before S1 and keep it fixed through S5.
- Confirm the 7B AWQ model fits without changing offload/device-map policy; if not, stop with a precise frozen-contract blocker rather than switching precision or model size.
- Quantized weights can shift the dominant memory path; choose targets from observed phase census, not from Llama/Qwen0.5 assumptions.
- If decode uses GEMV-like kernels while prefill uses GEMM-like kernels, preserve separate target manifests.

## Required outputs

```text
QWEN7B_AWQ_RUNTIME_RECEIPT
QWEN7B_AWQ_PREFILL_TARGET_MANIFEST
QWEN7B_AWQ_DECODE_TARGET_MANIFEST
QWEN7B_AWQ_S3_CANARY
QWEN7B_AWQ_S4_REPRO
QWEN7B_AWQ_S5_CAPTURE_SUMMARY
QWEN7B_AWQ_S6_PUBLICATION
```

Report quantization/backend identity prominently in the final pack so cross-model analysis does not confuse architecture effects with quantization effects.
