# C16 Qwen3 S2 Attention/KV V18R2

Decision: `C16_QWEN3_S2_ATTENTION_KV_109_V18R2_PASS_WITH_SCOPED_EVIDENCE`.

This continuation preserves the V18 and V18R1 BLOCKED attempts as immutable history and does not re-admit the older MLP anchor. It closes one new Attention/KV-adjacent formal target: `layer0.self_attn.repeat_kv(K)`.

The accepted target is strictly `KV_STORAGE_DIRECT_READ`: the repeat-K direct-copy kernel reads post-update K storage in the same CUDA process and materializes a new K-repeat buffer. It is not represented as an attention-score or attention-value core target, and this scoped decision makes no claim that the QK/AV core directly reads KV-cache storage.

Exact deployment: Qwen/Qwen3-8B revision `b968826d9c46dd6066d109eabc6255188de91218`; BF16, eager attention; S2_TEXT B1/T2048/D32; validated V2 input receipt `5913c573054d23a444477394a60f3f280311325e81175663b4ae2abd5ef6aafb`.
