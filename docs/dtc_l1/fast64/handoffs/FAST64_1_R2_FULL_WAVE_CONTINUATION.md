# FAST64.1 immutable R2 — full-wave continuation admission

Status: **ADMISSION PASS; five future-only rows authorized; no cohort-1 row altered**

The researcher supersedes the bootstrap two-worker ramp only for the five
missing immutable-R2 rows. The two cohort-1 rows remain unchanged and must
terminate naturally. Their inherited FD-9 dispatch lock is an old-controller
lifetime defect, not a scientific dependency, so the continuation uses a new
one-shot coordination lock:

`/workspace/fast64-runs/.fast64_1_r2_full_wave_continuation_dispatch.lock`.

The continuation's fixed scope is exactly:

1. `fast64_1r2_bicg_oo_cap8192_a1`
2. `fast64_1r2_bicg_io_cap1048576_a1`
3. `fast64_1r2_bicg_oo_cap1048576_a1`
4. `fast64_1r2_gesummv_io_cap8192_a1`
5. `fast64_1r2_gesummv_io_cap1048576_a1`

It cannot address either existing cohort-1 namespace. Every future row uses
the same immutable-v2 runner (`bf9a84…`), Core `bbcbb5e…`, runtime
`6a8743b4…`, A1 observer `2c2a6a…`, and frozen scientific/config source
`037f008b…`; current config and trace-config bytes are checked against that
frozen source before launch. The runner remains the only component that
atomically creates a namespace and publishes immutable START/TERMINAL
receipts.

## Fresh continuation audit

`/tmp/fast64-r2-continuation-resource-audit-20260908T123617Z.tsv` sampled the
actual cgroup for 60 seconds and returned
`PASS_FULL_FIVE_WORKER_CONTINUATION` at `2026-09-08T12:37:18Z`.

| field | observed value |
| --- | ---: |
| requested new R2 workers | 5 |
| cgroup quota | 384 CPU cores |
| cgroup useful CPU use | 12.822 core equivalents |
| throttled time / quota | 0.0000% |
| distinct physical-core candidates | 252 |
| live p95 simulator RSS | 3,107,979,264 bytes |
| required memory (5 + one safety footprint) | 18,647,875,584 bytes |
| MemAvailable | 131,807,342,592 bytes |
| cgroup memory headroom | 203,603,755,008 bytes |
| swap-out / OOM-kill delta / memory PSI | 0 / 0 / 0.00 |
| output required / free | 1,078,598,419 / 67,846,701,056 bytes |

Global host load average was 642.37 and host idle was 15.90%; these are
supplemental observations only. They are not mixed with the cgroup quota as a
hard rejection criterion. The candidate CPUs are topology-derived, distinct
physical cores; explicit `taskset` placement remains host scheduling metadata,
not scientific row identity.

The continuation audit and dispatcher are future-only and do not modify the
already-running SHA-pinned autorefiller, closeout controller, ordinary R2
dispatcher, collector, or either live cohort-1 process tree. The existing
closeout controller remains sole authority for 7/7 terminal strict collection
and `FAST64_1_R2_FULL_WAVE_COLLECTOR_PASS` publication.
