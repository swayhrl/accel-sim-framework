# Scientific interpretation

Status: `POST_HOC_DIAGNOSTIC_ONLY`. This addendum was motivated after inspection of V1 and is not a preregistered positive result. V1 remains unchanged with primary decision `TEMPORAL_AUTHORITY_INSUFFICIENT_CROSS_MODEL`.

## Exact recompute

The complete lag 1–16 spectrum is reported, not only lag 11. Lag 11 has mean overlap `7.666667`, mean Jaccard `0.928042`, and mean retention `0.958333` over 21 pairs. Its whole-step shuffle Jaccard p05/median/p95 is `0.158094` / `0.224136` / `0.313967`. The actual value is `ABOVE_SHUFFLE_P95`.

Across period-11 pairs, unordered exact-set repeats are `15`, ordered top-k repeats are `8`, and non-exact near repeats (7-of-8 or better) are `5`. Same-next-token pairs are `19` of 21. Router-input and router-logits SHA equality counts are `0` and `0`, respectively.

Lags whose actual mean Jaccard is above their own shuffle p95 are `[11]`. This full-spectrum disclosure prevents presenting lag 11 without its neighboring/control context. The permutation interval is descriptive; it is not a preregistered significance test or causal estimate.

## Token association and origin

Same-next-token pairs have a different expert-set Jaccard distribution from different-next-token pairs (see `TOKEN_ASSOCIATION.json`). Routing precedes next-token generation, so the recorded next token is an associated same-step output, not a causal input label. Current-step input tokens are `UNKNOWN` because the accepted runner/KV transition is absent; predecessor output tokens are not silently substituted.

The period-11 routing signal is confirmed in this accepted single-layer sequence and is associated with token repetition. Its origin remains unresolved between genuine generated-content repetition and capture/replay methodology. No source evidence supports labeling it a capture artifact.

## Scope boundary

Q30 has only four steps: `Q30_AUTHORITY_TOO_SHORT_FOR_PERIOD11_TEST`. DeepSeek is `SINGLE_STATE_ONLY`. Cross-model periodicity is `NOT_COMPARABLE`.

This result is not full-model temporal locality, cache opportunity, cache-line reuse distance, L2 ordering, hit rate, timing benefit, or justification for a period-11 cache policy.
