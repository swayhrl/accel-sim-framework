# Eager source-request transition and ownership contract

Current Core: `c0a5e2c31e407c57e3a4af3ce529c921e8059a05`.
Authority: user ruling of 2026-10-18 and Lane V
`26abd496417d9392245052e54fbd9ba27c6ffd96`.
Status: `OO_IMPLEMENTED_LOCAL_CPU_CHECKS_ONLY_LANE_Y_PENDING`.

## Events and ordering

| Source | Preserved condition and scope |
| --- | --- |
| IDLE_CLUSTER | CORE tick after CTA issue/latency decrement; original flush flag and this cluster's not_completed==0; all cores of that cluster; repeatable |
| MEMBAR | Warp MEMBAR and no scoreboard pendingWrites; clear MEMBAR and original flush_l1 condition; this core |
| CACHE_CONFIG_CHANGE | Requested cache status differs; all clusters before original config update; independent of flush_l1 flag |

No kernel ID/unique completion condition is invented. Core/cluster forwards the
source label to the same LD/ST request entry. True kernel completion, stores,
atomics, bypass, PROXY_FENCE and `flush()` gain no new DTC call.

Within the existing source call, C++ execution order defines:

1. Sample finite occupancy up to the request edge, without advancing service.
2. Count/source-label the request and revoke all currently visible OO mappings;
   update physical tag_valid and one map-loss timestamp per such generation.
3. Retain all live-Ref generations, or reclaim finished Ref0 generations once.
4. Record source-request phase/order/cycle and DTC changed/retained/reclaimed.
5. Invoke the original ordinary invalidate exactly once. Its original pending
   and conventional drain logic either commits immediately or remains pending.
6. Record ordinary immediate commit on return if pending cleared. Otherwise
   observe the original ordinary cycle call and record its pending-to-clear
   commit separately when it occurs. Several source requests may map to one
   ordinary pending retirement; their first/last request sequence is recorded.

The observer inherits cache code and only reads the protected pending bit;
ordinary `gpu-cache.cc/h` are unchanged. A commit count means the ordinary
retirement executed Tag invalidate; an unused Tag array may no-op. It is not a
count of actual ordinary valid mappings changed. Both branches' commit times
are not assumed equal. Detailed logs are bounded by the existing debug limit;
summary counts/first-last cycles and omitted-record count are always explicit
for K1. No complete event trace is claimed with a truncated log.

## Time model

DTC directory invalidation is an atomic logical visibility operation at the
source request with zero additional simulated-cycle latency and no new port
quota. There is no hidden GPU drain, delay or hardware PPA claim. It changes no
clock, finite-service grant, lower bandwidth, retire width, PIB or physical
capacity. The source request may occur after the last service edge: immediate
map-loss/free accounting therefore receives the explicit source cycle. A
separate occupancy-observation timestamp avoids losing the pre-free interval
without replenishing or advancing any service. K0 samples at its original edges.

Grant-only finite Tag state records a cycle, not an identity. If E intervenes
before access commits, access consults the revoked directory. References already
accepted keep their saved identity; partial instructions retain accepted lines
while their remaining references follow later lookups. The original next_reference
and completion ledger paths are unchanged. Same-cycle ordering follows actual
host call order, including core source requests relative to response/retire.

## State conservation

| Before E | At E | Later |
| --- | --- | --- |
| Visible, ready, Ref0, no service/waiter | Hide Tag; tag_valid=false; map-loss once; free immediately | Later allocation increments generation |
| Visible, pending lower/sector return, Ref>0 | Hide Tag; retain identity/generation/Ref/PIB/waiters and all external queues/masks | Original saved identity receives all sectors; no Tag resurrection |
| Visible, finite return queued or partly updated | Hide Tag; retain cursor, pending dependencies and all refs | Existing metadata width finishes readiness; no service advance at E |
| Ready with live consumer or collection/WB blocked | Hide Tag; retain allocation/Ref and collection state | Existing successful WB/retire decrements final Ref and frees once |
| Already hidden old generation | No state or map-loss change | Continues original owner lifecycle |
| Post-E same-address lookup | Old identity cannot be found by Tag | Allocate legal new identity or backpressure; old/new may coexist |

For each physical generation, Ref shadow equals live PIB references. Natural
pending lower/return/service/collection owners retain consumer Refs; invalidation
does not disturb this premise. Immediate free asserts ready/no waiter/no queued
service-return owner. No generation increment occurs on E. Finite map-loss is
inserted only for a visible mapping, so repeated E cannot overwrite the first
loss time. Existing retirement reclaims at final Ref with no queue deletion.

Physical allocated+free capacity, exact sector acceptance and lower acquire/
release conservation remain the original mechanisms. The unchanged actual
response path routes by saved UID/physical/generation, not by address lookup.
Invalid generation and duplicate/invalid sector invariants remain hard errors.
Local tests cover frontend identities and the production sector predicate;
actual LD/ST/collector integration and architectural values require Lane Y.

## Scope boundaries

OO only. IO has no independent orphan/release owner; value1 fails with
`IO_K1_UNIMPLEMENTED_STOP`, rather than creating an owner, fake instruction or
OO references. Modern/Base/LEGACY value1 are rejected and their value0 paths
remain supported. Disabled ordinary L1D and the external-cache constructor are
not supported K1 combinations. No data payload/coherence/write-after-read,
all-ISA or hardware timing correctness is inferred from lifetime balance.
