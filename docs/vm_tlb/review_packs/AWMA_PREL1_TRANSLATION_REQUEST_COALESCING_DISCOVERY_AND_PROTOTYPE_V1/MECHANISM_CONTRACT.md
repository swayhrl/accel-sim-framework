# PREL1_EXACT_TRANSLATION_REQUEST_COALESCER contract

Status: **FIXED FOR DIRECTED AND ZERO-DUPLICATION VALIDATION**

## Placement and identity

The mechanism compares a request immediately before its frozen per-SID L1 TLB
port launch. It is consulted only on a cycle where frozen V1 has an available
L1 port; a port-denied retry is not converted into an artificial merge.

Each SID owns two entries. Capacity 2 is selected by the preregistered Phase-A
rule: it is the smallest capacity with counts exactly equal to capacity 8 on
all seven development targets. The key is exact
`(ASID, VPN, page_size, translation_generation, translation_access)`.

## Leader and follower

A leader is only a frozen-V1 request that actually receives the L1 port and
launches a normal physical lookup. There is no proactive request, owner
selection, future information or speculative service.

If an exact live leader exists, the current baseline-eligible physical request
registers as a follower and launches no second L1 lookup. The leader continues
through the unmodified L1/L2/MSHR/PWQ/PTW path. Its natural result is retained
until every registered follower consumes it at that follower's normal
translation decision point. Consumption is exactly once.

Entries are never live-replaced. An entry-full request uses baseline. Once the
leader is READY the entry stops accepting followers; it remains finite state
until existing followers drain. There is no result forwarding between
completed, unrelated requests and no second-TLB semantics.

## Waiter bound

The accepted controller stores MSHR waiters in a software vector and has no
independent finite waiter-count parameter. The prototype therefore adds an
explicit bound of **32 followers per entry**, matching both the frozen
translation-MSHR entry scale and the source warp-width request scale. It is a
source-supported engineering bound, not selected from performance results.
Waiter overflow always uses the baseline physical path.

## Timing

The development model uses a same-cycle two-entry exact-key compare in
parallel with the current pre-L1 request decision:

`SIMULATOR_TIMING_ASSUMPTION_SAME_CYCLE_COMPARE`.

This is a simulator timing assumption, not free hardware. A conservative
`+1-cycle` comparison is preregistered and changes no capacity, identity,
waiter bound or service semantics. It is run only if the main candidate
survives the development matrix.

## Causal control

`GPGPUSIM_AWMA_PREL1_CONTROL=grouping_only` executes the same lookup,
leader/follower grouping and bounded bookkeeping, but every grouped follower
still launches its frozen baseline translation request and never consumes the
leader result. It is a diagnostic comparator, not a candidate.

## Required accounting

The mechanism reports leaders, followers, same-cycle/inflight merges,
entry/waiter-full fallbacks, leader service source, follower wait and delivery
latencies, head-block cycles, critical-path exposure, occupancy/waiter HWM and
complete terminal state. Physical service suppression is established only by
comparative L1 launches/probes and downstream L2/MSHR/PTW counts.
