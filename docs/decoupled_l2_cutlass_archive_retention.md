# CUTLASS archive retention record

The functional screening campaign keeps representative CUTLASS SGEMM and
WMMA cases, not a full performance sweep.  The full V100 archive can therefore
be reclaimed after its reproducibility record has been saved.

## Original artifact

- Local archive: `hw_run/decoupled-l2-pretraces/cutlass.tgz`
- Source: `ftp://ftp.ecn.purdue.edu/tgrogers/accel-sim/traces/tesla-v100/1.1.0.latest/cutlass.tgz`
- Published byte length: `82490519015` (about 76.8 GiB)
- Full gzip scan: intentionally skipped on 2026-08-13; this is recorded in
  `hw_run/decoupled-l2-monitor/archive_verify/cutlass_gzip_test.log` and is
  not a claim that the full archive was verified.

## Retained evidence

- `hw_run/decoupled-l2-monitor/cutlass_screening_scope.md` records the
  representative/deferred-workload decision.
- `hw_run/decoupled-l2-extract/cutlass.stage` retains the selected source
  `kernelslist.g`.
- `hw_run/decoupled-l2-trace-fraction/cutlass-*` retains the replayable
  trimmed traces used by the functional campaign.
- Every paired run directory retains its `result.txt`, `smoke.out`, and
  `simulator_provenance.txt`; failed attempts remain alongside successful
  clean reruns rather than being overwritten.

Before deletion, write the local `stat` metadata and SHA-256 into
`hw_run/decoupled-l2-monitor/archive_retention/`.  Reacquisition must use the
exact source URL above; a future full CUTLASS study should obtain a fresh
archive and perform a complete integrity scan before member selection.
