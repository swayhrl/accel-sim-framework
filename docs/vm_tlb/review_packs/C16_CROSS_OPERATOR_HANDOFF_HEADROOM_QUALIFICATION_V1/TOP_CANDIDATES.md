# Top candidates

1. **Qwen7B FFN gate/up→activation/multiply→down** has the largest optimistic kernel-sum bound (~1.804x), but fails G0: no non-double-counted pair wall-clock union, no exclusive materialization cost, and no accepted matched strong fusion baseline. It is not Lane7-ready.
2. **AWQ dequant→MMA** has strict source identity, but accepted natural SHARE3 zero-cost ceiling is only ~1.0177x and CTA-internal staging already removes major duplication; STOP.
3. Attention and OLMoE handoffs remain timing-authority limited.

No candidate meets the revised EARLY_NATIVE_ORACLE_GATE six requirements; no early gate file is emitted.
