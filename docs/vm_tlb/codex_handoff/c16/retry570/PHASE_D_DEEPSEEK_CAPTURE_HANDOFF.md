# Phase D — DeepSeek capture handoff

Entry requires Phase A status `IDENTITY_AND_LOCAL_ASSET_RECOVERED` for `deepseek`.

The exact DeepSeek family/variant must come from authoritative project evidence. Do not infer V2/V3/R1/distill/coder/chat/base from the generic label.

Execute `MODEL_CAPTURE_S0_S6_TEMPLATE_HANDOFF.md` with a dedicated deployment such as:

```text
c16_nvbit175_recovery_deepseek_v1
```

## DeepSeek-specific checks

- Record exact architecture and whether the target is dense or MoE.
- If MoE, record expert routing/top-k/expert-count behavior visible in the frozen workload; do not silently collapse or replace MoE execution.
- Record attention backend and KV-cache implementation.
- Preserve deterministic routing/input if routing is data-dependent.
- Expect prefill/decode to use different fused kernels and potentially different memory targets.
- If a custom fused kernel contains multiple address-bearing global loads, the target manifest may contain multiple static ranges; do not arbitrarily select one if the downstream scientific consumer requires the combined stream.
- If the exact model cannot fit under the frozen runtime, do not switch to a distill/smaller model without explicit new scientific authorization.

## Required outputs

```text
DEEPSEEK_RUNTIME_RECEIPT
DEEPSEEK_ARCHITECTURE_RECEIPT
DEEPSEEK_PREFILL_TARGET_MANIFEST
DEEPSEEK_DECODE_TARGET_MANIFEST
DEEPSEEK_S3_CANARY
DEEPSEEK_S4_REPRO
DEEPSEEK_S5_CAPTURE_SUMMARY
DEEPSEEK_S6_PUBLICATION
```

The final report must make clear whether observed memory behavior includes dense attention/MLP, MoE routing/expert kernels, or both.
