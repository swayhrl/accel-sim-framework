# C13 failure / retry audit

## Attempt 0 — admission deferred, no simulator launched

This is an infrastructure admission result, not an experiment failure and not
a C13 architecture finding.  At successive preflight samples on 2026-09-11:

| observable | observed | C13 decision |
|---|---:|---|
| logical CPUs | 512 | informational |
| runnable tasks | approximately 678--719 | reject new full-ROI work |
| CPU idle | approximately 4--6% | reject new full-ROI work |
| existing `accel-sim.out` processes | 42 | do not interfere |
| swap free | 24--108 KiB | reject new full-ROI work |
| memory PSI full / IO PSI full, avg10 | 0.00 / 0.00 | insufficient alone to admit |
| available memory | approximately 81--93 GiB | insufficient alone to admit |
| workspace free disk | approximately 91 GiB | retained as a future output-space check |

No C13 output directory or raw log was created.  No C12 / Operator-aware / other
project process was signaled, stopped, or modified.

## Retry policy

On a future admission check, require low runnable pressure and material free
swap in addition to nonzero available memory, low memory/IO PSI, and enough
disk for two fresh raw logs.  Start at most two P0 arms.  After each arm exits,
the C13 runner immediately writes its time sidecar and runs terminal,
provenance, telemetry, PTE/object, Segment, and per-kernel/snapshot closure
validation.  A resource-killed C13 attempt will be isolated in a new fresh
attempt directory and retried at lower concurrency; no raw log will be
overwritten.

## Addendum-controlled continuation — 2026-09-11

`C13_ADAPTIVE_ADMISSION_ADDENDUM.md` supersedes only the **future admission**
sentence above.  It does not change or delete Attempt 0: that conservative
deferral remains historical infrastructure evidence, not an experiment
failure.  In particular, high load/runnable pressure and low swap free are no
longer standalone rejection criteria; current CPU headroom, MemAvailable,
PSI, iowait, and observed swap-in/out govern 1→2-way admission.

Three subsequent 20 s-spaced samples before launch were GREEN: 512 logical
CPUs; CPU idle 5%; iowait 0%; MemAvailable 85.9–86.4 GiB; memory PSI full
0.00–0.14%; IO PSI full 0.00%; and `vmstat` swap-in/out 0 KiB/s.  The first
P0 arm (`C13-LAT-P8`) remained healthy for more than three minutes (RSS about
0.45 GiB, one-core CPU saturation, advancing markers); the second independent
P0 arm (`C13-LAT-D11`) was therefore admitted under the addendum.  The host
remains capped at two C13 full-ROI arms while aggregate CPU busy exceeds 90%.

## Attempt 00 — launcher lifecycle interruption (not a scientific result)

The first detached wrapper for `C13-LAT-P8` was reaped with its invoking
command session after emitting only the first marker.  Its nonterminal raw-log
prefix is preserved without overwrite at
`/workspace/vm-m4b-c13-diagnostics/results/C13-LAT-P8-ATTEMPT-00_LAUNCHER_LIFECYCLE_INTERRUPTED/`.
There was no simulator assertion, OOM, resource red condition, terminal
validator output, or architectural measurement.  The same frozen arm was then
restarted in a persistent command session into a fresh canonical output
directory and is the only candidate that can become an admitted C13 result.

## User-authorized 4-way P0 expansion — 2026-09-11

The user explicitly authorized a larger C13 parallel launch window after
observing approximately fifty logical CPUs of headroom and sufficient memory.
This instruction supersedes the previous *C13-only 2-way cap* while retaining
the original Goal's hard maximum of four full-ROI arms.  It does not authorize
interference with other projects or any fifth C13 arm.

Before expansion, three 10 s-spaced windows recorded CPU idle 9--10%, iowait
0%, MemAvailable 131.5--131.7 GiB, memory PSI full 0.00%, IO PSI full 0.00%,
and `vmstat` swap-in/out 0 KiB/s.  The existing P8/D11 simulators had combined
RSS about 1.15 GiB.  Under this explicit authorization, the existing simulator
PIDs were preserved and two independent, manifest-fixed config-only P0 arms
were added: `C13-LAT-P9` and `C13-CAP-P320`.  The C13 campaign driver was
updated to hold at four live arms and must not start a fifth.

## User-authorized full-matrix concurrent launch — 2026-09-11

The user then explicitly asked whether the five remaining fixed arms could run
alongside the existing four and authorized raising the limit if resources
allowed.  This is a scheduling override only: it does **not** add an
experiment, alter any config/trace/registration/Core/binary identity, or make
the diagnostic matrix exceed its fixed nine valid full-ROI arms.

Three additional 10 s-spaced windows were GREEN: CPU idle 9--10%,
MemAvailable 133.5--135.1 GiB, memory PSI full 0.00%, IO PSI full 0.00%,
iowait 0%, and swap-in/out 0 KiB/s.  The four live C13 arms had combined RSS
about 2.36 GiB.  This leaves material CPU headroom (roughly fifty logical
cores) and over 130 GiB available memory; even a conservative addition of five
C12-scale arm peaks remains well within headroom.  The campaign limit is
therefore nine—the complete fixed matrix and never a tenth arm—and the five
remaining manifest rows may be launched concurrently.

## Source-correct validator repair — `C13-SEL-D10` (no replay)

`C13-SEL-D10` exited cleanly with 740/740 markers and telemetry records, but
the first validator image incorrectly applied monotonic cumulative-counter
checks to every `vm_*` snapshot field.  Its only four errors were the
continuity/final-value checks for `vm_l2_tlb_subentry_valid_UNKNOWN` and
`vm_l2_tlb_subentry_valid_KV_CACHE`.  These are instantaneous valid-entry
gauges: the final Selective-policy snapshot can decrease after eviction and
must not be treated as per-kernel cumulative attribution.

The source-correct repair limits monotonic/delta-to-terminal validation to the
accepted Operator-aware `CUMULATIVE_METRIC_VALIDATION` set.  It adds a
`--validate` path that reads only an existing raw log and its `time-v` sidecar,
records the prior failed validation as
`C13_ARM_VALIDATION_PRE_REPAIR.json`, and refuses a live output directory.  No
simulator, Core, binary, trace, config, registration, or raw log is modified;
the immutable raw SHA remains the provenance anchor.  Any error that survives
this read-only revalidation remains fail-fast.

The repaired validator re-read the existing `C13-SEL-D10` log with SHA-256
`cb380b1288587ba5064b3b59e8ba949230e44ea860c309127f115f2c8750a426`.
The pre-repair JSON is retained alongside it and records exactly the four
gauge-only errors above.  Revalidation passed with simulator exit 0, 740/740
markers and telemetry records, and `gpu_tot_sim_cycle=34470902`; the accepted
monotonic attribution set had four active metrics and passed continuity plus
delta closure.  This is parser-only revalidation, not a replay.  Its paired
same-new-binary Decode control independently passed before the repair.

## Terminal parser-only revalidations — immutable evidence retained

The following terminal logs initially encountered the superseded validator image. Each retained `C13_ARM_VALIDATION_PRE_REPAIR.json` is immutable historical evidence; the current result comes from the source-correct `--validate` parser path, which reads the existing raw log only and never starts a simulator.

| arm | raw-log SHA-256 | retained gauge-only errors | final result |
| --- | --- | --- | --- |
| `C13-CAP-P320` | `34efd6337843065195b0f76bb6d9100e02a202e66a4c084aff5e7e9601d358eb` | `vm_snapshot_continuity:vm_l2_tlb_subentry_valid_occupancy; vm_terminal:vm_l2_tlb_subentry_valid_occupancy; vm_snapshot_continuity:vm_l2_tlb_subentry_valid_UNKNOWN; vm_terminal:vm_l2_tlb_subentry_valid_UNKNOWN; vm_snapshot_continuity:vm_l2_tlb_subentry_valid_WEIGHT; vm_terminal:vm_l2_tlb_subentry_valid_WEIGHT; vm_snapshot_continuity:vm_l2_tlb_subentry_valid_KV_CACHE; vm_terminal:vm_l2_tlb_subentry_valid_KV_CACHE` | PASS after immutable revalidation |
| `C13-SEL-D10` | `cb380b1288587ba5064b3b59e8ba949230e44ea860c309127f115f2c8750a426` | `vm_snapshot_continuity:vm_l2_tlb_subentry_valid_UNKNOWN; vm_terminal:vm_l2_tlb_subentry_valid_UNKNOWN; vm_snapshot_continuity:vm_l2_tlb_subentry_valid_KV_CACHE; vm_terminal:vm_l2_tlb_subentry_valid_KV_CACHE` | PASS after immutable revalidation |
| `C13-SEL-P10` | `f4e1707fbab5718bd567dce5c98373cdaa449d8aa571ff16e80d1bb9269f2f19` | `vm_snapshot_continuity:vm_l2_tlb_subentry_valid_KV_CACHE; vm_terminal:vm_l2_tlb_subentry_valid_KV_CACHE` | PASS after immutable revalidation |

These fields are instantaneous valid-entry occupancy gauges, not monotonic cumulative attribution counters. The accepted cumulative metric set remains fail-fast; any surviving non-gauge error would prevent final collection. No replay, raw-log rewrite, Core/binary/config/trace/registration change, or C12 asset modification occurred.
