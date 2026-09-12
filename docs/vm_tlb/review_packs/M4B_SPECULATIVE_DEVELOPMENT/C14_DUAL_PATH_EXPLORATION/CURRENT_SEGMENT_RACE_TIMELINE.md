# C14 current Segment race timeline

Status: `SOURCE_VERIFIED_FACT`  
Core anchor: `57bb71ecd015b6ec0ab32e45b0815e5beaf69172`

`t0` below is the cycle at which a fresh requester wins the L1 admission port.
`L1done = t0 + L1_latency`; `Sdone = t0 + Segment_latency`.  Same-cycle
ordering is the fixed-point loop in `translation_controller::service_lookups()`
(`src/gpgpu-sim/vm_translation.cc:1810-1817`).

## 1. Segment fast hit

```text
t0:     consume L1 port; schedule L1 service and Segment service in one operation
t=Sdone: Segment lookup hits registered descriptor
         -> Segment owns READY; L2_issue=0; MSHR/PWQ/PTW/PTE=0 for this lookup
         -> if L1 not done, record logical late-L1 discard (port is not restored)
t>=Sdone: requester retry observes READY, receives Segment SimPA, then can try data path
```

No L2 port/tag/replacement has been consumed because `LOOKUP_L2_LAUNCH` cannot
be reached from a Segment hit (`vm_translation.cc:1878-1911` versus `1972-1990`).

## 2. Segment hit after an L1 service result is available

```text
t0:     consume L1 port; schedule both services
t=L1done: L1 probe completes
  hit:   L1 immediately owns READY; pending Segment result is logically discarded
  miss:  wait for Segment; do not launch L2
t=Sdone: if L1 was miss and Segment hits, Segment owns READY
```

When L1 and Segment complete at the same cycle and both hit, mapping agreement
is asserted.  C12 does not permit a L1 miss to launch L2 in the interval before
the Segment result returns (`1925-1931`).

## 3. Segment miss / exact fallback

```text
t0:      consume one L1 port; schedule L1 + Segment
t=L1done: L1 miss
t=Sdone:  Segment miss (or reversed order); record miss-join slack
t=max(...): dual miss -> request one L2 port
t+L2lat:  L2 hit -> fill L1 -> READY
           or L2 miss -> allocate/merge MSHR + enqueue PWQ
             -> walker/PWC -> PTE issue/response -> conventional fills -> retry READY
```

The fallback reuses the completed L1 result and does not re-probe/reconsume L1.
Its incremental joining delay is explicitly counted, but a full fallback-cost
decomposition is not currently available by requester/source.

## 4. New requester while an exact MSHR already exists

```text
t0:       newcomer still consumes L1 port and launches its own L1 + Segment race
Segment hit: newcomer is READY from Segment; existing exact MSHR continues for its owners
dual miss:   newcomer joins existing MSHR once; it does not create another walk
completion:  existing MSHR fills conventional TLBs and wakes all attached waiters
```

This protects Segment opportunities for a new requester, but establishes no
safe request-local cancellation boundary within an already-admitted shared walk.

## Resource/cancellation ledger

| Resource/work | Segment hit before L1 completes | Segment hit after L1 completion | Can C12 cancel it? |
|---|---|---|---|
| L1 port | Already consumed at `t0` | Already consumed | No rollback API/source state |
| L1 tag/probe | Not yet called; result logically discarded | Already probed | Only pre-probe logical discard; no port refund |
| L2 port / tag / replacement | Not issued | Not issued | Suppressed by dual-miss state gate, not cancellation |
| MSHR/PWQ | Not allocated | Not allocated | Suppressed by dual-miss state gate |
| Walker/PWC/PTE | Not started/issued | Not started/issued | Suppressed by dual-miss state gate |
| Existing other-owner MSHR/PTW | May exist independently | May exist independently | No: shared ownership and no request-local cancel protocol |

## Modeling caveat

The comments/counters call L1 and Segment “parallel,” but this model does not
represent a separately cancelable L1 response queue.  The L1 port is a timing
resource; `probe()` occurs only at modeled completion. Therefore any C14 claim
about saved *physical* exact work must distinguish (a) port time already spent,
(b) a pre-probe shadow result not executed, and (c) conventional-tail work that
the existing gate already never admitted.
