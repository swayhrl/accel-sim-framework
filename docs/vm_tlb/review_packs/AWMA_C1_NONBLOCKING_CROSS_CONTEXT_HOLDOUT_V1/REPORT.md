# AWMA C1 nonblocking cross-context holdout V1

Status: **COMPLETE / SAFETY_ONLY_NO_SHARING_OPPORTUNITY**

## Phase 1: simulator-input and OFF qualification

Both preregistered `STR_8a5773a1d265` trace payloads match capture authority
`c8549227...` exactly and pass xz integrity, producer grammar authority,
Accel-Sim grammar consumption, identity, instruction/CTA/UID signature,
coverage, exactly-once, terminal, and controller-quiescence gates.

| target | context | step | OFF cycles | instructions | CTA | unique UID |
|---|---|---:|---:|---:|---:|---:|
| H1 | S2 | 16 | 19,578 | 10,601,472 | 224 | 102,144 |
| H2 | D128 | 96 | 19,778 | 10,601,472 | 224 | 102,144 |

The frozen candidate was not run until both independent OFF qualification
records were `PASS`.

## Phase 2: frozen candidate

| target | OFF | candidate | cycle change | lookup change | READY share | fallback |
|---|---:|---:|---:|---:|---:|---:|
| H1 | 19,578 | 19,558 | -0.102% | 0.155% more | 0 | 50,176 |
| H2 | 19,778 | 19,604 | -0.880% | 0.150% more | 0 | 50,176 |

Both candidates pass all correctness, coverage, exactly-once, terminal, and
quiescence gates. Sharing-induced owner wait and head blocking are zero, and
neither target regresses by more than 1%.

## Preregistered decision

Neither holdout point exposes an actual READY-result reuse opportunity and
neither has positive lookup suppression. Therefore this result is strictly
`SAFETY_ONLY_NO_SHARING_OPPORTUNITY`; it is **not** evidence of sharing
generalization. The small cycle improvements cannot be used as a T2-style
no-sharing mediator for a sharing claim.

The frozen source, policy, platform, frontend, and 10/80 parameters were not
changed. No OwnerOnly ablation, threshold/fanout sweep, ideal translation,
0/80 point, Pair A/B, or other target was run. Holdout results were not used to
tune the mechanism. No baseline promotion or paper-level conclusion follows.
