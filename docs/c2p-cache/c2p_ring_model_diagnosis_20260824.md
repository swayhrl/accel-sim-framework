# RING comparator diagnosis — 2026-08-24

## Finding

The prior post-`eff44679` RING comparator held an L1 miss-queue head whenever
its global discovery queue was full.  That is not the queue-full behavior of
the cited CCN/RING design.  CCN has a finite per-SM CB/ReqQ pair; if the request
network is congested, **new** local misses go directly to L2 until space returns.
Requests already accepted by CCN still make their normal ring traversal.

The primary source is Dublish, Nagarajan, and Topham, *Cooperative Caching for
GPUs*, TACO 2016, Sec. 4.2/4.2.1: it specifies local CB/ReqQ backpressure,
direct L2 routing while the CCN cannot accept a request, and a per-core request
throttler.  The paper is available at
<https://www.pure.ed.ac.uk/ws/portalfiles/portal/29959329/taco16_dublish_PURE_1.pdf>.
The C2P paper cites this design as its RING comparator.

This is distinct from C2P's query-queue escape path.  RING fallback is reported
by `c2p_ring_queue_bypasses`; `c2p_queries_queue_bypass` remains the C2P
controller metric and remains zero for RING.

## Controlled variants

| Variant | Queue-full behavior | Purpose |
|---|---|---|
| strict historical | Hold L1 miss head (`MISS_STALL`) | Reproduce the post-`eff44679` point only |
| CCN fallback | New miss goes to baseline L2 | Source-faithful RING/CCN backpressure |
| directed-link pipeline | Reserve each traversed request link | Physical-link sensitivity only; not a replacement for CCN fallback |

All variants preserve the C2P-paper comparator delays: two cycles per RING hop,
seven cycles for copied-tag lookup, and fourteen cycles for the remote cache-line
path.  No RING remote-hit predicate, L2 geometry, or trace was changed.

## First Btree result

The first replay used the 64-KiB Table-1 interpretation and the normal Btree
trace.  Its source/binary is frozen below its run directory.

| Mode | Total cycles | Normalized to baseline | Accepted RING requests | Remote hits | Ring queue fallbacks |
|---|---:|---:|---:|---:|---:|
| baseline | 234,962 | 1.000 | – | – | – |
| strict historical RING | 2,577,677 | 0.091 | 1,282,179 | 219,781 | 0 |
| CCN fallback RING, accounting-fixed replay | 227,340 | 1.034 | 106,031 | 28,997 | 1,202,846 |

The strict point is dominated by the global 0.5-request/cycle injection limit:
`1,282,179 × 2` cycles is already essentially the observed runtime.  CCN fallback
removes this model artifact while retaining every accepted traversal.  The result
therefore establishes that the former `0.091×` Btree RING result was not a credible
representation of the cited comparator.

The accounting-fixed replay preserves the same cycle count and satisfies the key
conservation check:

```
1,308,877 c2p_l1_misses
  = 106,031 c2p_queries_accepted
  + 1,202,846 c2p_ring_queue_bypasses
```

The corrected Btree evidence is therefore final for this point.  The independent
CUTCP and Stencil points below are from the same
`hw_run/c2p-ring-ccn-fallback-v2-20260824/` campaign.

## Corrected three-workload check

All three corrected runs below use the same binary and 64-KiB primary Table-1
interpretation as the audited paper-16 baseline/C2P results.  IPC normalization
is `baseline cycles / RING cycles`.

| Workload | Baseline cycles | CCN fallback RING cycles | RING normalized IPC | C2P normalized IPC | Interpretation |
|---|---:|---:|---:|---:|---|
| Btree | 234,962 | 227,340 | 1.034 | 1.026 | A high-reuse tree case that is modestly above baseline. |
| CUTCP | 4,538,631 | 4,616,155 | 0.983 | 1.001 | R1S0: many remote hits but little L2-latency sensitivity. |
| Stencil | 4,960,360 | 10,243,063 | 0.484 | 1.411 | The queue correction halves the old strict penalty but does not cure ring congestion. |

Stencil illustrates why the correction is necessary but not sufficient.  It accepts
4,643,838 requests and sends 5,267,051 more directly to L2, yet produces only
1,522,796 remote hits.  C2P instead obtains 3,280,804 remote hits with its parallel
filter/probe path.  The next RING-only mechanism to assess is the cited CCN's
per-SM request throttler; it must remain a separately configured experiment.

An explicitly labelled Btree capacity sensitivity (`ReqQ=512`) was also completed:
it slows RING to 252,841 cycles (0.929×).  Increasing the global accepted window
adds more network wait than useful hits, so it is not promoted to the main point.

## CCN-aligned comparator revision

The initial corrected point still used a single chip-global issue timestamp.
That is not a ring: it prevents independent links from pipelining, while also
failing to charge later requests for contention on the links they actually
cross.  The primary RING configuration now reserves every traversed directed
link for the paper's two-cycle hop time.

The original CCN additionally uses a per-core Request Throttler (RT): each SM
samples one million committed scalar instructions in a ten-million-instruction
epoch and, when its observed remote-hit rate is below 5%, sends subsequent
misses directly to L2 until the next epoch.  The new RING configuration
implements precisely those parameters.  A throttle bypass is a normal L1 miss
to L2; its copied tag remains available to other requesters.  Four counters
make the decision auditable:

- `c2p_ring_throttle_samples`;
- `c2p_ring_throttle_sample_requests`;
- `c2p_ring_throttle_sample_hits`;
- `c2p_ring_throttle_bypasses`.

This corrects the CCN comparator; it is not an optimization applied to C2P.
The response ring (opposite-direction response queues and their explicit
capacity) remains outside the present C2P comparator abstraction.  It should
be modeled only in a separately labelled CCN microarchitecture study, rather
than approximated by an uncalibrated response constant.

## Next validation

1. Verify corrected Btree accounting:
   `l1_misses = accepted + ring_queue_bypasses` and a fixed identical cycle count.
2. Complete CUTCP (R1S0) and Stencil (R1S1), contrasting the corrected RING point
   with their frozen strict results and baseline.
3. Keep directed-link results as a sensitivity result.  A no-match request occupies
   all links, so a physically stricter model can legitimately be slower; it must not
   be silently substituted for the CCN queue policy.
4. The CCN-aligned directed-link + RT configuration is being replayed for all
   sixteen canonical traces and the only R1S1 V100 extension, ISPASS BFS.  Do
   not combine these results with the historical global-injector points.
