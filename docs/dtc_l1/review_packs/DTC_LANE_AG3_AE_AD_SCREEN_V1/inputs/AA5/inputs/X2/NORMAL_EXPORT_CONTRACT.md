# X2 normal K1 export contract V1

Authorization: the user explicitly authorized this single print-only production
repair after AA4 `2b69f5ec8fae85c0ee1bbfe95ac93eb524bb172e` identified the missing
normal export. Baseline Core is `c0a5e2c31e407c57e3a4af3ce529c921e8059a05`.
This authorizes no full/canary simulation, old-lock acquisition, mechanism fix,
option retune, or continuation of AA1–4 execution authority.

## Normal entrypoint and population

The unchanged `gpgpu_sim::gpu_print_stat()` calls the existing
`shader_print_dtc_l1_stats()`. That function now adds a K1-only framed section,
calling const cluster -> core -> LDST delegates. The last delegate calls the
existing `source_invalidation_observer::print()` on its existing observer.
There is no new observer, counter, cache-state sampling or reset. The entire
legacy `shader_print_l1_miss_stat` chain remains disabled in normal printing.
The original per-SM row formatter and its field meanings are byte unchanged.

Each section covers the configured SM population exactly once; the FAST64
contract requires IDs 0..63. The section contains:

```
DTC_INVALIDATE_V1_SNAPSHOT_BEGIN version=1 sms=64 cycle=C no_event_cycle_sentinel=18446744073709551615
DTC_INVALIDATE_V1_SUMMARY sm=0 ... unchanged original fields ...
...
DTC_INVALIDATE_V1_SUMMARY sm=63 ... unchanged original fields ...
DTC_INVALIDATE_V1_SNAPSHOT_END version=1 sms=64 cycle=C
```

`C` is the existing absolute `global_cycle()` getter at the current normal
statistics boundary. No mutable snapshot counter/ID is introduced. More than
one normal print at the same cycle can yield separate identical snapshots;
these are not new events and are not merged or summed. Old public DTC/cache/
L2/DRAM numeric formats and aggregation meanings are unchanged.

## Cumulative values, absence and sentinel

The rows are per-SM **lifetime cumulative snapshots**, with the existing requests,
source counts (`idle`, `membar`, `config`, `unspecified`), ordinary commit count,
changed/retained/reclaimed/no-op totals, first/last request and commit cycles,
pending first/last request sequence IDs, and detail-record omissions.

A real K1 no-event row is present, has zero counts, and uses UINT64_MAX for all
four first/last cycle fields. The section explicitly declares this numeric
sentinel as UNDEFINED_NO_EVENT; do not turn it into a measured event cycle.
Pending first/last values are request sequence numbers, not clocks; a zero pair
means no pending sequence. Ordinary retirement may coalesce multiple requests;
it counts a commit invocation, including an unused ordinary Tag no-op, not the
number of ordinary mappings changed. Repeated idle requests remain counted.
Retained-at-event counts are not a second reclaim term.

K0 omitted/0 emits no K1 section or summary via this normal path. K0 event fields
remain UNAVAILABLE, not measured zero. The accepted AA3 observer supplement is
K1-only/noncomparative: no K1-minus-K0 event effect or causal share is licensed.
`-gpgpu_runtime_stat 500000` continues to parse with flag0, and debuglimit0
continues to suppress detail records. Neither option controls this normal
cumulative summary or was changed by X2.

## Parsing and last snapshot

`scripts/parse_normal_export.py` validates explicit framing/version/population,
all required unsigned fields, unique complete SM IDs, source/count arithmetic,
request and commit cycle/sentinel ranges, and pending-sequence bounds. It returns
the **last whole 64-SM snapshot**; it never sums cumulative snapshots or stitches
SM rows across boundaries. Missing, duplicate, unframed/private, truncated or
malformed sections fail closed, including a truncated final section after earlier
complete sections. K0 expected absence is a distinct unavailable result.

This parser qualifies the export section. It is not a replacement for a future
runner's complete normal-terminal/public-metric/timeout/conservation strict
acceptance. A completed export frame alone does not establish that a workload
finished or that the rest of its statistics were successfully printed.

## Scope and timing preservation

Only output delegates, their const declarations, and tests/build wiring change.
Idle-cluster/config/MEMBAR conditions and eager request linearization, physical/
generation/Ref/PIB/waiter/inflight/return identity, ordinary pending retirement,
finite quotas, clocks and public statistics are preserved by an exact source
delta allowlist. IO K1 remains STOP; modern, value/coherence/full-ISA and PPA
boundaries remain those accepted in V/Y2/X. AA4's prior STOP and historical
results are not revised or relabeled.

The pre-existing atomic invalidation with zero additional **simulated** cycles
is still a stated model assumption. Extra K1 host output has no assigned GPU
cycle cost here and proves no zero-cost hardware operation, port bandwidth,
area, frequency or physical timing result. Host wall time is not GPU speed.

## Qualification performed in this Goal

The CPU probe uses real compiled GPU/cluster/core/LDST objects and directly calls
`gpu_print_stat()` three times. It does not call a private observer printer,
launch a kernel, replay a trace, call GPU `cycle()`, or start a simulation
runtime thread. Prepared frontend metadata, a controlled ordinary owner, source
requests and one CPU LDST component cycle create bounded nonzero witnesses;
fixture timestamps are passive inputs, not performance results. 64x1 and 8x8
object topologies check both delegation loops. No-event sentinel, K0 omission/
explicit0, repeated requests, deferred commit coalescing, last-snapshot selection
and corruption rejection are tested. A separately fresh c0 build executes the
same fixture: its K1 normal export is absent, and all 15 corresponding old
public-output boundaries match the new build byte for byte after removing only
the new framed section. Seven original Core CTests are rerun unchanged.
