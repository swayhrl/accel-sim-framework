# Normalization contract

- Denominator one: 243 selected static MREF paths per isolated module, with executed and terminal zero paths kept separately. Selected path identity differs across lineages.
- Warps per executed path and lane events per warp remove raw path-count scale. Active-lane density is active lanes divided by 32 times warp records.
- Each trace is one selected natural routed expert `down_proj` invocation. Per selected module and per invocation values are numerically identical to its selected replay total; they do not describe a model-wide population. Cross-lineage per-token or per-routing-event rates are UNKNOWN because Q30 Decode3, DeepSeek selected decode and OLMoE D32 are not matched tokens or equivalent expert populations.
- Logical BF16 weight bytes (Q30 3,145,728; DeepSeek 5,767,168; OLMoE 4,194,304) normalize selected module scale. They do not describe measured bytes transferred.
- Geometry conditions on WEIGHT, INPUT, OUTPUT and OTHER; unique start address, 32B sector proxy and 128B line proxy are counted within each warp record. A sector proxy is not a cache transaction.
- Spatial concentration uses selected static MREF shards and is reported both among executed role shards and all 243 selected paths. Module/expert concentration is UNKNOWN with one module/expert per lineage.
- Unique 128B lines and cross-warp shared-line fractions are computed within each shard only. Separate shard replays may have different process addresses. Do not union them, infer cache hits, or assign chronology.
- C16WARP1 CTA/warp fields give spatial identity; its raw shards do not establish comparable natural ordering across paths. Short-window and phase metrics stay UNKNOWN.
