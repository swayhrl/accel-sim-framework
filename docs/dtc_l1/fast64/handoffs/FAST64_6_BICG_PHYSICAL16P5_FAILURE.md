# FAST64.6 — BICG / 16.5-KiB physical-pool preserved failures

Status: **TWO TERMINAL FAILURES PRESERVED; SOURCE-BACKED CAPACITY-BOUND
CLASSIFICATION CLOSED; NOT RESULTS; NO STAGE PROMOTION**

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

## OO source-backed classification

The already-acquired, future-only observational replay in
`/workspace/fast64-diagnostics/fast64_6_bicg_physical16p5_oo_coref283_diag_v1`
is terminal, not live.  Its immutable receipt records UUID
`2ef7f749-cf0c-4d45-a9d0-4a73b35d9d21`, exit `1`, and terminal UTC
`2026-09-10T21:53:36Z`; it binds the detached telemetry-only f283 Core,
immutable runner, exact frozen BICG payload and OO configuration.  It emits
the mode-specific `DTC_L1_OO_DEADLOCK` snapshot after the existing simulator
deadlock decision.

The unchanged diagnostic parser has materialized
`generated/fast64_6_diagnostics_v2/fast64_6_bicg_physical16p5_oo_coref283_diag_v1.json`
as `NONFORMAL_DIAGNOSTIC_NOT_RESULT`.  Its 16 printed SMs (16--31) each have
one PIB/frontend entry, `allocated_phys=132`, active references 28--31, and
zero lower-create/lower-issue/inflight work.  Since the frozen pool has exactly
132 physical lines, this independently proves OO capacity exhaustion with no
pending lower request or response.  It is not an inference from the IO row or
from GESUMMV.

The source-defined OO frontend rejects an allocation when no physical line is
free and its victim still has nonzero reference count; a deferred line can be
released only after a ready entry retires and its final reference closes.  The
f283 source region is identical to the later diagnostic source for
`dtc-l1-common.h` and `shader.cc`.  This is therefore a
**SOURCE_BACKED_CAPACITY_BOUND_RESOURCE_DEADLOCK**, not a source repair
candidate.  No allocation rollback, forced reclaim, or retry is authorized;
the original formal failure and the observation remain excluded from all
performance results and sensitivity curves.

The concurrently active 24-KiB BICG rows and all Stage3/4 simulators are not
modified, restarted or displaced.  FAST64.6 stays
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`; it does not logically advance.
