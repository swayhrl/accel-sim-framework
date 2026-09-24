# AWMA C1 opportunity portability Pair A V1

Status: **COMPLETE / GEMV_NO_READY_REUSE_ACROSS_CONTEXT_OBSERVED**

## Phase 1: simulator-input and OFF qualification

Both existing `STR_8bc741e5debc` trace payloads match capture authority
`c8549227...` exactly and pass xz integrity, producer grammar authority,
Accel-Sim grammar consumption, identity, instruction/CTA/UID signature,
coverage, exactly-once, terminal, and controller-quiescence gates.

| target | context | step | OFF cycles | instructions | CTA | unique UID |
|---|---|---:|---:|---:|---:|---:|
| A1 | S2/T2048 | 16 | 114,123 | 34,883,072 | 224 | 409,024 |
| A2 | T8192 | 16 | 117,698 | 34,883,072 | 224 | 409,024 |

The frozen candidate was not run until both independent OFF qualification
records were `PASS`.

## Phase 2: frozen candidate

| target | OFF | candidate | cycle change | READY share | fallback | admission change |
|---|---:|---:|---:|---:|---:|---:|
| A1 | 114,123 | 112,023 | -1.840% | 0 | 116,032 | 3.503% |
| A2 | 117,698 | 125,427 | 6.567% | 0 | 116,032 | 46.299% |

Both candidates pass all correctness, coverage, exactly-once, terminal, and
quiescence gates. Sharing-induced owner wait and head blocking are zero.

## Opportunity portability result

Both exact-kernel contexts expose zero READY-shared members. The registered
result is therefore `GEMV_NO_READY_REUSE_ACROSS_CONTEXT_OBSERVED`: READY-result
reuse opportunity is stably absent across S2/T2048 and T8192 for this exact
GEMV identity.

The performance response is nevertheless context dependent. A1 improves by
1.840%, while A2 regresses by
6.567%. A2 candidate admissions increase by
46.299% versus OFF, reaching 3,475,971 with
3,066,947 repeated admissions. A1's admission increase is only
3.503%. The candidate all-issue latency
totals also differ (A1 8,166,151,720; A2 6,829,438,283), but are retained as
observational timing rather than an additive decomposition. Since
READY reuse is zero on both sides, this divergence is attributed only as a
context-dependent owner/prelaunch/order and retry response, not sharing value.

## Scope

This is `CONTEXT_LENGTH_OPPORTUNITY_CHARACTERIZATION`, not a holdout or
mechanism promotion. The result does not authorize a mechanism change.

The frozen source, policy, platform, frontend, and 10/80 parameters were not
changed, and no target outside Pair A was run. No tuning, baseline promotion,
or paper-level conclusion follows.
