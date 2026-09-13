# Lane-E visual QA

This report is derived from the explicit agent visual-review record in `qa/E_VISUAL_REVIEW.tsv`. Machine signature/dimension checks are separately recorded in `E_MACHINE_FIGURE_CHECKS.tsv`; the builder does not assert human inspection.

| Figure | Status | Findings | Repair / re-review |
|---|---|---|---|
| F01 | PASS | All 12 workloads and Base/IO/OO legend are legible; retained IO regressions are visibly present; no clipping or overlap. | No repair required. |
| F02 | PASS | Heat-map headers, workload labels, source-unit labels, and nonexclusive-counter footnote are legible; no clipping or overlap. | No repair required. |
| F03 | PASS | Paired IO-HOL/OO-retire bars, legend, fraction axis, and noncausal footnote are legible; zero-height values are not mislabeled. | No repair required. |
| F04 | PASS | Logical-capacity axes, six-series legend, point markers, and accepted-points-only scope note are legible without clipping. | No repair required. |
| F05 | PASS | Physical sweep line membership is readable; 16.5-KiB boundary text explicitly distinguishes BICG/GESUMMV nonnumeric markers from Btree numeric points. | No repair required. |
| F06 | PASS | PIB capacity labels, compact series traces, legend, and same-mode scope note are fully visible and legible. | No repair required. |
| F07 | PASS | All ten panels, six-series legend, 24/32/48 labels, active-SM-cycle scope, and noncausal D4 note are visible and readable. | Removed duplicate F07 index emission and stale series call path before rebuild; regenerated and re-reviewed with one F07 only. |
| F08 | PASS | IO/OO duplicate-share bars, 7/3/2 descriptive annotation, percent axis, and legend are legible; figure does not imply DRAM traffic or performance recovery. | No repair required. |
| F09 | PASS | All 16 D6 evidence rows, the evidence-level colors, scope/boundary columns, and bottom boundary note are visible; no text or rows are clipped. | Initial 900-pixel matrix canvas clipped lower D6 rows. Expanded deterministic height to 1492 pixels, rebuilt, and re-reviewed all rows. |
