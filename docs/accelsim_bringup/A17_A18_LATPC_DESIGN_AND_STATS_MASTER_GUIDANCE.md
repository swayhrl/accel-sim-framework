# A17 plus A18 LATPC design and stats master guidance

## Round name

A17_A18_LATPC_DESIGN_AND_STATS_ONLY

## Purpose

This large round follows A16 LATPC paper variant slot.

A16 completed the paper-specific baseline vs latpc_noop infrastructure on the LATPC paper workload NW.

A17 plus A18 must move from infrastructure to mechanism preparation:

- A17: locate code and produce a mechanism design for LATPC in the current Accel-Sim repository.
- A18: add stats-only instrumentation for LATPC-related behavior, without changing simulator behavior or timing semantics.

A17 plus A18 must not implement LATPC performance mechanisms yet.

Do not implement:

- Regularity Detector as a functional prefetch generator.
- LATC compressed L1 TLB MSHR behavior.
- LATP page table walk batching or prefetching behavior.
- Any new latency, queueing, resource reservation, or TLB fill behavior.

Stats-only source changes are allowed in A18, but counters must never affect simulator control flow.

## Paper

LATPC paper path:

docs/accelsim_bringup/paper/2025_MICRO_LATPC_TLB_Prefetch_MSHR.pdf

Paper title:

LATPC: Accelerating GPU Address Translation Using Locality-Aware TLB Prefetching and MSHR Compression

Core mechanisms to preserve in the design:

1. Regularity Detector
   - Located after the TLB coalescer.
   - Consumes unique VPNs from a warp memory instruction.
   - Emits triples of VPN, Stride, and Index.
   - Demand requests use Stride=0 and Index=0.
   - Prefetch candidates have non-zero Stride and non-zero Index.
   - Uses 9-bit stride logic to stay within a 512-page boundary.

2. LATC
   - Extends L1 TLB MSHR entry matching.
   - A single MSHR entry can represent up to 32 in-flight TLB misses.
   - Uses Base VPN, 9-bit Stride, and 32-bit Valid Mask.
   - Must preserve warp replay and subentry semantics.

3. LATP
   - Extends page table walker or page walk buffer behavior.
   - Batches or tracks multiple L4 PTE walks from the same locality group.
   - Uses the fact that 512 PTEs fit within one 4 KB L4 page table row.
   - L1-L3 page walks should remain conceptually shared or unchanged.

Important A18 observation targets:

- Page divergence per warp memory instruction.
- Unique VPN stride count.
- Same L4 page table locality.
- L1 TLB MSHR reservation failures.
- PTW queueing or page walk stall cycles.
- Translation latency or a documented approximation.
- Prefetch candidate coverage potential.

## Inputs from previous rounds

A16 key facts:

- Final commit from Codex report: 6c2f13afff0014e1d3ba88c98d5b7a5864b215f1
- Selected workload: nw, LATPC paper NW, Rodinia, Regular+High
- A16 was no-op infrastructure only.

Useful prior outputs:

.local_reports/A16A_latpc_paper_profile_*.md
.local_reports/A16A_latpc_selected_workload_*.json
.local_reports/A16B_latpc_variant_manifest_*.json
.local_reports/A16C_latpc_experiment_results_*.csv
.local_reports/A16D_latpc_validation_summary_*.md
.local_reports/A16E_latpc_final_summary_*.md

Also useful:

.local_reports/A11_stats_equivalence_matrix_*.csv
.local_reports/A12_workload_config_lock_*.csv
.local_reports/A13_experiment_matrix_*.csv
.local_reports/A13_experiment_results_*.csv

## Required subround order

Run these stages in order.

A17A: LATPC paper requirements.
A17B: LATPC code localization.
A17C: LATPC minimal mechanism design.
A17D: readiness gate for A18.

A18A: LATPC stats field specification.
A18B: stats-only instrumentation.
A18C: build and stats probe.
A18D: stats-only validation.
A18E: closeout and review pack.

Do not start A18B source modifications until A17D says the hooks are safe enough.

A18A may still be completed even if A17D reports partial readiness, because it is a design/spec document.

## Required tracked files to create or update

Expected scripts:

scripts/accelsim/a17_latpc_paper_requirements.py
scripts/accelsim/a17_latpc_code_locator.py
scripts/accelsim/a17_latpc_design_synthesizer.py
scripts/accelsim/a17_latpc_readiness_gate.py
scripts/accelsim/a18_latpc_stats_field_spec.py
scripts/accelsim/a18_latpc_stats_probe_runner.py
scripts/accelsim/a18_latpc_validate_stats_only.py
scripts/accelsim/a18_latpc_closeout.py

A18B may modify simulator source files only after A17D readiness is clear. Every modified source file must be listed in A18B and A18E reports.

Do not create large generated tracked files.

## Required runtime outputs

Use timestamp format YYYYMMDD_HHMMSS.

A17A outputs:

.local_reports/A17A_latpc_paper_requirements_<timestamp>.md
.local_reports/A17A_latpc_mechanism_requirements_<timestamp>.csv
.local_reports/A17A_latpc_target_stats_from_paper_<timestamp>.csv

A17B outputs:

.local_reports/A17B_latpc_code_localization_<timestamp>.md
.local_reports/A17B_latpc_code_localization_matrix_<timestamp>.csv
.local_reports/A17B_latpc_symbol_scan_<timestamp>.csv

A17C outputs:

.local_reports/A17C_latpc_minimal_design_<timestamp>.md
.local_reports/A17C_latpc_future_implementation_plan_<timestamp>.csv

A17D outputs:

.local_reports/A17D_latpc_readiness_gate_<timestamp>.md
.local_reports/A17D_latpc_readiness_matrix_<timestamp>.csv

A18A outputs:

.local_reports/A18A_latpc_stats_field_spec_<timestamp>.md
.local_reports/A18A_latpc_stats_field_spec_<timestamp>.csv

A18B outputs:

.local_reports/A18B_latpc_stats_instrumentation_summary_<timestamp>.md
.local_reports/A18B_latpc_modified_files_<timestamp>.csv
.local_reports/A18B_latpc_stats_availability_matrix_<timestamp>.csv

A18C outputs:

.local_reports/A18C_latpc_build_and_probe_summary_<timestamp>.md
.local_reports/A18C_latpc_stats_probe_results_<timestamp>.csv
.local_reports/A18C_latpc_extracted_stats_<timestamp>.csv
.local_logs/A18C_<timestamp>_build.log
.local_logs/A18C_<timestamp>_baseline.log
.local_logs/A18C_<timestamp>_stats_only.log

A18D outputs:

.local_reports/A18D_latpc_stats_only_validation_<timestamp>.md
.local_reports/A18D_latpc_behavior_compare_<timestamp>.csv
.local_reports/A18D_latpc_stats_presence_<timestamp>.csv

A18E outputs:

.local_reports/A18E_latpc_final_summary_<timestamp>.md
.local_reports/A18E_latpc_readiness_checklist_<timestamp>.csv
.local_reports/A18E_latpc_git_status_<timestamp>.txt
.local_reports/A18E_latpc_git_diffstat_<timestamp>.txt
review_packs/A17_A18_LATPC_DESIGN_STATS_review_pack_<timestamp>.tar.gz

## Status labels

Use these labels consistently:

PASS:
All required outputs exist, build/run/validation passed, and source changes are behavior-neutral.

PASS_WITH_WARNINGS:
Core objective passed, but some stats are partial, some hooks are approximate, or some optional targets are unavailable.

PASS_DESIGN_ONLY:
A17 completed, but A18 instrumentation was not safe to implement due to missing hooks. This is acceptable only if documented clearly.

BLOCKED_NO_PDF:
LATPC paper PDF is missing.

BLOCKED_NO_A16_CONTEXT:
A16 selected workload or variant context is missing and cannot be reconstructed.

BLOCKED_FOUNDATION_MISSING:
Current Accel-Sim tree does not contain enough VM/TLB/PTW foundation to safely instrument LATPC stats.

FAIL_BUILD:
Code changes were made but build failed.

FAIL_RUN:
Build passed but selected workload could not run.

FAIL_BEHAVIOR_CHANGED:
Stats-only instrumentation changed baseline cycles, instructions, IPC, or other exact fields beyond tolerance.

FAIL_DIRTY_TREE:
Unexpected runtime outputs or unrelated files remain in git status.

## Behavior preservation contract

A18 stats-only instrumentation may:

- Add counters.
- Add histogram counters.
- Add printout of latpc_* stats.
- Add scripts and reports.
- Add config metadata only when it does not affect behavior.
- Add comments documenting hook locations.

A18 stats-only instrumentation must not:

- Change queue size.
- Change latency.
- Change scheduling.
- Change TLB hit or miss decision.
- Change MSHR allocation decision.
- Change page walk issue, completion, or fill order.
- Change memory request order.
- Change replay logic.
- Inject prefetch requests.
- Compress MSHR entries.
- Batch PTW requests.

Any value computed for stats must not be used in a branch that changes simulator behavior.

## A18 readiness policy

A17D should classify readiness into one of three modes:

FULL_STATS_ONLY_INSTRUMENTATION:
Safe hooks exist for warp VPN/page divergence, TLB MSHR reservation failure, PTW/page walk, stats print path, and selected workload run path.

PARTIAL_STATS_ONLY_INSTRUMENTATION:
At least one safe hook exists, but not all paper target stats can be implemented. Proceed only with safe counters and clearly mark unavailable fields.

DESIGN_ONLY_BLOCKED:
No safe source-level instrumentation hook exists, or the codebase lacks the required VM/TLB/PTW foundation. Do not modify simulator core source. Produce reports and close out with PASS_DESIGN_ONLY or BLOCKED_FOUNDATION_MISSING.

## Time policy

Estimated total wall time: 2 to 4 hours.

Per-stage estimates:

- A17A: 10 to 20 minutes.
- A17B: 25 to 45 minutes.
- A17C: 20 to 40 minutes.
- A17D: 10 to 20 minutes.
- A18A: 15 to 25 minutes.
- A18B: 45 to 90 minutes if source instrumentation is safe.
- A18C: 20 to 60 minutes depending on build and simulator runtime.
- A18D: 10 to 25 minutes.
- A18E: 10 to 20 minutes.

If any single stage exceeds 60 minutes without producing a useful intermediate report, stop that stage and write a blocker report.

## Git policy

Do not push.

Do not use:

- git add .
- git add -A

Only add explicit tracked paths.

Never commit:

- .local_reports
- .local_logs
- .local_runs
- .local_traces
- review_packs
- trace files
- hw_run outputs
- build outputs
- paper PDF unless it was already tracked before this round

Final commit message suggestion:

scripts: add LATPC localization and stats instrumentation

## Final response requirements

The final Codex response must include:

1. Final status.
2. Final commit hash.
3. Review pack path.
4. A17A through A18E key report paths.
5. List of tracked files changed.
6. List of simulator source files changed, if any.
7. Selected workload.
8. Whether A18 used full, partial, or design-only mode.
9. Stats fields implemented, approximated, and unavailable.
10. Baseline behavior validation result.
11. Final git status --short.
12. Clear statement that A17 plus A18 did not implement LATPC performance mechanisms.
