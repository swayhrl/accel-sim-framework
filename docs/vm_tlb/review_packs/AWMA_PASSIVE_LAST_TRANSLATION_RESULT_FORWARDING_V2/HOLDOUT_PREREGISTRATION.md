# Future independent holdout preregistration

Stage: `AWMA_PASSIVE_LAST_TRANSLATION_RESULT_FORWARDING_V2`

Frozen before any V2 performance run on 2026-09-25.

## Primary future holdout

- structural identity: `STR_e0922aa2a506`
- phase/family: `DECODE / AT_NATIVE_REDUCE`
- selection basis: pre-existing Lane D meta-suite, capture priority, and
  operator-family diversity only

## Sole permitted fallback

Only if the primary identity cannot be captured legally because of
producer-runtime identity or trace-grammar incompatibility:

- structural identity: `STR_48b98b28a393`
- phase/family: `DECODE / AT_NATIVE_UNROLLED_ELEMENTWISE`

No other fallback is permitted. The primary/fallback choice must not depend on
V2 development performance, hit counts, or any mechanism result.

## Isolation

This stage does not capture, inspect, or run the future holdout. It does not
start node109 GPU work. The future holdout remains independent of the seven
development targets used to implement and evaluate V2.
