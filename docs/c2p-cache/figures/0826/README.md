# 0826 exploratory figure workspace

Everything below this directory is an **exploratory or diagnostic artifact**.
It is not a formal experiment result, publication figure, or conclusion source.
Each subdirectory must document its input provenance, transformations, and
limitations before it is reviewed or reused elsewhere.

Formal local measurements remain under `../local-results/`; editable redraws
of reference-paper artwork remain under `../paper-redraw/`.

- `fig11-paper-rs-rebucket16/`: measured local normalized-L2-access values
  regrouped by the paper's R/S labels.  This is a presentation-only
  diagnostic; it does not alter the underlying measurements.
- `fig11-paper-shape-local-avg-no-ccd/`: non-measurement sensitivity chart
  that retains each visible design's local group mean but uses the published
  Fig. 11 workload shape; CCD is hidden only in that rendering.
- `fig11-paper-shape-c2p-near-paper-no-ccd/`: the preceding visual shape
  construction with user-requested C2P-only group factors (`0.7359` for
  R1S0 and `0.8657` for R1S1); no new simulation data.
- `fig10-paper-rs-ata-all-shape-ga-c2p1034/`: derived from the latest Fig. 10
  visual sensitivity with only GA/C2P set to `1.034`; no new simulation data.

Current Fig. 10 sensitivity artifacts:

- `fig10-paper-rs-rebucket16-r1s1-mismatch-plus10/`: C2P-only +10% on
  paper-R1S1/local-mismatch cases.
- `fig10-paper-rs-rebucket16-r1s1-mismatch-plus10-sg-ge-2d-plus15/`:
  the preceding scenario plus a further C2P-only +15% on SGEMM, GEMM, and
  2DConv; includes ATA/CCD/RING paper-vector comparison tables.
- `fig10-paper-rs-rebucket16-ata-shape-sensitivity/`: the preceding C2P
  sensitivity scenario plus an explicitly non-measurement ATA shape exercise
  requested for visual comparison with the paper groups.
- `fig10-paper-rs-rebucket16-ata-shape-sensitivity-ring-r1s1-plus45/`: the
  preceding visual sensitivity exercise plus a uniform +45% RING multiplier
  on paper-R1S1 workloads; not simulator output.
- `fig10-paper-rs-rebucket16-ata-shape-ring-r1s1-plus595-no-ccd/`: follow-up
  figure with R1S1 RING at 1.595x of the local measurement and CCD hidden
  from rendering only; complete CSVs retain CCD.
- `fig10-paper-rs-rebucket16-ata-shape-ring-r1s1-plus16269-no-ccd/`: same
  figure with R1S1 RING at 1.6269x after a further +2% visual multiplier.
- `fig10-paper-rs-rebucket16-ata-shape-ring-r1s1-plus16269-no-ccd-r0s1-paper/`:
  same figure with all plotted R0S1 workload values replaced by the matching
  paper-vector values; the R0S1 AVG is recomputed over AT/BI/GS only.
- `fig10-paper-rs-rebucket16-ata-r1s1-paper-shape-avg803/`: keeps the
  current ATA R1S1 average while linearly preserving the paper's per-workload
  above/below-baseline direction; a visual construction, not simulator data.
- `fig10-paper-rs-rebucket16-ata-all-groups-paper-shape-local-avgs/`: applies
  the same paper-shape/current-average construction to ATA in every R/S group;
  the legend is moved above the plot to avoid overlap.
