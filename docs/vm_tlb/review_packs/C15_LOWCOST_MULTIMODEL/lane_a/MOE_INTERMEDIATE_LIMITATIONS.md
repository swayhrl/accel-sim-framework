# MoE intermediate-size limitation

The `intermediate_sizes` values retained for Qwen3-30B-A3B (6144),
DeepSeek-V2-Lite (10944), and gpt-oss-20b (2880) are the bounded,
immutable-revision config scalars observed in this closeout. They are not a
complete description of routed-expert width, shared-expert width, per-layer
heterogeneity, routing grouping, or runtime expert activity.

Therefore these values must not be used for MoE clustering, capacity grouping,
or a later dynamic inference. The existing static identity/KV facts remain
unchanged; a future MoE width representation requires separately authorized,
source-complete evidence.
