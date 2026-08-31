# Paper figures draft v3 — vectorAdd removed

Status: visual review only. This is a new figure-only redraw and leaves `PAPER_FIGURES_DRAFT_v2/` unchanged.

`vectorAdd_4M` is removed from all three figures and all corresponding ordered plotting tables. All other values are read unchanged from the frozen CSV inputs used by v2; no simulator workload was rerun and no scientific data, raw log, parser, source, or provenance was modified.

Order: `BlackScholes`; `dwt2d`, `convolutionSeparable`, `mergeSort`, `sad`, `spmv`, `transpose`, `scan`; `FWT_7_21`, `cfd_097k`, `btree`, `gemm`.

The same conditional-reuse, zero-temporal handling, and Figure 2 eligible-miss-admission-cycle denominator semantics as v2 are retained. The wrapper under `plot_scripts/` invokes the frozen v2 CSV-only renderer with only the workload order changed.
