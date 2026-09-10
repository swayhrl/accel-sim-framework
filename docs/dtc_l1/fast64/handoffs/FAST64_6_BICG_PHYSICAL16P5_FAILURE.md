# FAST64.6 — BICG / 16.5-KiB physical-pool preserved failures

Status: **TWO TERMINAL FAILURES PRESERVED; NOT RESULTS; NO STAGE PROMOTION**

## Frozen attempt identity

Both attempts use the frozen FAST64.6 physical point (132 physical 128-B
lines = 16,896 B), BICG payload, scientific Framework
`037f008b330eb230353b60edf126d6be9f45afdc`, repaired Core
`95ccdb7a056f2d53f740d90869785cac6d4ee0f5`, repaired runtime
`462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9`, A1
observer, config-materialization source
`180e81c68816012165c26dab577e693b3b798292`, and SHA-addressed immutable
runner `bf9a84c8aab54ccd5d00a8465d69669cfac78012b783c3cfd9e0e4433062e6af`.

| Attempt | Mode/config | UUID | terminal receipt | disposition |
| --- | --- | --- | --- | --- |
| `/workspace/fast64-sensitivity-v1/fast64_sens_v1_bicg_physical16p5_io` | IO / `FAST64_SENS_PHYSICAL_16p5KB_IO` | `cf459ee2-7ac4-4caa-8649-26eeb31d1d4e` | exit 1, `2026-09-10T17:34:54Z` | `FAILED_CAPACITY_BOUND_DEADLOCK_PRESERVED_NOT_RESULT` |
| `/workspace/fast64-sensitivity-v1/fast64_sens_v1_bicg_physical16p5_oo` | OO / `FAST64_SENS_PHYSICAL_16p5KB_OO` | `a6061cae-52b5-4263-a7fd-04434386ffaa` | exit 1, `2026-09-10T17:17:10Z` | `FAILED_DEADLOCK_PRESERVED_NOT_RESULT_OO_DIAGNOSTIC_PENDING` |

The read-only closeout collector correctly did not generate a success JSON for
either row.  The raw output, receipts and immutable manifests remain in their
listed namespaces.  Neither failure is a timeout, an observer failure or a
performance data point.

## IO source-backed classification

The IO fatal at `simulator.stdout:2534` reports deadlock after the last
writeback from core 27.  The immediately following DTC dump shows each affected
SM has one non-ready FIFO head, zero free and 132 allocated physical lines,
one partial entry holding 28--31 lines, and zero lower-create, lower-issue and
inflight requests.  Its preceding periodic statistics show lower
create/issue/response `526336/526336/526336`, lower credit
acquire/release `526336/526336`, lower outstanding zero and lower-cap-full
zero.  Thus this is not a downstream lower-cap or response-loss hypothesis.

This is the exact intentionally modeled IO circular resource dependency:
`dtc_l1::io_frontend::access()` retains the references already allocated to an
instruction when a later required line has no free physical allocation; FIFO
retirement requires the incomplete head to become ready before releases occur.
`docs/dtc_l1/DTC_L1_SPEC.md` §§3.4 and 8 freeze this behavior: partial
allocation has no rollback, and physical-space deadlock is valid in
undersized configurations.  The implementation must not be changed to
rollback or atomically allocate all lines just to make this sensitivity point
complete.

## OO disposition and next observation

The OO attempt independently reaches the simulator deadlock detector, but the
current formal Core emits the detailed resource dump only for PAPER_IO.
Its last periodic counters have balanced lower lifecycle and zero outstanding
lower requests, while no terminal OO resource snapshot exists.  It must not be
silently assigned the IO root cause.  The next action is a future-only,
telemetry-only OO fatal-dump enhancement and one exact nonformal diagnostic
reproduction when a resource-safe slot is available.  It cannot change timing,
allocation, retirement, request lifecycle, config, payload or formal Core
identity, and the original failure remains preserved regardless of the
diagnostic outcome.

The concurrently active 24-KiB BICG rows and all Stage3/4 simulators are not
modified, restarted or displaced.  FAST64.6 stays
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`; it does not logically advance.
