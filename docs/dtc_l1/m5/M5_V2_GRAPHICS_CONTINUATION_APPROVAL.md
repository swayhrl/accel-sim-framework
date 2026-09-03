# M5 v2 Graphics Continuation Approval

Status: **HISTORICAL APPROVAL — SCHEDULING SUPERSEDED BY M5 v3**

Approval date: 2026-09-04.

This file originally authorized graphics continuation after the ten-compute M5.6 closeout. Its scientific constraints remain valid, but its sequencing/freeze assumptions are superseded by:

`docs/dtc_l1/m5/M5_V3_PARALLEL_TRACKS_APPROVAL.md`

Current authoritative interpretation:

- M5.7 provenance and M5.8 graphics path recovery may run **now** in an isolated Framework-only graphics-research window;
- M5.9+ graphics Core/integration work must wait for `M5.COMPUTE_FREEZE`;
- `M5.COMPUTE_FREEZE` requires both Paper-10 M5.6 PASS and Extended-20 M5.E3 PASS;
- graphics integration branches are created from the exact compute-freeze SHAs;
- M5.12 depends on Paper-10, Extended-20, and the graphics formal/unavailable terminal evidence.

Preserved scientific constraints:

- do not use a calibrated memory proxy as formal paper graphics reproduction;
- `GM-ALL-PAPER` requires all original 10 compute + 5 graphics workloads to be source-backed/correctness-clean and requires cross-path metric comparability;
- Extended-20 is supplemental and never part of `GM-ALL-PAPER`;
- Figure 4.6 area/synthesis remains outside M5 and requires separate M6 authorization.
