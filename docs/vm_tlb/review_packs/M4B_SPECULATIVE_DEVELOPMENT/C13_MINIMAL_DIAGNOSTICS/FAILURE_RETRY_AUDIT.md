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
