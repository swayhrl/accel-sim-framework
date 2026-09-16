# C16 Qwen3 S3 KV scaling V20

Decision: `C16_QWEN3_S3_KV_SCALING_109_V20_PASS`. This is scoped strictly to layer0 first-decode `self_attn.repeat_kv(K)` as `KV_STORAGE_DIRECT_READ` materialization.

Fresh V20 isolated replays and full-scope captures were used for both S2 and S3; V18R2/V19 history was not used as the scaling baseline.
