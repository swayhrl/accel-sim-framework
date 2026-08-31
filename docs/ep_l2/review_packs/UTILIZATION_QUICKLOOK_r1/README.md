# EP-L2 utilization quicklook r1

Status: **UTILIZATION_QUICKLOOK_REVIEW_READY** — figure-only visual checkpoint.

This package was generated from frozen machine-readable CSVs only.  It launches
no simulator workload, modifies no Core source, and does not modify raw results
or scientific CSVs.  The selected exact workload set is `dwt2d`,
`convolutionSeparable`, `spmv`, `scan`, `FWT_7_21`, `cfd_097k`, and `btree`.

## Contents

* `figures/FIGA1_L2_UTILIZATION_HEATMAP.{png,svg}` — hotspot-slice resource
  occupancy / pressure heatmap.
* `figures/FIGA2_L2_UTILIZATION_GROUPED_BARS.{png,svg}` — the same values as
  grouped bars.
* `figures/FIGB_L2_BLOCKING_SUBSET_WBUF8.{png,svg}` — WBUF=8 exclusive blocker
  rates over eligible demand-miss admission cycles; printed labels are the total
  blocking rates.
* `plotting_tables/` — exact numbers and frozen-source SHA-256 records used by
  the figures.
* `plotting_scripts/` — reproducible CSV-only generator.
* `notes/METRIC_MAPPING.md` — AVG/P95/MAX selection and proxy semantics.
* `notes/OVERLAP_NOT_AVAILABLE.md` — why no simultaneous-blocker heatmap is
  claimed from the available frozen records.

The utilization selection is P95 where available, AVG for MissQ because this
schema has no MissQ P95, and capacity-normalized to the fixed 128-entry
per-slice resources.  Raw selected occupancy and capacity are retained in the
plotting table.  `MAX` is not plotted; it remains a schema field and is not
substituted for P95/AVG.  See the metric note for the WB-path proxy limitation.

Figures use a white paper-style background, black axes, dashed horizontal grid
lines, a horizontal legend, consistent category order, and text-preserving SVG
output.  Figure B contains no overlap interpretation.
