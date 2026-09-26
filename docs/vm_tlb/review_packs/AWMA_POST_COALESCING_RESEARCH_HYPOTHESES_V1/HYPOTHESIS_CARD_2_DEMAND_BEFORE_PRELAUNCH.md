# Hypothesis card 2: demand before resident prelaunch

Status: `DIAGNOSTIC_HYPOTHESIS`, not yet a qualified new mechanism.

## Problem

The frozen source scans resident accessq entries for translation prelaunch
before executing the accessq-head translation path. Both use the same finite
per-SID controller/L1-TLB port. A non-head prelaunch may therefore perturb a
head demand even when both are non-speculative requests from resident work.

## Existing ability

- the accepted frontend already preserves results and applies them exactly
  once;
- the TLB enforces its existing one-port-per-cycle configuration;
- Lane B will provide the reasonable warp-level grouping baseline;
- the cache path independently checks data-port/bank/interconnect admission.

## Explicit remaining difference

The fixed rule changes only same-cycle arbitration among already eligible
translation requests: accessq-head demand precedes resident non-head
prelaunch, and prelaunch uses otherwise idle capacity. It does not classify
warps as compute/memory, monitor generic LSU pressure, suppress completion
bursts, or create speculative translation work.

gem5 Vega uses a coalescing window, finite probes per cycle, and downstream
backpressure, but its reviewed source does not use the AWMA dynamic
instruction's accessq-head status for this arbitration. RPAWS is a warp issue
scheduler using instruction type and global busy signals. Generic
demand-over-prefetch priority is a well-known design principle, so even a
positive result would not by itself establish novelty. LATPC's exact
prefetch/demand arbitration is unknown without full text.

## Online information

- whether a request is the current accessq-head demand;
- whether it is a resident non-head prelaunch;
- baseline eligibility and arrival order;
- the existing finite port count.

No completion prediction, future trace event, cache oracle, or added port is
used.

## Fixed finite rule prepared by the fixture

For the existing single port, choose an eligible head demand first. If none
exists, choose the oldest eligible resident prelaunch. Preserve deterministic
order among ties. Never cancel already-issued service.

## Possible cost

- lost translation/data overlap for later accessq entries;
- delayed TLB misses or PTWs for non-head groups;
- no improvement when prelaunch never collides with head demand;
- conventional rather than publishable design differentiation.

## Minimum counterexample

If a resident prelaunch is the only eligible request, it still receives the
port. An ineligible head request does not block eligible work. Zero ports means
zero grants; the rule never invents capacity.

## Required metrics

- cycles with simultaneous eligible head demand and non-head prelaunch;
- head-demand L1-port denials attributable to same-cycle prelaunch;
- prelaunches displaced into idle slots and added delay;
- translation-ready, address-apply, and cache-admission timestamps;
- physical L1/L2/MSHR/PTW work and downstream pressure;
- target cycles/progress and all correctness/quiescence gates.

## Falsification

Reject H2 if:

- Lane B has no resident-prelaunch/head collision;
- source-backed accounting shows prelaunch cannot deny the head request;
- demand-first does not reduce head translation delay;
- lost overlap offsets the response on all preregistered targets;
- the only differentiator is generic pressure-aware scheduling or a completion
  burst already covered by RPAWS/MASK.

## Development gate

H2 is not eligible for performance replay until Lane B reports a nonzero,
source-attributed collision count and CAC/LATPC uncertainty is shown not to
control the claimed distinction. It may remain only a matched diagnostic.
