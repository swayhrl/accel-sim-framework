# Backend representativeness

The audit is bound to Transformers `v4.51.0`, tree commit `0720e206c6ba28887e4d60ef60a6a089f6c1cc76`, and the four blob IDs listed in `BACKEND_SOURCE_AUDIT.tsv`. No current-main behavior is substituted.

| backend | exact 4.51.0 behavior for Qwen3-8B | explicit HF repeat materialization |
|---|---|---|
| eager | Qwen3 eager calls `repeat_kv` on key and value with `num_key_value_groups` | yes |
| SDPA | integration repeats key/value before PyTorch SDPA when the module has groups | yes |
| FlashAttention2 | integration transposes and passes original key/value head counts to FA2 | no |
| FlexAttention | with 32 local query heads (power of two), keeps `enable_gqa=True`; repeat is only the non-power-of-two fallback | no for accepted configuration |

Accepted receipts bind K-post `[1,8,T,128]` to repeat-K `[1,32,T,128]`, hence 32 attention heads, 8 KV heads, and four groups. The V20 capture is therefore representative of the eager path and the same explicit-HF-repeat aspect of SDPA, but not of FA2 or normal-path FlexAttention. This source classification is not a performance ranking.
