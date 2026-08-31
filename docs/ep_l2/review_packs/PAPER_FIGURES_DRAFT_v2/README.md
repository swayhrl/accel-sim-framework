# Paper figures draft v2

Status: `PAPER_FIGURES_DRAFT_V2_REVIEW_READY` — visual review only.

This is a figure-only redraw. No simulator workload was rerun, and no raw log, scientific CSV value, simulator source, parser semantic, or frozen provenance was modified. The only inputs are the frozen CSVs in `../DRAFT_FIGURES_CHECKPOINT_r1/plotting_tables/` (their per-row CSV source paths and SHAs are recorded there).

Workload order and group separators are identical across all three figures:

1. Streaming / Spatial: `vectorAdd_4M`, `BlackScholes`
2. Low Temporal Reuse: `dwt2d`, `convolutionSeparable`, `mergeSort`, `sad`, `spmv`, `transpose`, `scan`
3. Reuse Rich: `FWT_7_21`, `cfd_097k`, `btree`, `gemm`

Figure 1 is conditioned only on true temporal sector reuse. `vectorAdd_4M` and `BlackScholes` have no such events, so their positions are deliberately preserved as N/A rather than fabricated 100%-normalized bars. The `T=` labels come from the exact all-sector temporal fraction in `FIG1V2_PANEL_A.csv`.

Figure 1S retains the cold / spatial / true-temporal decomposition over all sector references. Figure 2 uses WBUF=8, with every blocker segment divided by eligible miss-admission cycles; therefore each stack height, and its printed value, is the overall L2 admission blocking rate, not a composition among already-blocked cycles.

`plotting_tables/` holds the exact ordered values rendered; `plot_scripts/redraw_paper_figures.py` is the reproducible CSV-only renderer. SVGs are primitive, editable vector elements.
