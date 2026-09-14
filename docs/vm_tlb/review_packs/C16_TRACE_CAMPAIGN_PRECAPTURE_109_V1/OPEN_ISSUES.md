# Open issues

- Matrix frozen; large formal NVBit capture BLOCKED.
- Object maps are absent. Require WEIGHT, QUANT_METADATA, KV_CACHE, UNKNOWN_RUNTIME.
- Qwen0 GEMM semantics remain UNKNOWN; do not claim FFN.
- AWQ actual backend is unfused AutoAWQ; no fused-equivalence claim.
- Raw 7B S2 OOM; no dtype/backend/context/offload retry.
- Llama is S0 canary only; Qwen3/DeepSeek remain unbound and untokenized.
