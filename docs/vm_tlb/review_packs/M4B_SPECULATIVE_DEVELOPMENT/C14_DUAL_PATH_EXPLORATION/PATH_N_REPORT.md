# C14 Path N — translation exposure / criticality exploration

Status: `OBSERVATIONAL_PROXY_GO`; no architectural performance mechanism is
being proposed in this path.

Every value is `EXPLORATORY_MICRODIAGNOSTIC` and
`STATE_CONTEXT_NOT_FULL_ROI_EQUIVALENT`.  `HEAD_BLOCKED_CYCLES` means the
local LDST head proxy described in `PATH_N_INSTRUMENTATION_AUDIT.md`; it is
not a global GPU critical path.

## Completed exact-mode rows

| Selector / geometry | Cold cycles | Instructions | requester latency | local head-blocked aggregate | Other observation |
|---|---:|---:|---:|---:|---|
| N-FFN-L7, Prefill F0-like | 434459 | 91308032 | 8549602 | 8549602 | on/off pair matches cycles and instructions; pending requester HWM=35 |
| N-AP-L7, Prefill F0-like | 140838 | 31932416 | 2388326 | 2388326 | object-/outcome-keyed proxy emitted |
| N-DECODE-FFN, Decode F0-like | 456541 | 33181696 | 12946940 | 12946940 | L2 misses=176, walks=132, PTE-DRAM=42 |
| N-DECODE-AP, Decode F0-like | 127062 | 10571776 | 3469118 | 3469118 | ready L2/PTW accesses in the observed head commonly admitted same cycle |
| N-LOW-DELTA, Decode F0-like | 33994 | 9961472 | 593653 | 593653 | L2 misses=176, walks=39, PTE-DRAM=17 |
| N-LOW-DELTA, Decode F7-L5-like | 33312 | 9961472 | 348913 | 348913 | L2 misses=117, walks=6, PTE-DRAM=7 |
| N-HIGH-DELTA, Decode F0-like | 3758863 | 868036608 | 58685284 | 58685284 | L2 misses=8306, walks=8060, PTE-DRAM=2082 |
| N-HIGH-DELTA, Decode F7-L5-like | 3730066 | 868036608 | 34439916 | 34439916 | L2 misses=258, walks=37, PTE-DRAM=37 |

The low-delta selector was chosen from accepted full-ROI ranking where its
F7-L5/F0 cycle difference was near zero.  Its cold replay instead differs by
-682 cycles while translation aggregates drop substantially.  This is direct
evidence that the cold single-kernel context is not full-ROI equivalent; it
must not be used to overwrite the accepted ranking or extrapolate a speedup.

N-EO-691 remains in flight.  N-DECODE-FFN, N-DECODE-EO/high-delta F0, and
high-delta F7-L5 have terminal receipts.

## What has been established

1. Requester latency and local blocked-cycle accounting have the same total
   in the present LDST-head implementation because both increment for a
   pending head access.  They are nevertheless different concepts: requester
   latency counts lifecycle; the C14 proxy is constrained to a head request
   and can be attributed by object and outcome.
2. Translation ready-to-data-admission gap is directly observable.  It is
   often zero for L2-hit/PTW completion in the completed samples, while some
   L1-hit paths have positive queueing gaps.  “Data admission” is deliberately
   weaker than true memory/DRAM issue.
3. This is a useful `GO` for further *observation*, not a `GO` for claiming a
   global critical path or for changing TLB policy.

The high-delta cold pair directly demonstrates the needed distinction:
translation aggregates fall by `24245368` and cycles fall by `28797`.  The
former is an accumulated per-access quantity, so this is not a ratio or a
global-stall conversion.  It does show that even a very large translation
event reduction should be interpreted through an exposed-stall proxy and
actual cycle measurement rather than requester-latency alone.
