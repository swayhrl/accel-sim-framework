# Codex → ChatGPT latest report

Stage: figure-only utilization quicklook — visual review ready

Status: **UTILIZATION_QUICKLOOK_REVIEW_READY**

This is a new, isolated visual checkpoint.  It does not supersede the Target
Baseline campaign or make a scientific acceptance claim.

Frozen runtime provenance used by this quicklook:

* Core: `ca3e7bc0b8f61b5d7c052bcda2a91955a1e5c919`
* Framework: `db1c90182fad02aacbd282b67ecdc57b8e4cc365`
* B0/Motivation schemas: `EPL2B0V1` / `EPL2MOTV1`

The package contains CSV-only redraws for exactly seven selected workloads:
`dwt2d`, `convolutionSeparable`, `spmv`, `scan`, `FWT_7_21`, `cfd_097k`, and
`btree`.  It includes a P95/AVG hotspot-slice occupancy heatmap, matching grouped
bars, and a WBUF=8 exclusive-blocking subset view.  No simulator workload was
rerun; no Core source, raw result, or scientific CSV was modified.

The frozen outputs do not contain joint blocker states, so no simultaneous
overlap matrix is inferred or plotted.  The precise limitation and required
future telemetry are documented in the package.

Review entry point: [UTILIZATION_QUICKLOOK_r1](../review_packs/UTILIZATION_QUICKLOOK_r1/README.md)
