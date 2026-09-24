# AWMA C1 T2 owner-wait/retry attribution V1

Stage: `AWMA_C1_T2_OWNER_WAIT_RETRY_ATTRIBUTION_V1`

Accepted parent:
`AWMA_C1_DELIVERY_BANDWIDTH_DIAGNOSTIC_V1 @
070cb2f8b1ffea431f0f8acb9ca32a0dd16a0f14`.

Frozen parent conclusion:
`DOES_NOT_SUPPORT_ONE_SLOT_DELIVERY_SERIALIZATION_AS_MAJOR_T2_CAUSE`.
No 4-slot/8-slot experiment is permitted or run.

## Question and starting evidence

This phase asks why T2 C1 reduces physical translation service but remains
1.026% slower than OFF. The prioritized explanation is dependency/order work
before delivery: member wait for owner, accessq-head blocking, repeated owner
retry, repeated downstream admission, and owner-first scheduling perturbation.

Accepted evidence already shows:

| Target | Arm | Cycles | Coverage admissions | Unique UID |
|---|---|---:|---:|---:|
| T0 | OFF | 527,896 | 3,090,304 | 3,090,304 |
| T0 | C1 | 487,624 | 3,090,304 | 3,090,304 |
| T2 | OFF | 93,079 | 715,333 | 411,008 |
| T2 | C1 | 94,034 | 832,383 | 411,008 |

Thus T2 C1 adds 117,050 logical accessq admissions over OFF, whereas T0 does
not show corresponding admission inflation.

## Frozen semantics and observational telemetry

The accepted one-slot C1 semantics, grouping key, owner selection, lookup
suppression, READY ownership, delivery bandwidth, downstream behavior,
RTX4080/V1 baseline, traces, and 10/80 overlay are unchanged.

Telemetry is gated by `GPGPUSIM_AWMA_OWNER_WAIT_DIAGNOSTICS=1` and records only
the selected kernel:

- admission count per logical UID and histogram, repeated admissions and
  readmitted UID count;
- owner translation attempts/retries per UID;
- member cycles waiting for owner readiness;
- head-block cycles split into owner-not-ready and owner-ready/delivery cases;
- owner service path: L1 hit, L2 hit, outstanding-MSHR merge, or PTW;
- cohort-size histogram;
- first owner-wait to member-delivery latency and histogram;
- first/all downstream issue latency from first accessq residency;
- pending member-wait state at termination.

No per-access log is emitted. Per-UID maps exist only as diagnostic metadata
and never participate in scheduling, arbitration, translation, completion, or
downstream issue decisions.

## Bounded execution and interpretation rule

After A1 correctness smoke, the only first-stage matrix is T0/T2 × OFF/C1.
Every telemetry arm must reproduce the accepted cycles, instruction/CTA
identity, coverage and terminal quiescence before attribution is admissible.

Owner-wait/head-blocking is considered supported only if T2's extra C1
admissions are localized to repeated logical UIDs and co-occur with C1-specific
owner-wait/head-blocking or delayed downstream issue at a materially stronger
normalized rate than the T0 control. Aggregate overlapping warp-stall counts
are not equated one-for-one with kernel cycles.

Only if that directional evidence is clear may one diagnostic
`READY_ONLY_OR_NO_WAIT_SHARE_CONTROL` be added: a member shares only when its
owner result is already READY; otherwise it follows the frozen baseline
translation path instead of waiting. Any lookup-suppression loss must be
reported, and the control is not a performance candidate.

If the telemetry does not support the hypothesis, no ablation is run and the
phase stops with the next candidate explanation.

## Results

The frozen observational matrix is terminal and reproduces every accepted
cycle/coverage result exactly. All correctness and quiescence gates pass.

| Target | Arm | Cycles | Admissions | Repeated admissions | Readmitted UIDs | Head-block cycles |
|---|---|---:|---:|---:|---:|---:|
| T0 | OFF | 527,896 | 3,090,304 | 0 | 0 | 0 |
| T0 | C1 | 487,624 | 3,090,304 | 0 | 0 | 9,021,728 |
| T2 | OFF | 93,079 | 715,333 | 304,325 | 948 | 0 |
| T2 | C1 | 94,034 | 832,383 | 421,375 | 133,263 | 2,079,258 |

T2 C1 adds the accepted 117,050 admissions entirely as repeated admissions.
The fraction of logical UIDs admitted more than once rises from 0.23% to
32.42%. T2 C1 has 132,544 size-2 cohorts, exactly 132,544 owners and 132,544
members. Every member completes an owner wait; total owner-wait latency is
1,946,714 cycles, or 14.69 cycles per member, and all 2,079,258 observed wait
cycles occur while that member is the accessq head.

Owner service in T2 is 131,489 L1 hits (99.20%), 431 L2 hits, 500 outstanding
MSHR merges and 124 PTWs. Owner retry attempts total 1,946,714, numerically
matching owner-to-member wait latency. This ties the dependency to repeated
owner observation rather than physical walk traffic.

T0 is an important control: it has more aggregate waiting and larger cohorts,
but only 2.92 head-block cycles per logical UID versus T2's 5.06, and its much
larger lookup suppression still yields a net benefit. Aggregate head-block
counts therefore are not treated as recoverable kernel cycles. Instead, the
T2-specific size-2 structure, head-resident member wait, retry/latency match,
and admission redistribution jointly support the bounded owner-wait
hypothesis.

First-issue latency changes only slightly on T2 (13.29 to 13.50 cycles per
unique UID), while all-admission latency falls because the repeat distribution
changes. This evidence does not support a generic downstream latency increase;
it localizes the intervention to owner/member ordering and head retry.

Decision after telemetry:
`TELEMETRY_SUPPORTS_READY_ONLY_OR_NO_WAIT_SHARE_CONTROL`.

Exactly one diagnostic control is therefore admitted. A head member whose
owner is not READY follows its own frozen baseline translation path and is
excluded from later sharing; a member still shares when the owner result is
already READY. The control must preserve correctness and explicitly report
lost lookup suppression. No other ablation or bandwidth sweep is authorized.

## READY-only/no-wait diagnostic control

The A1 smoke and T2 control are terminal with full logical UID coverage, zero
untranslated/unobserved, zero duplicate application, and empty
lookup/READY/MSHR/PWQ/walker/diagnostic wait state.

| T2 arm | Cycles | Admissions | Repeated admissions | Lookup requests | L1 probes | Shared deliveries | Head-block cycles |
|---|---:|---:|---:|---:|---:|---:|---:|
| OFF | 93,079 | 715,333 | 304,325 | 549,207 | 412,391 | 0 | 0 |
| accepted C1 | 94,034 | 832,383 | 421,375 | 282,838 | 279,190 | 132,544 | 2,079,258 |
| READY-only/no-wait | 89,689 | 744,542 | 333,534 | 549,775 | 412,357 | 0 | 132,544 |

All 132,544 size-2 cohort members encounter a non-READY owner and take the
baseline fallback; none receives a shared result. C1-specific head blocking
falls by 93.63%, and cycles improve by 4.62% versus accepted C1, becoming 3.64%
better than OFF. Repeated admissions fall by 87,841 versus C1, although they
remain 29,209 above OFF.

The diagnostic simultaneously loses essentially all lookup suppression:
lookup requests are 0.10% above OFF instead of 48.50% below OFF, and L1 probes
return to the OFF level. Owner work continues in parallel with fallback member
translation, so this deliberately inefficient control cannot be presented as
a candidate mechanism or resource-matched design.

## Conclusion and limits

Decision:
`SUPPORTS_OWNER_WAIT_HEAD_BLOCKING_AS_MAJOR_T2_REGRESSION_CAUSE`.

The observational evidence and the single intervention agree: T2's size-2
owner/member organization makes the member sit at the accessq head while a
mostly-L1-hit owner is repeatedly observed. Removing that wait reverses the
regression even while discarding C1's primary service-saving benefit. This is
causal support for owner-wait/head-ordering cost, not a final architecture.

No 4-slot/8-slot run, extra ablation, parameter sweep, baseline change or T0
ablation was performed. A future design would need to preserve lookup
suppression while avoiding head serialization, then receive a separate
resource/timing study and independent validation; this phase does not start
that work.

Implementation changes are limited to diagnostic requester-path propagation,
per-UID aggregate telemetry, and one per-access fallback bit used only by the
authorized control. Default OFF/C1 behavior remains unchanged. Full raw
per-access logs are not emitted; diagnostic maps are terminally checked and
excluded from architectural scheduling.
