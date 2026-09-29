# Engineering fixes

## Git transport

The initial HTTPS fetch made no progress. HTTP/1.1 also stalled and was
terminated after a bounded wait. GitHub SSH fetched the exact expected handoff
commit. No scientific work was affected.

## Positive-smoke validator

The first S1 positive-smoke postcheck required nonzero sampled return-queue
occupancy. The existing queue can drain in the same cycle as the sample, so the
observed maximum was legitimately zero. The simulator run itself was rc=0 and
unchanged. Validation was rerun against the immutable log with source-level
proof of the existing return path.

## Formal attempt0

Before attempt0 had completed a kernel, review found a non-preregistered
summarizer condition requiring all subpartitions and an assumed queue depth.
Only the exact R101R3 child and runner were terminated. The partial raw is
retained under `raw/formal/failed` and is not used scientifically.

The all-subpartition requirement was reduced to recording nonzero
participation before the successful run. The assumed queue-depth bound
remained inadvertently in the formal-at-run summarizer.

## Completed-run postprocessing

The successful simulator process completed rc=0, empty stderr and 6/6
coverage. Two postprocessing-only checks failed:

- the inherited `awma_r101r2_transient_service_mode` print label reflects the
  shared combined service enum and therefore prints `s1_partition_hit`, while
  the command receipt independently proves R101R2 O2 was selected as none;
- maximum existing ingress/return occupancy was 61/64 rather than the
  summarizer's unapproved assumed maximum 8.

A recovery summarizer used the command receipt as selector authority and
treated 61/64 as observed finite-path telemetry. It also requires actual
return-full and data-port-busy cycles. All 56 gates then pass.

`ORCHESTRATION_RECOVERY.json` binds every immutable simulator artifact before
and after recovery. No simulator rerun or scientific-value modification
occurred.
