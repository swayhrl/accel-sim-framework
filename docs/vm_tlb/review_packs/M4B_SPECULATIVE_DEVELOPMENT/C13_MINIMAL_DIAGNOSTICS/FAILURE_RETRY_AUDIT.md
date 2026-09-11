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
