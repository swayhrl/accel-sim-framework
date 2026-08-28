# Peer-locality attribution guide

This guide defines how to interpret the read-only counters emitted by the
peer-locality diagnostic.  It intentionally contains no result values; the
per-run CSVs and their recorded provenance are the evidence source.

## Primary rate

The paper-comparable local opportunity rate is the issue-time, exact-sector
rate:

```text
issue_sector_redundant / issue_events
```

`issue_events` is a new-MSHR request that reached the ordinary lower-read
admission point.  It excludes MSHR merges, matching one physical L2 demand per
lower request.  `detect_events` is the same physical request set, sampled at
its common lower-queue insertion point.  The legacy `c2p_l1_misses` counter is
not a conservation anchor for this diagnostic: it is maintained by the C2P
accept path and can include events outside this queue-level observation set.
The wider accepted-L1-miss denominator is reported separately as
`l1_accepted_records = detect_events + l1_mshr_merge_records`; it must never
be substituted for the paper-comparable denominator without saying so.

## Evidence-to-cause matrix

| Observation | Attribution supported | Follow-up |
|---|---|---|
| `detect_mshr_merge_events` materially changes the rate versus `issue_events` | Statistic denominator/coalescing semantics | Compare paper wording and report both rates; do not change the mechanism. |
| Issue exact-sector rate is low, but issue resident-line rate is much higher | Sector-validity/data availability, not tag residency | Inspect sector cache configuration and whether the paper's L1 model is sectorized. |
| Many `detect_1_issue_0` events | Peer eviction or invalidation while the lower request waits | Use wait histogram, then check miss-queue/port pressure before changing candidate policy. |
| Many `detect_0_issue_1` events | A peer arrives during lower-request queueing | This is a timing/scheduling opportunity, not a Bloom-filter error. |
| Literal 16 KiB changes the rate toward the paper while four-set 64 KiB does not | Capacity is the dominant configuration difference | Treat the stated paper capacity/geometry contradiction explicitly. |
| Four-set 64 KiB changes the rate toward the paper while literal 16 KiB does not | Set/conflict geometry is dominant | Preserve 64 KiB capacity; study set indexing/replacement. |
| Neither geometry changes the gap, and the local/outer/distance distributions differ | Trace placement, 64x1 endpoint topology, or scheduler mapping | Run the explicitly recorded topology/scheduler sensitivity before changing C2P. |
| Exact-sector rate matches but C2P gains differ | Protocol/queue/remote-latency model, not redundant opportunity | Use the existing C2P residence, target-port, and probe statistics. |

## Locality safeguards

The local/outer split is based on a logical eight-SM cluster, and distance is
logical SID distance.  Neither is a physical NoC distance in the current
64x1-endpoint Accel-Sim configuration.  Therefore these counters may identify
trace placement or topology sensitivity, but may not be cited as a measured
network latency distribution.

## Qualification

Do not draw an attribution conclusion from a stage until its
`invariant_report.md` says every selected workload is `PASS`.  The report
requires 64 registered L1s, no lost detect record, detect/lower/issue count
conservation, and every histogram conservation equation.
