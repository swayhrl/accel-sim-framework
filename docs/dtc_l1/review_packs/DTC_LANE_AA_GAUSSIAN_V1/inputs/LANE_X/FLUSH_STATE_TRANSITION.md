# Source events and state conservation

Status: `SCIENTIFIC_STOP`; the DTC transitions below are requirements for a
future implementation, not executed code or a correctness proof.

All line numbers refer to frozen Core
`6fba0136f8465b59fe5858a950fa39efb265f654`; Lane X changes documentation only.

## Actual ordinary source events

| Request source | Existing predicate | Scope and ordering |
| --- | --- | --- |
| `gpu-sim.cc:2515-2527` | CORE tick; `gpgpu_flush_l1_cache`; cluster `get_not_completed()==0` | After `issue_block2core()` and latency decrement, independently per cluster; can repeat; not one kernel-end callback |
| `shader.cc:6877-6888` | Warp has MEMBAR, its scoreboard has no pending writes, existing `flush_l1()` | Clears that warp's MEMBAR and requests its core's invalidation; other warps/cores need not be drained |
| `gpu-sim.cc:1749-1754` | Cache preference differs from current status | All clusters, before configuration update; no flush-option predicate at this caller |

`shader.h:3005,3447-3448` defines core `get_not_completed()` as its thread count;
`shader.cc:7471-7475` sums that count within a cluster. Neither is an event ID or
a once-per-kernel guard. Actual occurrence counts for particular benchmarks are
unmeasured here.

The shared chain is cluster/core `cache_invalidate()` ->
`ldst_unit::invalidate()` (`shader.cc:4012-4015`) ->
`baseline_cache::invalidate()` (`gpu-cache.cc:1268-1279`). The last function
records `m_invalidate_pending=true` and tries to retire it.

`retire_pending_invalidate()` (`gpu-cache.cc:1281-1286`) commits only when
`!conventional_miss_lifecycle_active()`. That predicate requires an empty
miss queue, extra-fields map and MSHRs (`gpu-cache.h:1474-1478`).
`baseline_cache::cycle()` retries retirement (`gpu-cache.cc:1249-1265`).
`tag_array::invalidate()` (`gpu-cache.cc:478-487`) also returns early if unused.
Thus a source request, a deferred commit attempt and a meaningful valid-Tag
transition are distinguishable. A future contract must identify which one
defines the DTC event, including the unused-conventional-cache case.

## Existing time model

The ordinary invalidation loop adds no explicit simulated invalidation latency,
bandwidth quota or SM stall. Conventional busy state can postpone its commit by
an unbounded-in-advance number of existing cycles. The MEMBAR comment mentioning
a possible 5k-cycle stall is a TODO, not implemented timing. No fixed delay or
drain is added here. No zero-time or nonzero-time K1 model has been implemented
or approved by this STOP. In particular, clearing DTC at the request call does
not automatically reproduce the conventional deferred-commit timing.

## Required OO conservation at an approved event

For each visible mapping `(logical line, phys_id, generation)`, a future lookup
invalidation must clear only the mapping and that physical generation's
`tag_valid`. It must preserve allocated bytes/state while consumers own Refs.

| State after visibility loss | Required lifetime |
| --- | --- |
| Ref > 0, lower request queued/in flight, sectors incomplete | Retain physical generation, owner request UID, expected/received sector masks, waiters, pending dependencies, lower credit, service state and all PIB references |
| Ref > 0, response complete but finite metadata wakeup unfinished | Retain physical state and service-return cursor; no premature ready or retirement |
| Ref > 0, data ready/collecting/writeback blocked | Preserve reference ownership through successful existing retirement |
| Ref == 0, no remaining request/service owner | Reclaim exactly once under existing rules; record visibility-loss time consistently with finite-service map-loss accounting |
| Re-access to invalidated logical address | Existing finite Tag/allocation/lower-create rules apply; a new physical generation must not alias the retained generation or consume its reply |

The shadow Ref sum must equal live PIB references for each physical generation.
Allocated + free must equal physical capacity. Every unmapped allocation must
have an explicit retained owner or be reclaimable. Lower acquire minus release
must equal outstanding requests. All sector fragments must complete exactly
once before their existing owner/credit is released. Repeated events must not
double-reclaim or replace the first map-loss timestamp of a retained generation.

Existing OO replacement demonstrates part of this lifecycle in
`dtc-l1-common.h:588-604`; final-Ref release is at `:699-713` and `:731-745`.
Those paths do not implement a source-event API. Integration must additionally
preserve `shader.cc:3451-3484` response UID/sector ownership. A stale generation
must remain a hard failure; a lookup miss is not permission to drop its reply.
No new finite-service port quota, collection delay or physical resource may be
introduced to repair the event contract.

## IO and remaining scope

IO records displaced physical identities in the replacing PIB owner's
`release_on_retire` (`dtc-l1-common.h:273-279`) and releases them at FIFO retirement
(`:354-362`). It has no OO Ref Count and no general release owner for an
invalidation event when no replacing instruction exists. Do not invent a PIB
owner, add OO Ref semantics, drain the GPU, or clear every physical line.

A future common interface may accept an already-approved source event and
report invalidated/retained/reclaimed counts for supported modes. Neither IO
nor OO implements that interface in this STOP. IO's ownerless release problem
is explicitly out of scope pending a mechanism-preserving resolution. The
MODERN_OO_SECTOR frontend is also not implemented for K1. Full matrices remain
OO-only and require external Lane V contract plus Lane Y independent validation.
