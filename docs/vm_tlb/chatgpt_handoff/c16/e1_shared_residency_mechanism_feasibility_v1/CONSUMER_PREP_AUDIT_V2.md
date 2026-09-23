# Shared-Residency Consumer Prep Audit V2

## Prep reviewed

Consumer/design prep:

`hrl/c16-e1-shared-residency-design-review-174new-v1@547e9263a8d0c12bb34d96e27134a120b83fb6d0`

Overall design review is accepted:
- code map is grounded in accepted Core `57bb71e`;
- M1 elastic protected quota is a reasonable first simulator mechanism;
- oracle/software-region identity correctly separates policy efficacy from detection accuracy;
- M0 static partition is an appropriate stranding control;
- bounded additional trace is sufficient in principle for the proposed D2→D3 natural reuse interval.

No producer rerun or design-prep rerun is requested.

## Two small hardening points handled directly

### 1. Fixed full-budget runtime query-back must stay fixed

Upstream CUDA qualification established:

- requested full-qweight set-aside = 33,947,648 B
- runtime query-back = 37,748,736 B

The shared-hardware stage intentionally keeps the same requested full budget across:
- rotating qualification;
- SETASIDE_ONLY;
- ROTATE_CONTROL_3;
- SINGLE_L0_UP;
- SHARE2_UP;
- SHARE2_L0;
- SHARE3.

Therefore independent consumption should require the same runtime query-back value for these fixed-full-budget conditions.

A change in actual query-back is not silently accepted as equivalent policy state.

### 2. CUDA hitRatio is not an exact byte/line partition

For SHARE2/SHARE3:

- hitRatio=0.5 / 1/3 is a CUDA access-policy hint used under one fixed total set-aside.
- It must not be interpreted as exactly one-half / one-third of qweight lines being deterministically protected.
- It must not be mapped directly to an exact simulator quota fraction.

The real-hardware experiment asks whether this bounded shared policy retains multiple targets under one fixed budget.

The later simulator quota remains an independent modeled mechanism whose quotas are specified in actual line/byte units.

## Consumer hardening authority

Use before final producer consumption:

`hrl/c16-e1-shared-residency-consumer-hardening-v2`

This hardening:
- fails closed if the fixed-full-budget runtime query-back drifts from 37,748,736 B;
- preserves the hitRatio interpretation boundary;
- adds a regression test for query-back drift.

This is a correctness-preserving consumer hardening only. It does not change the 109 experimental matrix or any preregistered materiality rule.
