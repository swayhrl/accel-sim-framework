# Single-target large-job aging V1 — CPU-qualified candidate, not applied

Purpose: keep the finite35-input campaign from indefinitely refilling with small
jobs while an eligible large input remains unstarted. This is a scheduling policy,
not a workload/performance selection rule. It never lowers registered peaks,
hardcaps, memory floors or candidate charges; it never pauses a model or edits a
claim/spec/scientific ledger.

The implementation follows B's reviewed
`agents/B/LARGE_JOB_AGING_RESERVATION_PROPOSAL_V1.txt` with the owner's additional
stale-witness and no-double-reservation safeguards.

## Target and feasibility

At most one target exists. An eligible DH-P0 with full unchanged cost>=8GiB must
have waited>=30min from the immutable broad qualification/registration witness,
not spec mtime or retry time. Prefer a program never started in this request,
then oldest first eligibility, then stable input/cohort identity. An input already
live or claimed does not acquire a second reservation. A target already fitting
is offered first through the existing original gates; no extra model owner exists.

Before restricting ordinary backfill, compute conservative own-drain feasibility:

`C_after_drain = current_budget + 0.88×fresh_own_anonPSS − (effective_total_growth − removable_own_effective_future)`.

Only actual own live generations with recent anonymous PSS can be removed. Peer,
foreign, unobserved claim and uncertain-generation forecasts remain reserved.
Uncached own rows also remain retained; partial valid witnesses may prove
feasibility, but never pretend unknown PSS equals RSS. If own-drain cannot prove
the target fits, release the virtual fence and continue ordinary safe fits.
Record whether evidence is incomplete or the full observed own-drain is insufficient.
No external release or job interruption is assumed.

##75/25 credit

For an actual natural exit observed after target arming, use its last recent
anonymous-PSS and **effective** future-growth witness:

`estimated_release = last_effective_future + floor(0.88×last_anonPSS)`.

The PSS's original sampling time and last-live observation must both be<=60s old
when the native closure is first observed. Stale witnesses give no credit. Source
PSS is clamped to current observed RSS when heap shrink is observed. This release
quantity is explicitly an operational estimate, not exact deallocation causality.

Protect75% only after the natural completion has strict accepted archive/native
restore evidence. Clip realizable credit to actual positive growth of
`C = exact_provider_budget − effective_committed_growth`. Positive changes of
padding discount are subtracted **per cohort**, preventing a simultaneously
disappearing discount from hiding a new padding expansion. External free or heap
shrink without a natural completion earns0. Simultaneous effects cannot be causally
separated perfectly; both the own-release estimate and actual positive-C bound
apply, and no exact attribution claim is made.

If native DONE precedes strict/archive acceptance, observed positive release can
be recorded as an unprotected pending token. It is not R yet. Intervening negative-C
movement/new claims consume those tokens before later acceptance. No earlier
unattributed external capacity is banked as a future completion. A UUID is credited
at most once. Saved protected credit is capped at the target's full original cost.

Normal backfill requires original gates plus `C−full_candidate_cost >= virtual_R`.
Offer the target first when its full cost fits, then safe ordinary backfill if
the original provider defers it. A zero-start defer retains saved credit; no blind
timeout repeatedly discards the reservation.

## Claims and uncertain spent identities

When the exact provider already fully includes the target's claim/unknown future
cost, virtual_R becomes0: that real accounting already carries its reservation.
Saved credit remains visible for a later zero-start claim withdrawal. This avoids
double-reserving a whole target plus R and unnecessarily blocking other legal work.
If full accounting cannot be proved, retain the virtual fence.

The target stays visible while claimed or spent-but-unobserved and is never
resubmitted. Clear it only when the legitimate actual model generation is observed
or an authoritative terminal execution receipt closes the identity. A failed
terminal receipt is not scientific acceptance and earns no completion-release
credit; its scientific negative remains in the existing ledger.

## Padding integration and owner installation

`RuntimeFrames` calls the existing post-padding provider. B's
`effective_own_rows(snapshot)` supplies `basefuture−real_discount+claim_topup`;
the preserved base list is never mistaken for effective growth. Source claims
are not altered. Anonymous PSS collection is cached30s (configurable30–60s), not
repeated on every chooser call. Every prospective dispatch is rechecked against
current consumed/claim state; backfill margin is checked again before return.
The actual original chooser and native prepare retain all CPU, disk, pressure,
four-preexec and full-cost gates.

Proposed main-owner-only wiring, **not executed by Agent E**:

```python
frames = RuntimeFrames(ROOT, engine, res, consumer, B_module.effective_own_rows)
guard = AgingChooser(res.choose_dispatch, frames, journal=operational_journal)
guard.install(res, frames.assert_owner)
# Restore exactly the previously wrapped chooser, without touching models/claims:
# guard.restore(frames.assert_owner)
```

The new outer wrapper must be installed after B's padding/consistent/affinity
wrappers, retaining their callable as `original`. The installer asserts the same
existing main-thread owner PID/start/lease through the approved owner callback;
no new dispatcher, executor or background owner is created. Main must pin module,
adapter and policy SHA, preserve frozen tools, and record the actual activation.

`large_job_aging.py` is the state machine/instance wrapper;
`aging_runtime_frames.py` is the read-only frame adapter. `qualify_aging.py` uses
synthetic isolated claims and filesystem plus the real D accepted-result schema
and actual B effective-row helper. All synthetic inputs are marked CPU-only;
no native launcher or signal API is invoked. This candidate cannot guarantee a
completion order or ETA; its final admission is always the original provider's.
