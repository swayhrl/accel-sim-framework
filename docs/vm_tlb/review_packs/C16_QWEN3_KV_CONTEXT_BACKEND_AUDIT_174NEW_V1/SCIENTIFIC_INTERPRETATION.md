# Scientific interpretation

## Independent raw closure

Both accepted authorities pass independently: all 16 C16WARP1 shards close their header/manifest/terminal counts and hashes, all have overflow zero, and every shard covers its full CTA extent. Source indices `237,475,713,950` join only the replay-local `KV_POST_UPDATE_K`; destination indices `241,479,717,953` join only `KV_DERIVED_REPEAT_K`. No cross-replay VA relation is used.

S2 has 16,785,408 active-lane events and grid 16,392; S3 has 67,117,056 events and grid 65,544. Both ratios are `3.998535871156662`. This is approximately fourfold, not exact, because the sequence extent is 2049 -> 8193. Source reads and destination writes each scale by the same ratio. At width-qualified U16, logical lane bytes on either side equal the expanded repeat-K tensor bytes; these are instruction-level logical bytes, not DRAM bytes.

## Backend classification

Transformers 4.51.0 eager and SDPA explicitly materialize repeated K/V. FlashAttention2 does not use the HF repeat path, and FlexAttention uses `enable_gqa=True` for the accepted power-of-two 32-head configuration. Thus the measured repeat-K kernel is an eager/SDPA-style backend implementation path, not a model-intrinsic KV-cache requirement. The backend-independent component is narrower: compact K-post storage `[1,8,T,128]` and its long-context growth, plus the model's 32/8 GQA relationship.

## Page descriptors and boundaries

`PAGE_FOOTPRINT_DESCRIPTORS.tsv` reports only per-shard values and `SUM_OF_PER_SHARD_UNIQUES`. They scale with tensor/context extent but are not TLB miss rates. This Goal proves no cache/TLB cause, reuse distance, global chronology, DRAM traffic, all-attention behavior, direct QK/AV reads from original KV storage, or backend performance ordering.

## Decision

Primary label: `EAGER_REPEAT_KV_AMPLIFICATION_INDEPENDENTLY_CLOSED_BACKEND_SPECIFIC`. Qualifications: `REPEAT_KV_MATERIALIZATION_SHARED_BY_EAGER_AND_SDPA_NOT_FLASH`, `QWEN3_KV_CONTEXT_SCALING_CLOSED_NO_ARCHITECTURE_GENERALIZATION`, and a precisely limited backend-independent compact-KV component. No cache/TLB mechanism or GPU follow-up is authorized. A future same-input eager-versus-legal-optimized-backend comparison is conditionally scientifically justified only if deployment relevance or measured performance becomes a project question.
