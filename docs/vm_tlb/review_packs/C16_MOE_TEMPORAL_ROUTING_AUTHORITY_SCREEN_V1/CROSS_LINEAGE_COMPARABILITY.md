# Cross-lineage comparability

## Result

`TEMPORAL_AUTHORITY_INSUFFICIENT_CROSS_MODEL`

| Pair / scope | Classification | Reason |
|---|---|---|
| Q30 per-layer vs OLMoE layer 1 | `PARTIAL_COMPARABLE` | Both have explicit top-k set sequences and identical set-metric definitions, but Q30 has 4 steps across 48 layers while OLMoE has 32 steps for one layer. Horizon and authority coverage differ, so no locality ranking is valid. |
| Q30 vs DeepSeek | `NOT_COMPARABLE` | DeepSeek has one explicit routing state and no temporal sequence. |
| OLMoE vs DeepSeek | `NOT_COMPARABLE` | DeepSeek has one explicit routing state and no temporal sequence. |
| Three-lineage temporal conclusion | `NOT_COMPARABLE` | The three lineages do not share a common multi-step authority level. |

No cross-lineage row qualifies as `SUPPORTED_COMPARABLE`. Q30 supplies a full-model explicit sequence but only four steps (`LOW_TEMPORAL_POWER`). OLMoE supplies a 32-step explicit sequence but only for layer 1. DeepSeek supplies only one state. These asymmetries are authority limitations, not evidence that one model has more or less temporal locality.

The screen therefore reports each supported scope separately and does not order the models by locality.
