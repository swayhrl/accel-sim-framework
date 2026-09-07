# Future resource gate contract

**Evidence label: `SPECULATIVE_DIAGNOSTIC`**

Before every future B9 job, effective concurrency is exactly one. The helper
observes two snapshots five seconds apart and refuses launch when either
`pswpin` or `pswpout` changes, available memory falls below the accepted
threshold, or iowait exceeds 15% in that window.

The normal threshold is the accepted B6/B7 formula:
`MemTotal/5 + 4 GiB`. After E07/E08 calibration, it is never lowered; the
required value becomes the maximum of that normal threshold, `4 * peak_RSS`,
and `memory_span + 2 * peak_RSS`. E09/E10 require their phase's successful
calibration artifact and a supplied calibrated peak/span. An admission failure
is `RESOURCE_DEFERRED`, not a zero result and not permission to relax a limit.

E07/E08 capture `/usr/bin/time -v` peak RSS, MemAvailable before/after, the
swap window, iowait, and partial hash. Every arm writes fresh evidence below
`/workspace/vm-spec-farm/future-evidence/b9-e01-e10/`; B1--B8 paths are never
reused or overwritten.
