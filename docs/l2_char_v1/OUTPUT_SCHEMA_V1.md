# Framework L2CHARV1 artifacts

`util/l2_char/parse_l2_char.py` accepts only versioned `L2CHARV1` records and
fails for missing mandatory slice/window fields.  It never converts a missing
field to zero: missing values are `NA` where optional and mandatory omissions
are errors.  It emits `summary.csv`, `slice.csv`, `window.csv`, and
`manifest.json` with SHA256 provenance for supplied config and trace files.

The parser retains slice identifiers and orders windows by `(slice, window)`.
Workload-level spatial ratios are derived from slice data, not by averaging
per-slice percentiles.

For a formal campaign, invoke the parser with `--production`. It rejects
missing workload/input/kernel/kernel-id, config and trace paths, simulator
command, or either repository's branch/SHA. Debug mode retains `NA` only for
intentionally incomplete synthetic records.

`SLICE` also carries production set-reservation observations:
`max_reserved_ways_any_set`, `sets_all_ways_reserved_{avg,max}`, and
`cycles_any_set_all_reserved`.  These are optional additive V1 fields; older
logs remain parseable, while a producer that emits them must preserve the
same per-way production state definition documented by the paired core.

The core emits compact final `HIST` records for reserved ways, MSHR entries,
merge depth, MissQ, and MissQ-WB. The parser merges their bins across slices
and labels the result `*_global_p50/p95/max/avg`; it never averages a
per-slice percentile to represent a workload percentile. `WINDOW` carries
window-local eligible/blocked deltas and ratios for fill and frontend resource
blockers. `summary.csv` carries aggregate blockers, WB fractions, and both
slice CV and max/mean for supported resource metrics.
