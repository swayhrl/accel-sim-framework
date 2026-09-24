# Cost/Benefit Consumer Resume Audit V2

## Current 174 prep

`hrl/c16-e1-residency-cost-benefit-consumer-174new-v1@278964bfb243a93adf43e748eb3e067e34b16b8a`

Status before producer:
`READY_FOR_E1_RESIDENCY_COST_BENEFIT_109`

Producer now exists:

`hrl/c16-e1-residency-cost-benefit-closure-109-v1@86ef7dcfb49241bd87ff4a8d59b4d950d53de0a5`

No producer rerun is requested.

## One pre-data consumer bug found during producer audit

The prepared native budget consumer encoded:

- per-up_proj qweight bytes = 1,212,416 B
- 28-layer total = 33,947,648 B
- BFULL hitRatio = 1

This is incorrect for the accepted deployment.

Raw producer authority confirms every gate/up/down qweight tensor is:

`33,947,648 B`

Therefore:

- exact one-layer up_proj qweight = 33,947,648 B
- 28-layer aggregate up_proj qweight footprint = 950,534,144 B
- BFULL requested set-aside remains 33,947,648 B
- BFULL hitRatio under the preregistered formula is exactly `1/28`

The producer raw BFULL policy correctly records hitRatio `0.03571428571428571`.

This is a consumer implementation error, not a scientific-contract or producer error.

## Hardening authority

Apply before consuming producer:

`hrl/c16-e1-residency-cost-benefit-consumer-hardening-v2`

This branch is based directly on the 174 prep and fixes:

- exact per-module qweight bytes;
- exact 28-layer aggregate footprint;
- hitRatio denominator;
- regression tests;
- explicit raw condition alias contract;
- explicit raw `lm_head` -> normalized `output` packaging boundary.

The scientific budget matrix and materiality rules are unchanged.

## Deterministic raw normalization

Producer native raw condition names are:

- CONTROL_B8 / FAIR_B8
- CONTROL_B16 / FAIR_B16
- CONTROL_B24 / FAIR_B24
- CONTROL_BFULL / FAIR_BFULL

The frozen consumer used normalized names:

- CONTROL_UP28_B8 / FAIR_UP28_B8
- ...
- CONTROL_UP28_BFULL / FAIR_UP28_BFULL

174 may map these names deterministically.
This is packaging normalization only.

Do not alter:
- requested budget;
- runtime actual query-back;
- selected family;
- qweight interval;
- hitRatio;
- policy properties;
- reset history.

Preserve both raw and normalized names plus source SHA.

Producer raw final-stage category:
`lm_head`

Consumer normalized category:
`output`

174 may normalize `lm_head -> output` while preserving the raw category and source SHA.
No other semantic-category inference is authorized.

## Raw field normalization

Producer native run files expose:

- `child_module_census`
- `child_call_order`
- `child_occurrences`
- `top_module_census`
- `top_call_order`
- `top_occurrences`
- `decode_step_ms`
- `policy_receipt`
- `policy_transitions`
- `policy_transition_count`

The consumer may construct its normalized document only from these raw fields.

Producer policy transition time is `cpu_update_ns`.
Normalize as:

`api_duration_us = cpu_update_ns / 1000`

Do not mix units.

## Required real-artifact canaries

Before full consume:

1. RAW_AUTHORITY_run0
2. RAW_NATIVE_CONTROL_B8_run0
3. RAW_NATIVE_FAIR_B8_run0
4. RAW_NATIVE_FAIR_BFULL_run0
5. L0 up_proj D3 FAIR_BFULL NCU
6. L0 self_attn D3 FAIR_BFULL NCU

Canaries must close:
- exact 33,947,648 B qweight windows;
- 140 updates/run;
- BFULL hitRatio=1/28;
- token/SHA identity;
- top-level non-overlap;
- requested/actual budget;
- NCU semantic/policy identity.

## Expected independent scientific closure

Producer cross-check only:

`RESIDENCY_OFFSET_LOCALIZED`

174 must derive the label from raw evidence under the frozen pre-data decision rule.

Important causal boundary:

Supported:
- all four budgets preserve broad up_proj local benefit;
- none gives positive whole-decode benefit beyond dispersion;
- top-level decomposition explains the former residual;
- at full budget, aggregate self-attention slowdown is the largest directly measured offset component.

Not supported:
- one self-attention kernel causes the offset;
- L2 miss change uniquely causes the offset;
- DRAM traffic uniquely causes the offset.

No simulator implementation is auto-authorized.
