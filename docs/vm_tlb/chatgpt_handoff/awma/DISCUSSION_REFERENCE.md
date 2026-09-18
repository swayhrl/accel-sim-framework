# AWMA Discussion Reference — Lookup Model Validity

Date: 2026-09-18

## 1. The lookup matrix is scientifically useful, but not yet a mechanism result

The prior stage found a very large cycle response to reducing the modeled L1 TLB lookup latency.

That is important evidence of simulator sensitivity.

It is not yet evidence that a real RTX4080 can gain the same amount from a faster TLB.

Two issues must be closed first:

1. the model's lookup latency changes the time at which TLB residency is observed;
2. the baseline 10/80 cycle values may be generic project timing assumptions rather than hardware-calibrated values.

## 2. Why L2 gets worse when made faster

The current controller does not determine hit/miss at launch and then delay only the response.

Instead:

```text
launch at cycle t
wait configured latency
probe TLB state at t + latency
```

Suppose another request fills the same translation at t+30.

Then an 80-cycle lookup can probe at t+80 and hit.

A 0- or 40-cycle lookup can probe before the fill and miss.

Therefore:

```text
shorter lookup latency
!=
same hit/miss stream with fewer waiting cycles
```

This directly explains why L2 misses increase when L2 latency is shortened.

It may also contribute to the changing L1 request stream.

## 3. Why zero/zero can beat I0

I0 bypasses the TLB hierarchy entirely.

Zero/zero still executes the normal translation state machine, port/arbitration/fill/retry logic, but all lookup service intervals are zero.

Those two paths create different timing/order in the lower memory system.

Therefore 0/0 being 17011 cycles faster than I0 is not evidence that a real zero-cycle TLB is better than no translation.

It is evidence that the full simulator is timing-coupled and that counterfactual paths can perturb cache/memory scheduling differently.

## 4. The 10-cycle L1 value needs provenance

The source history that introduced the lookup timing calls 10 and 80:

```text
generic M3 ... lookup service cycles
```

That wording matters.

If there is no separate calibration receipt, the correct claim is:

> Q05 is highly sensitive to the lookup timing parameter in the accepted model.

The incorrect claim would be:

> RTX4080 spends ten hardware cycles on every L1 TLB hit and a five-cycle design therefore gives the measured speedup.

The next stage searches the project evidence before deciding which statement is supportable.

## 5. What read-only fill-race telemetry will tell us

For every lookup, observe TLB residency at launch without touching state, then compare with the real probe at service completion.

The important transition is:

`launch miss -> completion hit`

This directly counts lookups whose result benefits from a translation fill arriving during the modeled service interval.

If this class is common, the lookup-latency sweep is strongly coupled to fill timing.

## 6. Invocation accounting also matters

The simulator repeatedly calls translation while a request is pending.

Existing source distinguishes:

- new lookup;
- in-flight lookup bypass/retry;
- existing MSHR waiter bypass;
- ready/completion retry.

These are not independent memory transactions.

The next stage must reconcile these units before interpreting changing lookup counts.

## 7. Global versus local memory may matter

Q05 contains both global and substantial local-memory activity.

Local memory is mapped into the global timing address space using SM/thread placement.

If lookup timing changes CTA/warp timing enough to change local-memory transaction behavior, some lookup-count variation may come from this path.

The next stage therefore asks for per-space translation accounting rather than treating every VM request as homogeneous.

## 8. Calibration should be a separate future GPU task

Published GPU microbenchmark work is useful for methodology and for showing that TLB hierarchy/reach can be reverse-engineered, but older architectures and end-to-end memory plateaus do not directly calibrate Ada/RTX4080 pure lookup latency.

Therefore the current stage only writes an RTX4080 calibration plan.

A future user-approved 109 run can execute it without mixing that hardware-calibration work into simulator-model debugging.

## 9. Decision gate after this stage

Only after model validity closes should the project choose among:

- keep the current model for qualitative screening only;
- calibrate lookup timing on RTX4080 before quantitative claims;
- revise lookup timing semantics;
- proceed to a mechanism study with a parameter envelope rather than one assumed latency.

No mechanism is chosen yet.
