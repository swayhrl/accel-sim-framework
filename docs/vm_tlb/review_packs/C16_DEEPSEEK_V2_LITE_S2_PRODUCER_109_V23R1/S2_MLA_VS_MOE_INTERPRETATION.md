# DeepSeek S2 MLA vs MoE anchors

MLA is `kv_b_proj` expansion from exact normalized compressed latent, not a persistent-cache direct-read claim. It has 31 direct-GLOBAL static MREFs, 11 executed shards and 271360 active-lane events.

MoE is natural routed expert 4 `down_proj`, with exact route weight 0.07594462484121323. It has 243 direct-GLOBAL static MREFs, 169 executed shards and 11538432 active-lane events.

No cross-process VA, chronology, reuse-distance, or cache/TLB causality comparison is made.
