# Final decision

Decision:

`R101R4_P0_AND_P1_MATERIAL_POST_L1_DOWNSTREAM_LOCALIZED`

Native recommendation:

`NATIVE_CHECK_WARRANTED_POST_L1_DOWNSTREAM`

## Source-path audit

The accepted path was bound from translation completion through L1 lookup,
MSHR/miss queue, request ICNT, partition/L2, return ICNT, LD/ST response FIFO,
L1 fill/MSHR release and LDG/LDGSTS/store completion.  P1 is gated to exactly
`L1_GPU_CACHE`; no L2 or other cache instance can enter the local service.

## P0 result

P0 retains O2's post-translation/pre-L1 position and one-cycle service while
fixing scheduled/ready capacities at 1/16.  It completes rc=0 with empty
stderr, exact context, 55/55 gates, full drain and no duplicate/outstanding
transaction.

| Arm | ROI cycles | Improvement vs B0 |
| --- | ---: | ---: |
| accepted B0 | 2,985,319 | 0% |
| accepted O2 | 1,130,670 | 62.1256555832% |
| P0 finite pre-L1 | 1,130,670 | 62.1256555832% |

P0 boundaries are 3,293,262, 3,615,057 and 4,107,499 cycles.  It serves
27,594,656 reads and 2,342,912 writes with observed maximum scheduled/ready
depths 1/16 and no full event in this input.  P0 therefore passes the 5% gate:
the accepted O2 response does not depend on unbounded queue capacity under the
frozen envelope.

## P1 result

P1 preserves normal L1 lookup, reservation/merge/miss and normal L1 fill/MSHR
release.  Only an L1D lower request is locally serviced before request ICNT;
nonqualified and non-L1 traffic remain baseline.

P1 completes rc=0 with empty stderr, exact 2,976,829-cycle context, 57/57
gates, full drain and zero duplicate/outstanding requests.

| Arm | ROI cycles | Improvement vs B0 |
| --- | ---: | ---: |
| accepted B0 | 2,985,319 | 0% |
| P1 post-L1 local | 2,737,282 | 8.3085593198% |
| accepted S1 partition-side | 2,963,656 | 0.7256510946% |

P1 boundaries are 3,887,250, 4,798,511 and 5,714,111 cycles.  It locally
services 1,126,400 LDG reads and 2,342,912 writes.  Formal LDGSTS local-service
count is zero and is retained as an observation, not upgraded to an error.
Maximum scheduled/ready depths are exactly 1/16.  Finite pressure is real:
240,511 scheduled-full cycles and 243,786 ready-full cycles are observed.

Measured-ROI hierarchy deltas include 3,469,312 L1D accesses, 3,347,725 L1D
misses, zero pending-hit observations, 680,073 reservation failures,
26,494,723 L2 accesses, 1,494,893 L2 misses/DRAM reads and 353,077 DRAM
writebacks.  These are recorded mediators, not additive cycle fractions.

## Engineering recovery

The initial P1 formal attempt completed the exact context but deadlocked in
kernel4 because interception in generic `baseline_cache::cycle` lacked an
L1-instance guard.  The failed attempt and old runtime are retained as
engineering evidence.  Adding `m_level == L1_GPU_CACHE` restores the intended
scope without changing latency, queue capacity or service policy.  The rebuilt
binary passed full qualification and a bounded formal-XXT liveness diagnostic
before the complete formal rerun.

The complete rerun was rc=0 and immutable.  Its formal-at-run summarizer then
failed only two non-preregistered nonzero assumptions: formal LDGSTS service
and L1 pending-hit telemetry.  A hash-bound postprocess-only recovery records
both zero values, changes no simulator raw and closes 57/57 gates.

## Interpretation boundary

Because P0 and P1 are both at least 5%, while accepted S1 is below 5%, the
allowed conclusion is:

> In this accepted simulator scope, material response remains after the normal
> L1 miss decision but disappears at the partition-side S1 placement.

This result does not assign response to one downstream component, establish a
hardware mechanism, measure area/energy, prove Native speedup, novelty or
generalization.  O2/P0/P1/S1 differences must not be subtracted to claim L1,
ICNT or cache latency fractions.

No 109 run, FULL5, H1, queue sweep or new R101 mechanism was started.
