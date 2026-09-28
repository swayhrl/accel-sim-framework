# Scientific interpretation

## Authority result

- Q30: `FULL_MODEL_EXPLICIT_SEQUENCE`, 48 layers × 4 decode steps, top-8. The node164 semantic receipt contains explicit IDs and token bindings; its committed summary is hash-only. Four steps are labeled `LOW_TEMPORAL_POWER`.
- DeepSeek: `SINGLE_STATE_ONLY`, layer 1, one top-6 state. No multi-step accepted/durable routing sequence was found, so no temporal metric is computed.
- OLMoE: `SINGLE_LAYER_EXPLICIT_SEQUENCE`, layer 1 × 32 consecutive decode steps, natural top-8 with weights, router input/logit hashes, and token bindings. V34 is an ancestor of accepted V40 and its routing SHA matches the V34 checksum manifest.

## Descriptive temporal result

For OLMoE layer 1, actual mean adjacent overlap is `3.032258` and mean adjacent Jaccard is `0.250659`. The 1,000-permutation marginal-preserving shuffle distributions are:

- overlap: median `2.645161`, p05 `2.193548`, p95 `3.193548`;
- Jaccard: median `0.224822`, p05 `0.171546`, p95 `0.294940`.

Its descriptive interval position is `WITHIN_SHUFFLE_P05_P95`. The observed ordering therefore does not resolve extra adjacent-set correlation beyond this marginal-preserving control. This is a bounded descriptive non-detection, not proof that the generating process has no temporal dependence, and it does not establish causality or statistical significance.

Across Q30's 48 four-step layer sequences, Jaccard interval positions are: above p95 `0`, within p05–p95 `48`, below p05 `0`. Because each sequence has only three adjacent pairs, these are low-power diagnostics and are not promoted into a Q30 temporal-locality conclusion. The mean actual Q30 adjacent Jaccard across layers is `0.341320`.

## Boundaries

Frequency locality is not temporal locality. Temporal set overlap is not a full-model cache opportunity. A single-layer expert-ID sequence is not cache-line reuse distance, L2 transaction order, hit rate, or timing benefit. Expert IDs are always interpreted as `(layer_id, expert_id)`; IDs are never mixed across layers. Route rank is not treated as kernel call order.

No LRU/cache simulator or expert-object reuse-distance proxy was run. Although Q30 has full-layer IDs, its four-step horizon is too short for a capacity conclusion; OLMoE lacks the other layers and ordinary traffic. No 4 MiB L2 mapping or performance claim is made.

## Decision

The OLMoE authority/integrity screen and bounded analysis complete as `OLMOE_SINGLE_LAYER_TEMPORAL_SCREEN_PASS`; “pass” means the sequence is valid and the screen ran, not that a positive temporal signal was found. The observed OLMoE result lies within the shuffle p05–p95 interval. The requested cross-model answer is `TEMPORAL_AUTHORITY_INSUFFICIENT_CROSS_MODEL` because DeepSeek lacks a sequence and Q30 has only four steps.
