# Paper figures — style redraw r1

Status: **PAPER_FIGURES_STYLE_REDRAW_REVIEW_READY**.

This is a **style-only redraw** of the current utilization and structural
blocking plots.  No simulator workload was rerun and no scientific-data value,
denominator, source CSV, or semantic definition was modified.

The reference plotting script was found and reviewed at
`PAPER_FIGURES_DRAFT_v5/plot_scripts/plot_blocking_composition_reference_style.py`.
Its compact paper layout conventions were reused/adapted for the current
seven-workload tables: white background, top horizontal legend, darker axes,
light dashed grids, thin vertical dashed separators, below-axis set label, and
primitive editable SVG output.  The script was adapted rather than invoked
unchanged because the reviewed current data use a different workload set and a
different Figure-2 denominator.

## Contents

* `figures/FIG1S_L2_UTILIZATION_REFERENCE_STYLE_DRAFT.{png,svg}` — same four
  current hotspot-slice utilization/pressure-proxy series and values.
* `figures/FIG2_L2_STRUCTURAL_BLOCKING_REFERENCE_STYLE_DRAFT.{png,svg}` — same
  WBUF=8 blocker stacks.  Stack height remains the overall blocking rate over
  eligible demand-miss admission cycles.
* `plotting_tables/` — exact copied current plotting tables plus source hashes.
* `plot_scripts/` — CSV-only renderer.

No benchmark-name-inferred archetype labels were added.  The below-axis caption
identifies only the selected exact workload set.
