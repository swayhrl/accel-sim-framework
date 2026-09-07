# C10 implementation requirements — not implemented by C9

状态：`FUTURE_AUTHORIZATION_REQUIRED`。本文件限定将来受控实现的最小 delta；C9 没有修改
Core、config、测试、binary 或 simulator。

## Required replacement of current shortcuts

| Current frozen shortcut | Required C10 replacement | Non-negotiable invariant |
| --- | --- | --- |
| `weight_segment_map` stores `start,end` and returns `vpn` | context-tagged local descriptor table with v1 fields and `pa_base_ppn + (vpn-va_base_vpn)` arithmetic | Segment output is real non-identity-capable PA/PPN. |
| normal mapper/PTE backend uses identity-like PPN | opt-in registered physical mapping backend shared by ordinary L1/L2/PTW and Segment | L1/PTE and Segment translations agree for all registered pages. Standard historical backend remains unchanged when C10 mode is off. |
| `OBJECT_WEIGHT` gates Segment hit | privileged-registration artifact / driver-model install state gates only by ASID+descriptor range+rights+epoch | object map remains telemetry-only. |
| global vector/no Segment port | 35 local replica tables, 8 total descriptors for one provisioned ASID/table, one accepted lookup/cycle/table | local Segment admission locksteps with local L1 admission. |
| wait-both L1+Segment completion | explicit `HIT_FIRST / MISS_JOIN` join token and terminal owner state | L1 hit can finish before Segment; L2 launch occurs only after both misses. |
| current 768-group subentry candidate | 16-way, 64KiB `G=96` standalone profile and `G=32` charged-combined profile | no C10 profile calls 768 groups equal-cost. |
| generic PWC as free 128-entry vector | separately labeled C9 physical-accounting PWC configuration for F5 | no raw PWC entry-count fairness claim. |

## Interfaces and configuration

Names below are requirements, not an instruction to preserve a particular CLI spelling. C10 must make
the values visible in the run manifest and telemetry:

| Interface | Required value/behavior |
| --- | --- |
| Segment registration input | versioned driver-owned artifact with ASID, epoch, full-page VA base/limit, PA base PPN, read-only, mapping class, and registration outcome. It is not an object map. |
| physical mapping backend | exposes PPN for registered non-identity pages to normal PTW/L1/L2 fills; rejects mapping inconsistency. |
| local table config | explicit enabled flag, `descriptors_total=8`, `provisioned_asids=1`, local-table placement, ASID=16 bits, epoch=16 bits and PA=49 bits. |
| Segment timing config | `Lseg` parameter with required 5/10/20 sensitivity profiles and one accepted request/cycle/local table. |
| ordering config | fixed v1 `HIT_FIRST_MISS_JOIN`; no selectable legacy wait-both default in architecture profiles. |
| lifecycle events | install, install-ack, revoke, revoke-ack, ASID generation update, admission failure and fallback reason. |
| sub-entry config | explicit `groups=96` standalone or `groups=32` combined, 16-way, 16 leaves/group, 64KiB-only and C9 accounting profile identifier. |
| fairness config | arm ID F0--F9, charged-bit formula/value, Segment replicas, exact/group/PWC capacities and page-policy class. |
| PWC F5 config | level-partitioned 40/40/40 entries, pointer-payload accounting and explicit port/queue/timing model; legacy PWC remains a separate standard-mode profile. |

The C10 parser must reject descriptors that overlap within an ASID, have an invalid epoch/class/rights,
contain a non-contiguous VPN-to-PPN run, include partial admitted pages, exceed capacity, or disagree
with the registered physical mapping backend. Rejection must be atomic conventional fallback.

## Required state and timing model

### Segment state

- a local descriptor table per translation cluster, keyed by ASID and containing exactly the C9 v1
  descriptor fields; local tables must have identical acknowledged content within an epoch;
- a per-ASID driver epoch / invalidation generation and install/revoke acknowledgement tracking;
- a per-request join token with independent L1/Segment result state, `l2_not_issued`, terminal owner,
  mapping/permission audit fields, and exactly-once completion guard;
- one local Segment port consumed at the same admission event as the existing one-port L1 lookup;
- no nominal Segment queue in v1. If C10 cannot uphold this contract, it must stop and request a new
  architecture decision rather than hiding a queue in the 10-cycle latency.

### Sub-entry state

- 16-way group array with `G=96` or `G=32`; PLRU state has 15 bits/set;
- group `{valid, ASID, base_VPN}` and 16 leaves `{valid, PPN, Q}`; no object attribution field in
  lookup/fill/replacement state;
- ASID generation captured by all fill transactions; leaf/group invalidation wins against a stale fill;
- distinct tag/leaf hit, existing-group fill, new-group fill, group-eviction and valid-leaf-eviction
  counters; 2MiB is rejected by this v1 profile.

### Timing and pressure telemetry

C10 must carry `Lseg` and `Qsegment` separately. It must record L1/L2 ports and queues, Segment accepts
and denials, join state duration, L2 launch guard, MSHR/PWQ/walker/PWC/PTE waits and requester latency.
No performance report may collapse these to only miss rates.

## Directed tests required before any replay

| Test family | Minimum directed cases |
| --- | --- |
| real PA mapping | non-identity PA base; multiple virtual pages; PA offset arithmetic; two physical extents; request boundary/page-cross rejection; ordinary PTE result matches Segment PA. |
| registration/provenance | no object map but valid descriptor hit; object-labelled VA without descriptor miss; ASID mismatch; RW/store/atomic rejection; overlap/capacity/pin/class failure gives atomic conventional fallback. |
| lifecycle | install visibility only after all local acks; revoke before remap/free; epoch mismatch; stale fill after shootdown; context switch; ASID reuse after ack; model unload. |
| ordering | Segment-first hit; L1-first hit with slow Segment; L1-miss/Segment-hit blocks L2; Segment-miss/L1-hit blocks L2; both miss launches one L2; dual-hit equal PA; injected mismatch faults; no duplicate side effect. |
| throughput | same-cycle requests to different local clusters both accepted; one local request/cycle accepted; second same-cycle local request observes explicit L1 admission backpressure; no hidden Segment queue in v1. |
| latency sensitivity | 5/10/20 Segment points; L1 hit completion is independent of delayed Segment; miss-join and lower-path counters remain conserved. |
| sub-entry accounting | `B_exact=66,000`; `G=96` fits; `G=112` rejects; historical 768 groups not an equal-cost arm; combined `G=32` after 37,800 Segment bits. |
| sub-entry semantics | base-tag/leaf hit, invalid selected leaf, existing-group fill, group replacement, leaf/group invalidation, ASID mismatch, stale fill race, 2MiB reject. |
| fair alternatives | F2/F4/F5/F6/F7/F8 manifest bits/capacities match C9 formula; PWC pointer payload/port accounting is exposed. |

## Regression and evidence obligations

1. Standard L2 exact mode, ordinary 64KiB and standard 2MiB behavior must retain all C0 M1--M3 and
   M4C regression invariants. C10 may not change the historical standard identity backend when the new
   architecture mode is disabled.
2. The prior C2/C3 directed tests remain useful historical semantic coverage but must be updated with
   real PA and `HIT_FIRST / MISS_JOIN` cases. A passing old wait-both result does not validate C10.
3. C4/C7 artifacts stay immutable historical `SPECULATIVE_CANDIDATE` evidence. They must not be
   relabeled as post-C10 performance results or compared numerically to a new mapping model.
4. Before any bounded or full replay, create a fresh binary/runtime provenance record, run all directed
   tests, prove standard-mode compatibility, and verify fairness manifest fields. A separate later
   authorization is still required for C5 and host resource policy remains in force.

## Stop conditions for a future implementer

Do not improvise an indirect mapping, a shared queue, dynamic migration, a different associativity,
unaccounted descriptor replicas, arbitrary page-size support, or a performance-oriented latency value.
If v1's fixed mapping/registration/topology/order/budget contract cannot be realized while retaining
standard mode and the directed invariants, stop and request a new architecture decision.
