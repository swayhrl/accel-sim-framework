# Framework L2CHARV1 artifacts

`util/l2_char/parse_l2_char.py` accepts only versioned `L2CHARV1` records and
fails for missing mandatory slice/window fields.  It never converts a missing
field to zero: missing values are `NA` where optional and mandatory omissions
are errors.  It emits `summary.csv`, `slice.csv`, `window.csv`, and
`manifest.json` with SHA256 provenance for supplied config and trace files.

The parser retains slice identifiers and orders windows by `(slice, window)`.
Workload-level spatial ratios are derived from slice data, not by averaging
per-slice percentiles.
