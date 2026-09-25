# Pre-L1 request-coalescing opportunity contract

Status: **FROZEN BEFORE PHASE-A RUNS**

## Physical launch

`translate()` calls, retries, coverage admissions, port-denied attempts and
lookups already registered in an MSHR are not physical launches. A physical
launch is counted only after the per-SID L1-TLB port is granted and immediately
before a new `lookup_operation` enters the accepted translation controller.
Consequently `awma_prel1_physical_launches` conserves with
`vm_l1_tlb_lookup_launches`, not with `vm_translation_lookup_requests`.

The downstream stages remain distinct:

- L1 probe: the admitted lookup's first physical service;
- L2 probe: recorded only when the accepted L2 port launches;
- existing-MSHR handling: recorded only when `allocate_or_merge()` registers
  the physical requester as a waiter on an already live MSHR;
- PTW: the accepted MSHR/PWQ/walker path, unchanged by Phase A.

## Identity and scope

The observer models a small coalescer immediately before each per-SID L1 TLB.
The table is therefore per SID. Its exact key is:

`(ASID, VPN, page_size, translation_generation, translation_access)`.

SID selects the local table and is not discarded. Offset and request size do
not change the accepted page translation after the existing cross-page check;
they are not keys. No VPN-only or cross-generation matching is allowed.

## Classification

Each admitted physical launch receives exactly one launch-time class:

- `UNIQUE`: no prior equal identity has launched or completed;
- `SAME_CYCLE_DUPLICATE`: an equal launch remains live from the same cycle;
- `INFLIGHT_DUPLICATE`: an equal earlier-cycle launch remains live;
- `POST_COMPLETION_REPEAT`: no equal launch is live, but one completed earlier.

If a request is later registered on an existing global MSHR, its final
disjoint accounting class is `EXISTING_MSHR_HANDLED`. This can overlap a
per-SID launch-time `UNIQUE` or `POST_COMPLETION_REPEAT` when the existing MSHR
leader came from another SID. Raw launch-time classes and MSHR-overlap counters
are both retained; final conservation subtracts every overlap exactly once.

## Timing-risk observation

For each raw same-cycle/inflight pair, Phase A records actual baseline leader
and follower launch/completion cycles. The offline result separates
leader-no-later from leader-later cases. Completion information is never used
for an online decision.

## Finite capacity

Four observational per-SID tables run in parallel at capacities 1/2/4/8.
Allocation uses the first invalid entry. Live entries are never evicted. A
full table passes the request through baseline and records a full event.
Entries release only at the natural physical completion of their leader.

The prototype capacity is the smallest of 1/2/4/8 whose legal merge count is
exactly equal to capacity 8 on every development target. No performance result
or approximate coverage threshold participates in selection.
