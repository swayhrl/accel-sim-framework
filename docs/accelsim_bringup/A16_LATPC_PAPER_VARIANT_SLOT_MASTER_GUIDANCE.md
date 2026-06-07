# A16 LATPC paper variant slot master guidance

## Round name

A16_PAPER_VARIANT_SLOT_LATPC

## Purpose

This round makes Accel-Sim ready to run a paper-specific baseline-vs-variant loop for LATPC.

A16 is infrastructure only. It must create and validate a LATPC no-op variant slot. It must not implement LATPC mechanisms yet.

The intended full chain is:

1. Read and summarize the LATPC paper profile.
2. Pick one trace-available workload that appears in the paper.
3. Create a baseline-vs-latpc_noop variant slot.
4. Run a bounded experiment matrix with baseline and no-op variant.
5. Compare exact or approximate stats.
6. Produce result tables, final summary, and review pack.

## Paper

Server path:

docs/accelsim_bringup/paper/2025_MICRO_LATPC_TLB_Prefetch_MSHR.pdf

Paper title:

LATPC: Accelerating GPU Address Translation Using Locality-Aware TLB Prefetching and MSHR Compression

Important facts to preserve in A16 reports:

- LATPC is evaluated with Accel-Sim.
- The paper extends the simulator to model virtual memory features such as multi-level TLBs, page walk queue, page table walkers, and page walk cache.
- The evaluated system is RTX 2060-like.
- The paper evaluates 24 workloads from CUDA SDK, Lonestar, Pannotia, Parboil, Polybench, and Rodinia.
- The paper reports LATPC speedup over baseline, but A16 must not claim to reproduce the speedup.

## Primary workload policy

Do not choose ATX first unless a matching existing Accel-Sim trace is already available.

Current bringup evidence suggests Rodinia traces are more likely available. The preferred workload order is:

1. nw
2. lud
3. backprop
4. bfs or rodinia-bfs

Rationale:

- nw is in the LATPC paper table as NW, Regular+High, high L2 TLB MPKI.
- lud is also in the paper table as LUD.
- backprop is in the paper table as BP.
- rodinia-bfs is in the paper table as BFR, but existing local naming may be bfs.

If nw trace is available, select nw as A16 primary workload.
If nw is unavailable, fall back in the order above and document why.

## A16 scope

A16 must implement only a no-op or config-equivalent variant slot:

- baseline: existing Accel-Sim baseline command and config
- latpc_noop: same trace, same config, same simulator binary, same simulator arguments, only variant metadata differs

A16 must not:

- Modify simulator core behavior.
- Implement Regularity Detector.
- Modify TLB MSHR format.
- Modify page table walker behavior.
- Add LATP or LATC logic.
- Claim paper-level reproduction.
- Run a full 24-workload campaign.
- Attempt NVBit tracer if no GPU is visible.

## A16 subrounds

A16A: Paper profile and workload lock.

A16B: LATPC no-op variant slot.

A16C: Variant matrix runner.

A16D: Baseline vs no-op validation.

A16E: Closeout and review pack.

Complete them in order. Do not skip A16A, because A16B and later steps should depend on the selected workload and trace found by A16A.

## Required output locations

Tracked files may be added under:

- docs/accelsim_bringup/
- scripts/accelsim/

Runtime outputs must be placed only under:

- .local_reports/
- .local_logs/
- .local_runs/
- .local_traces/
- review_packs/

Do not commit runtime outputs.

## Required reports

Use timestamps in filenames.

A16A should produce:

- .local_reports/A16A_latpc_paper_profile_<timestamp>.md
- .local_reports/A16A_latpc_workload_candidates_<timestamp>.csv
- .local_reports/A16A_latpc_selected_workload_<timestamp>.json

A16B should produce:

- .local_reports/A16B_latpc_variant_slot_<timestamp>.md
- .local_reports/A16B_latpc_variant_manifest_<timestamp>.json

A16C should produce:

- .local_reports/A16C_latpc_variant_matrix_<timestamp>.csv
- .local_reports/A16C_latpc_command_matrix_<timestamp>.csv
- .local_reports/A16C_latpc_runner_summary_<timestamp>.md

A16D should produce:

- .local_reports/A16D_latpc_baseline_vs_noop_results_<timestamp>.csv
- .local_reports/A16D_latpc_baseline_vs_noop_compare_<timestamp>.csv
- .local_reports/A16D_latpc_validation_summary_<timestamp>.md

A16E should produce:

- .local_reports/A16E_latpc_final_summary_<timestamp>.md
- .local_reports/A16E_latpc_readiness_checklist_<timestamp>.csv
- review_packs/A16_LATPC_PAPER_VARIANT_SLOT_review_pack_<timestamp>.tar.gz

## Status semantics

Use these status labels:

- PASS: all required outputs exist, commands passed, no-op stats comparison is within tolerance.
- PASS_WITH_WARNINGS: core chain passed but some optional fields were missing or some paper text extraction was partial.
- BLOCKED_NO_TRACE: no matching existing trace for any candidate workload.
- BLOCKED_NO_PDF: LATPC paper PDF is missing.
- FAIL_RUNNER: runner or simulator command failed.
- FAIL_NOOP_MISMATCH: baseline and no-op variant produced unexpected stat differences.
- FAIL_DIRTY_TREE: unexpected tracked or untracked files remain after cleanup.

## Time policy

Estimated total wall time: 90 to 150 minutes.

Per-stage estimates:

- A16A: 10 to 20 minutes.
- A16B: 20 to 35 minutes.
- A16C: 30 to 50 minutes.
- A16D: 10 to 30 minutes, depending on simulator runtime.
- A16E: 10 to 20 minutes.

If any single stage exceeds 60 minutes without producing a useful intermediate report, stop and write a blocker report.

## Git policy

Do not push.

Do not use:

- git add .
- git add -A

Only add explicit tracked source paths under docs/accelsim_bringup and scripts/accelsim.

Never commit:

- .local_reports
- .local_logs
- .local_runs
- .local_traces
- review_packs
- hw_run
- trace files
- build products

The final response must include:

- Commit hash.
- Review pack path.
- Key report paths.
- Final git status --short.
- A clear statement that A16 is no-op variant infrastructure, not LATPC mechanism reproduction.

## Suggested final commit message

scripts: add LATPC paper variant slot pipeline
