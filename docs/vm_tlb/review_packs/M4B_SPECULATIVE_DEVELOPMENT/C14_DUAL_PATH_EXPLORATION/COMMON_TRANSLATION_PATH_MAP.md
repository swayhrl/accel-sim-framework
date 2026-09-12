# C14 common translation-path map

Status: `SOURCE_VERIFIED_FACT`  
Core anchor: `swayhrl/gpgpu-sim@57bb71ecd015b6ec0ab32e45b0815e5beaf69172`  
Audit scope: C12 exact-translation and Weight-Segment source only; no C13 source
or output was modified.

## Executive result

The C12 implementation is already a **Segment + L1 parallel / L2-after-join**
design.  An admitted request consumes an L1-TLB port first, then creates a
single `lookup_operation` that schedules both L1 and (when enabled/installed)
Segment completion.  The L2 exact probe is not launched until the L1 result and
the Segment result are both known and neither has won.  Consequently a Segment
hit cannot have consumed L2 port, L2 tag/replacement, translation MSHR, PWQ,
walker/PWC, or PTE traffic in this C12 implementation.  It can only have
consumed its admission-time L1 port; an unfinished L1 result is logically
discarded.

This is a source fact about the C12 model, not an inference from C13 data.

## Request lifecycle

```text
LD/ST memory-pipeline head (one coalesced mem_access_t)
  -> ldst_unit::memory_cycle(): translation not yet applied
  -> translation_controller::translate(sid, asid=0, SimVA, bytes, uid)
     -> if already active lookup: PENDING; if READY: apply SimPA
     -> otherwise consume one per-SM L1 port and create lookup_operation
         -> L1 service interval                                  [parallel]
         -> eligible/installed Segment service interval          [parallel]
         -> winner selection
              Segment hit  -> READY (conventional exact tail suppressed)
              L1 hit       -> READY (late Segment result discarded)
              both miss    -> acquire L2 port -> L2 service
                                -> L2 hit -> fill L1 -> READY
                                -> L2 miss -> MSHR alloc/merge + PWQ
                                      -> walker + PWC progression
                                      -> physical PTE request(s)
                                      -> PTE response(s)
                                      -> fill L2 then waiter L1s
                                      -> requester retries L1 -> READY
  -> set SimPA and continue within the same memory_cycle invocation
  -> normal L1D/bypass/interconnect admission (or normal cache backpressure)
```

Source ownership and timing points:

| Stage | C12 code evidence | State/resource effect |
|---|---|---|
| Coalesced requester boundary | `src/gpgpu-sim/shader.cc:2424-2489` | `ldst_unit::memory_cycle` invokes translation only for the current memory-stage `accessq_back()` head. A non-`READY` result returns `false` with `COAL_STALL`; no normal data-cache processing follows that invocation. |
| Translation admission | `src/gpgpu-sim/vm_translation.cc:2154-2276` | Existing lookup/waiter is retried without resource competition. A fresh request consumes `m_l1s[sid].try_consume_port(cycle)` at lines 2229-2233 before the operation is created. |
| Parallel candidate launch | `vm_translation.cc:2222-2249` | `attempt_segment` requires enabled and active registration. The new operation receives both `cycle + L1_latency` and `cycle + Segment_latency`; no L2 work is launched at admission. Segment attempt is a registration-path attempt, not merely a Weight telemetry label. |
| L1/Segment completion and winner | `vm_translation.cc:1810-1970` | Both results are serviced from `LOOKUP_L1_SERVICE`; a Segment hit owns completion at lines 1878-1911. An L1 hit owns completion when Segment has not completed at lines 1913-1923. Only a dual miss advances to `LOOKUP_L2_LAUNCH` at line 1966. |
| Exact L2 | `vm_translation.cc:1972-2016` | L2 port is consumed only in `LOOKUP_L2_LAUNCH`, after the dual-miss gate. Probe/tag and potential L1 fill occur only after the L2 service interval. |
| MSHR/PWQ | `vm_translation.cc:2018-2087` | An L2 miss alone reaches `allocate_or_merge`; this is the only shown allocation/merge site. New allocation appends both MSHR and PWQ. |
| Walker/PWC/PTE | `vm_translation.cc:2357-2410`, `gpu-sim.cc:2172-2218` | Controller cycle turns PWQ entries into active walks. Physical PTEs are offered only for active walks and are injected into the real interconnect only after buffer admission; `pte_request_issued` commits that state. |
| Completion | `vm_translation.cc:2279-2355`, `shader.cc:2487-2533` | PTE completion fills conventional L2 and waiter L1s, records a completed outcome, and wakes waiters. Their normal retry does the accepted L1 delivery probe; `READY` sets SimPA and falls through to ordinary data-memory handling. |

## Race and cancellation boundary

### Segment hit

At a Segment hit C12 sets `LOOKUP_READY` immediately.  If the L1 result has
not completed, the model increments `segment_late_result_discards` and writes
the shadow L1 completion time to its launch time (`vm_translation.cc:1893-1901`).
This is a **logical late-loser discard**, not rollback of an L1 port: the port
was already consumed at admission.  If L1 completed concurrently and hit, C12
asserts matching PPNs (`1882-1888`).

The source then increments `segment_l2_suppressed`, `segment_mshr_suppressed`,
`segment_pwq_suppressed`, `segment_walker_suppressed`, `segment_pwc_suppressed`,
and `segment_pte_suppressed` (`1902-1908`).  These are accounting fields for
the avoided conventional tail.  They are not evidence that an already-admitted
L2/MSHR/PTW/PTE operation was physically cancelled: the state-machine gate
proves none was admitted for this lookup.

### L1-first result

If L1 hits before the Segment result is available, C12 returns the L1 result
without waiting for a Segment miss.  The Segment result is late-discarded
logically (`1913-1923`).  This preserves an existing fast exact path; it also
means Segment fallback penalty is confined to requests whose L1 result misses
and must wait for the Segment outcome before L2 can start.

### Dual miss and fallback

For an eligible Segment attempt, neither L2 nor MSHR admission begins until
both L1 and Segment have completed and missed (`1925-1967`).  The recorded
`segment_miss_join_wait_cycles` is the difference between the earlier and later
completion (`1954-1964`).  The fallback then reuses the completed L1 result;
it does not re-consume an L1 port or re-probe L1 (`1938-1940`).

### Merged request

Each new requester gets its own L1+Segment lookup before it may join an
existing exact MSHR: the active lookup test precedes `find_mshr` in
`translate()` (`2172-2213`).  If it dual-misses, `allocate_or_merge()` attaches
one waiter to the existing MSHR, records its lookup timing, and does not create
a second walk (`2046-2062`).  A Segment winner for that new requester can still
bypass the pre-existing exact walk; it does not cancel the other requester's
walk because that walk may have other waiters and has no per-request cancel
protocol.

## Requester latency versus memory issue

`note_requester_completion()` defines requester translation latency as
`ready_cycle - entry_cycle` (`vm_translation.cc:2094-2152`).  Its `ready_cycle`
is the cycle of the later retry call that observes `LOOKUP_READY` or the cycle
at which PTW completion records the waiter; it is a request-lifecycle latency,
not a global GPU critical-path measurement.  For an MSHR waiter it includes
time after MSHR join.

After `translate()` returns `READY`, the same `memory_cycle()` invocation sets
SimPA and immediately continues to normal L1D/bypass/interconnect code
(`shader.cc:2487-2533`).  Thus there is no deliberately inserted
translation-completion-to-data-issue delay.  Nevertheless a request can still
encounter ordinary L1D/cache/interconnect backpressure, and other warps/cores
can progress while this LD/ST head is translation-pending.  The existing
requester-latency total therefore cannot be read as exposed GPU execution
stall.

## Existing observability relevant to C14

C12 already has aggregate lookup, per-source outcome, MSHR/PWQ/walker/PWC/PTE,
object-attribution, and requester-latency statistics in
`vm_translation.h:567-774` and `vm_translation.cc:2716-3113`.  It also counts
`vm_translation_stall_cycles` at the LD/ST memory-cycle pending return
(`shader.cc:2479-2485`; output at `shader.cc:790-795`).  That latter field is a
useful local memory-stage blocked-cycle precursor, but has neither its own
explicit proxy contract nor per-kernel/object/source attribution.  The detailed
C14 gap-to-instrumentation mapping is in `OBSERVABILITY_GAP_MATRIX.tsv`.

## Consequences for C14 paths

1. **Path P candidate 1 is already the C12 architecture.**  C12 already gates
   L2 issue until Segment/L1 dual miss. Reimplementing “Segment-before-L2 gated
   issue” would be redundant and risks semantic drift.
2. **Path P candidate 2 has no safe unadmitted L2 exact work to cancel.** The
   only concrete pre-admission loser is the shadow L1 result after its port was
   consumed. There is no rollback boundary for that port, and cancellation of
   an existing MSHR/PTE would violate other-waiter ownership. It should be
   `NO_GO_WITH_EVIDENCE` unless future instrumentation disproves this control
   path.
3. **Path N can conservatively instrument the current memory-stage head
   condition.** It must call it a local `TRANSLATION_HEAD_BLOCKED_CYCLE` proxy,
   not a GPU-wide critical path, and separately observe ready-to-data admission.
