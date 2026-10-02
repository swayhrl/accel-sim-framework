# AWMA R23G R81 live mixed-dispatch validation V1

Stage: `AWMA_R23G_R81_LIVE_DISPATCH_109_V1`

Final decision:
`R23G_R81_LIVE_DISPATCH_LOCAL_RESPONSE_PRESENT`

## 1. Public validation cohort

The validation source is the public Hugging Face test split of
`korotkov/glaive-function-calling-v2-parsed` at exact revision
`b5b1a23f1a88b180d512789ab0a77bf0764dc774`. The pinned JSON is 37,743,768
bytes with SHA256
`eb796aacc2d775f52f8e7bb3edaa4dddfb52044e2e5b8e13f0226bbba482b516`.

Of 12,553 source rows, 5,350 passed the frozen structural and XGrammar 0.2.8
compile filter. Canonical record hashes were sorted and the first 24 formed the
qualification pool. B0/A0 alone then qualified all 24; the first 12 were frozen
before any M1 execution and grouped consecutively into V0/V1/V2. No union
fraction, output length, timing, or candidate performance influenced selection.
This parsed derivative is a structured-generation validation cohort, not an
independent production distribution.

## 2. Exact online union cost

The only union implementation uses the current active CPU XGrammar bitmasks, a
persistent `uint32[4748]` buffer, NumPy OR/reduce, and a fixed 256-entry byte
popcount LUT. It applies strict `<0.01` over vocabulary 151,936. The cost is
inside M1 LIVE_HEAD.

| Batch | OR/step median (ms) | Popcount/step median (ms) | Branch/step median (ms) | Total union+dispatch/step median (ms) | Total/generation median (ms) |
|---|---:|---:|---:|---:|---:|
| V0 | 0.006665 | 0.044135 | 0.000533 | 0.075711 | 2.244045 |
| V1 | 0.005556 | 0.043200 | 0.000417 | 0.073022 | 7.079472 |
| V2 | 0.008052 | 0.050839 | 0.000498 | 0.089197 | 2.371240 |

The total exceeds the three isolated components because it also contains the
fixed active-row indexing, byte-view/LUT materialization overhead, timers, and
scalar plumbing within the exact dispatch function.

## 3. Real A0/A3 switching

The semantic canary and every formal run followed the same deterministic arm
trajectory:

| Batch | Steps | A0 | A3 | A3 fraction | Transitions | Longest A0/A3 run |
|---|---:|---:|---:|---:|---:|---:|
| V0 | 29 | 6 | 23 | 79.31% | 4 | 3 / 16 |
| V1 | 94 | 23 | 71 | 75.53% | 8 | 14 / 25 |
| V2 | 27 | 10 | 17 | 62.96% | 6 | 6 / 6 |

The old C1 engineering fixture also passed 72/72 exact online-union counts,
72/72 retrospective arm classifications, and 72/72 selected-token checks. It
was not reused as validation performance evidence.

## 4. Net LIVE_HEAD response

LIVE_HEAD includes union, dispatch, unchanged A0/A3 duplicate unpacking,
grouping/metadata/H2D, head compute, reduction, winner D2H/synchronization,
launches, and real arm transitions.

| Batch | Group 0 saving | Group 1 saving | Group 2 saving | All group medians favor M1 | Every gap > 3x larger-arm MAD |
|---|---:|---:|---:|---|---|
| V0 | 24.16% | 24.48% | 23.98% | Yes | Yes |
| V1 | 31.32% | 30.91% | 33.80% | Yes | Yes |
| V2 | 15.72% | 15.52% | 15.52% | Yes | Yes |

All three B4 batches are stable local positives. Exact per-sample values and
every step are retained in the formal and dispatch-trace tables.

## 5. Complete-generation safety

No batch had a stable complete-generation regression above 2%:

- V0 group medians favored M1 by 2.82--5.10%.
- V1 favored M1 by 0.24--14.70%, with substantial wall-time variance in two
  groups.
- V2 favored M1 by 4.19% and 4.01% in two groups; the third was 1.12% slower,
  below the safety threshold and not noise-stable.

Complete generation is secondary safety evidence, not a new universal benefit
claim.

## 6. Answer to the scientific question

Yes. The old conditional sparse-state response survives exact online union
computation and real live A0/A3 switching on all three new public B4 batches.
All B0/M1 token trajectories, stop positions, JSON texts, schema checks, and
matcher terminations are exact. This is a bounded software execution result; it
does not authorize or motivate an automatic hardware mechanism.

## Contents

The pack contains the frozen authority/cohort, exact union contract, old-fixture
canary, semantic results, all formal samples, all per-step dispatch records,
response summaries, environment/lock receipts, raw index, and hash closure.
