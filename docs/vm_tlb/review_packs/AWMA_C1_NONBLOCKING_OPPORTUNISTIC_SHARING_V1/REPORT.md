# AWMA C1 nonblocking opportunistic sharing V1

Status: **COMPLETE / NONBLOCKING_OPPORTUNISTIC_SHARING_SUPPORTED_DEVELOPMENT**

## Frozen mechanism

`nonblocking_opportunistic_share` is opt-in and uses no cohort-size threshold.
Accepted C1 legality and owner selection are unchanged. At each member's
frozen V1 baseline translation decision point:

- READY owner: reuse the legal result and skip that member's physical lookup;
- owner not READY: permanently mark the member fallback and immediately enter
  the unchanged baseline path;
- a late owner result cannot apply to a fallback member.

Only the accessq head can consume a shared result, so delivery is a real finite
one-member-per-cycle resource. Owner and fallback work is never cancelled;
fallback duplicate lookup requests and their terminal service class are
reported explicitly. No future information, extra port, free service, or
unlimited broadcast is introduced.

## Development matrix

| target | OFF | nonblocking | cycle change | lookup suppression | READY share | fallback |
|---|---:|---:|---:|---:|---:|---:|
| T0 | 527,896 | 506,778 | -4.000% | 94.696% | 2,381,824 | 340,640 |
| T1 | 665,802 | 643,076 | -3.413% | 97.248% | 6,182,246 | 447,706 |
| T2 | 93,079 | 89,689 | -3.642% | -0.103% | 0 | 132,544 |
| SPLITKV | 73,923 | 74,361 | 0.593% | 97.708% | 204,035 | 14,827 |
| COMBINE | 10,480 | 10,484 | 0.038% | 97.356% | 942 | 74 |

All five points have zero sharing-induced owner-wait cycles and zero
sharing-induced head-block cycles. No target regresses by more than 1%; T0 and
T1 retain both substantial lookup suppression and positive performance gain.
All correctness, exactly-once, coverage, controller/candidate quiescence, and
fallback accounting gates pass. The A1 integration smoke also passes before
the development matrix.

## Cost disclosure and interpretation

Fallback is not free: the five development points launch 935,791 disclosed
duplicate physical lookup requests in total. Most complete as L1 hits; 3,337
complete as MSHR merges, so the owner is never cancelled and overlapping work
remains visible. Full per-target L1/L2/PTW service bins, total controller MSHR
merges, admissions/re-admissions, and downstream issue latency are in
`DEVELOPMENT_MATRIX.tsv`.

T2 has no READY-shared member and slightly more lookup requests than OFF, yet
is faster. Its response therefore must not be attributed to result reuse; it
is development evidence consistent with owner-prelaunch/order effects and
requires an independent causal study if used later. SPLITKV and COMBINE have
small regressions below the fixed 1% stop bound.

Owner-service bins classify results consumed by the proactive owner branch.
An owner eventually consumed by its ordinary baseline head path is not entered
in those bins; the review therefore enforces a bounded observation rather than
false equality with cohort count. Fallback service and terminal controller
accounting remain exact.

## Decision and scope

The required development criteria support freezing this mechanism and all
parameters. No tuning, threshold sweep, Fanout-4 extension, OFF rerun, or
Batch1 Pair C mechanism result was used. These five targets are development
evidence, not holdouts.

The next allowed step is to wait for the already pre-frozen cross-context
scientific holdout trace, then perform independent validation without changing
this source or its parameters. This stage does not promote a baseline and does
not make a final mechanism, novelty, or paper claim.
