# A20-A23 LATPC VM substrate master guidance

## Round name

A20_A23_LATPC_VM_SUBSTRATE

## Purpose

This large round follows A19.

A19 concluded that the current tree provides address observation and stats print plumbing, but does not expose a complete active L1/L2 TLB, TLB MSHR, PTW, page-walk queue, or PWC foundation that can directly host faithful LATPC.

A20-A23 must build a minimal shadow virtual-memory substrate that can observe addresses, derive VPNs, simulate TLB/MSHR/PTW/PWC-like statistics in a side model, and validate that this model does not change simulator timing or control behavior.

This round is not LATPC mechanism implementation. It is a foundation round.

## Core principle

Implement a shadow VM substrate first.

The shadow VM substrate may:

- observe warp memory instruction addresses
- derive VPNs using a configurable page size
- maintain shadow L1 TLB and L2 TLB state
- maintain shadow TLB MSHR occupancy and reservation failure counters
- maintain shadow PTW queue and PTW completion counters
- optionally maintain shadow PWC counters if safe
- print latpc_shadow_* and latpc_vm_* stats
- run only when explicitly enabled by a harmless config or environment variable

The shadow VM substrate must not:

- change any real simulator memory request
- change queue size
- change latency
- change scheduling
- change TLB/cache hit or miss behavior in the real simulator
- block or replay warps
- inject prefetches
- compress real MSHRs
- batch real page walks
- change IPC, cycles, instructions, or cache stats

## Subrounds

Run in order.

A20A: Requirements and scope.
A20B: Shadow VM architecture.
A20C: Implementation plan and gate.
A21A: Shadow VM core implementation.
A21B: Address hooks and stats print integration.
A21C: Runner integration and stats parser.
A22A: Build and behavior equivalence validation.
A22B: Shadow VM sanity and sensitivity checks.
A22C: Foundation report and readiness classification.
A23A: Timing integration decision.
A23B: Closeout and review pack.

## Inputs

Use latest reports from A16, A17/A18, and A19.

Important inputs:

.local_reports/A16A_latpc_selected_workload_*.json
.local_reports/A16C_latpc_experiment_results_*.csv
.local_reports/A18D_latpc_stats_only_validation_*.md
.local_reports/A19A_latpc_vm_tlb_ptw_scope_*.md
.local_reports/A19B_latpc_vm_module_scan_*.csv
.local_reports/A19C_latpc_hook_mapping_*.csv
.local_reports/A19D_latpc_foundation_assessment_*.md
.local_reports/A19E_latpc_foundation_closeout_*.md

Paper:

docs/accelsim_bringup/paper/2025_MICRO_LATPC_TLB_Prefetch_MSHR.pdf

Selected workload from A16 and A19:

nw

## Expected implementation mode

Preferred mode:

SHADOW_VM_ADDRESS_OBSERVATION

Meaning:

- use effective address or per-lane address observation
- derive VPN-like values
- maintain shadow VM/TLB/PTW state
- do not modify real timing

Fallback mode:

DESIGN_ONLY_BLOCKED

Use only if no safe address hook exists or build-system risk is too high.

Do not attempt timing integration in A20-A23. A23A should decide how to do timing in a later round.

## Suggested config or environment variables

Prefer environment variables to avoid changing existing config parser unless the parser is already easy to extend.

Recommended variables:

ACCELSIM_LATPC_SHADOW_VM=1
ACCELSIM_LATPC_SHADOW_PAGE_SHIFT=12
ACCELSIM_LATPC_SHADOW_L1_ENTRIES=32
ACCELSIM_LATPC_SHADOW_L2_ENTRIES=1024
ACCELSIM_LATPC_SHADOW_L1_MSHR_ENTRIES=16
ACCELSIM_LATPC_SHADOW_L2_MSHR_ENTRIES=128
ACCELSIM_LATPC_SHADOW_PTW_COUNT=16
ACCELSIM_LATPC_SHADOW_PWQ_ENTRIES=128
ACCELSIM_LATPC_SHADOW_PTW_LATENCY=300
ACCELSIM_LATPC_SHADOW_PWC_ENABLE=0

If using existing config is safer, document the config names and defaults.

Default must be disabled.

When disabled, only old A18 sentinel stats may print. No shadow state update should occur.

## Suggested default model

Page size:

- default page shift 12 for 4 KB pages

L1 TLB:

- per-SM if shader/core id is available
- fully associative
- default 32 entries
- LRU replacement

L2 TLB:

- global if no memory-partition-specific TLB model is available
- approximate set associative or fully associative
- default 1024 entries
- LRU replacement

MSHR:

- shadow structure only
- count allocation attempts, hits on outstanding VPN, successful allocations, reservation failures
- default L1 MSHR entries 16
- default L2 MSHR entries 128 if modeled

PTW:

- shadow only
- fixed number of walkers, default 16
- logical completion time based on current simulator cycle plus latency
- maintain a completion list or heap
- advance shadow completions up to current cycle before processing new observations
- insert completed translations into shadow TLBs
- do not stall real simulator

PWC:

- optional in first version
- if implemented, use simple fully associative caches for L1/L2/L3 page table levels
- if not implemented, mark PWC as DEFERRED

## Required stats naming

Use prefixes:

latpc_shadow_
latpc_vm_
latpc_tlb_
latpc_ptw_
latpc_pwc_

Keep A18 sentinel stats:

latpc_stats_only_marker
latpc_stats_only_version
latpc_functional_mechanism_enabled

Add:

latpc_shadow_vm_enabled
latpc_shadow_vm_version
latpc_shadow_page_shift
latpc_vm_warp_mem_inst_observed
latpc_vm_translation_request_total
latpc_vm_unique_vpn_total
latpc_vm_page_div_bin_1
latpc_vm_page_div_bin_2_3
latpc_vm_page_div_bin_4_7
latpc_vm_page_div_bin_8_15
latpc_vm_page_div_bin_16_31
latpc_vm_page_div_bin_32
latpc_vm_unique_stride_sample_total
latpc_vm_unique_stride_sum
latpc_vm_same_l4pt_translation_total
latpc_vm_l4pt_translation_total
latpc_tlb_l1_access_total
latpc_tlb_l1_hit_total
latpc_tlb_l1_miss_total
latpc_tlb_l2_access_total
latpc_tlb_l2_hit_total
latpc_tlb_l2_miss_total
latpc_tlb_l1_mshr_alloc_attempt
latpc_tlb_l1_mshr_alloc_success
latpc_tlb_l1_mshr_reservation_fail
latpc_tlb_l1_mshr_hit_under_miss
latpc_ptw_request_total
latpc_ptw_queue_enqueue_total
latpc_ptw_queue_full_event_total
latpc_ptw_queue_shadow_stall_cycle_total
latpc_ptw_walk_issue_total
latpc_ptw_walk_complete_total
latpc_pwc_l1_hit_total
latpc_pwc_l1_miss_total
latpc_pwc_l2_hit_total
latpc_pwc_l2_miss_total
latpc_pwc_l3_hit_total
latpc_pwc_l3_miss_total

Derived stats should be generated in scripts, not necessarily printed by simulator:

latpc_vm_multi_translation_fraction
latpc_vm_avg_unique_stride
latpc_vm_same_l4pt_fraction
latpc_tlb_l1_miss_rate
latpc_tlb_l2_miss_rate
latpc_tlb_l1_mshr_reservation_failure_rate
latpc_ptw_avg_shadow_queue_stall

## Output files

A20A:

.local_reports/A20A_latpc_vm_substrate_requirements_<timestamp>.md
.local_reports/A20A_latpc_vm_substrate_requirements_<timestamp>.csv

A20B:

.local_reports/A20B_latpc_shadow_vm_architecture_<timestamp>.md
.local_reports/A20B_latpc_shadow_vm_architecture_matrix_<timestamp>.csv

A20C:

.local_reports/A20C_latpc_substrate_implementation_plan_<timestamp>.md
.local_reports/A20C_latpc_source_file_plan_<timestamp>.csv
.local_reports/A20C_latpc_implementation_gate_<timestamp>.csv

A21A:

.local_reports/A21A_latpc_shadow_vm_core_impl_<timestamp>.md
.local_reports/A21A_latpc_shadow_vm_core_files_<timestamp>.csv

A21B:

.local_reports/A21B_latpc_shadow_vm_hooks_stats_<timestamp>.md
.local_reports/A21B_latpc_hook_integration_matrix_<timestamp>.csv
.local_reports/A21B_latpc_modified_source_files_<timestamp>.csv

A21C:

.local_reports/A21C_latpc_runner_integration_<timestamp>.md
.local_reports/A21C_latpc_runner_matrix_<timestamp>.csv

A22A:

.local_reports/A22A_latpc_shadow_vm_build_equiv_<timestamp>.md
.local_reports/A22A_latpc_behavior_compare_<timestamp>.csv
.local_logs/A22A_<timestamp>_build.log
.local_logs/A22A_<timestamp>_baseline.log
.local_logs/A22A_<timestamp>_shadow_vm.log

A22B:

.local_reports/A22B_latpc_shadow_vm_sanity_sensitivity_<timestamp>.md
.local_reports/A22B_latpc_shadow_vm_sanity_<timestamp>.csv
.local_reports/A22B_latpc_shadow_vm_sensitivity_<timestamp>.csv
.local_logs/A22B_<timestamp>_*.log

A22C:

.local_reports/A22C_latpc_shadow_vm_foundation_report_<timestamp>.md
.local_reports/A22C_latpc_shadow_vm_readiness_matrix_<timestamp>.csv

A23A:

.local_reports/A23A_latpc_timing_integration_decision_<timestamp>.md
.local_reports/A23A_latpc_timing_integration_plan_<timestamp>.csv

A23B:

.local_reports/A23B_latpc_vm_substrate_closeout_<timestamp>.md
.local_reports/A23B_latpc_vm_substrate_checklist_<timestamp>.csv
.local_reports/A23B_latpc_git_status_<timestamp>.txt
.local_reports/A23B_latpc_git_diffstat_<timestamp>.txt
.local_reports/A23B_latpc_source_patch_<timestamp>.diff
review_packs/A20_A23_LATPC_VM_SUBSTRATE_review_pack_<timestamp>.tar.gz

## Status labels

PASS:
Shadow VM substrate implemented, build passed, selected workload ran, behavior was unchanged, and non-trivial shadow VM stats were emitted.

PASS_WITH_WARNINGS:
Core substrate ran, but some fields are approximate, PWC is deferred, or sensitivity trends are weak.

PASS_DESIGN_ONLY:
Design was completed but safe source implementation was blocked.

BLOCKED_NO_A19_CONTEXT:
A19 reports are missing and source hooks cannot be reconstructed.

BLOCKED_NO_ADDRESS_HOOK:
No safe effective-address or per-lane address hook exists.

FAIL_BUILD:
Build failed after source changes.

FAIL_RUN:
Selected workload failed.

FAIL_BEHAVIOR_CHANGED:
Shadow VM enabled changed standard simulator stats.

FAIL_STATS_EMPTY:
Shadow VM ran but all important VM/TLB/PTW counters are zero or absent.

FAIL_DIRTY_TREE:
Unexpected runtime outputs or unrelated files remain in git status.

## Git policy

There are two git repositories to consider:

1. Top-level Accel-Sim repository:
   /workspace/repos/accel-sim-framework

2. Nested simulator repository:
   /workspace/repos/accel-sim-framework/gpu-simulator/gpgpu-sim

If simulator source under the nested repository is modified, commit it inside the nested repository first.

Suggested nested commit message:

sim: add LATPC shadow VM stats substrate

Then commit top-level docs and scripts.

Suggested top-level commit message:

scripts: add LATPC VM substrate pipeline

Do not push.

Do not use:

git add .
git add -A

Only add explicit paths.

Never commit runtime outputs:

.local_reports
.local_logs
.local_runs
.local_traces
review_packs
trace directories
build outputs
hw_run outputs

## Review pack requirements

A23B review pack must include:

- A20-A23 guidance docs
- A20-A23 scripts
- A20-A23 latest local reports
- A22 logs
- source patch diff
- git status and diffstat
- list of modified source files
- final summary
- readiness checklist

The review pack must not include:

- full trace directories
- build directories
- unrelated old reports
- paper PDF unless it was already tracked
- another review pack

## Final Codex response requirements

Report:

1. final status
2. top-level commit hash
3. nested simulator commit hash, if any
4. review pack path
5. selected workload
6. implementation mode
7. modified source files
8. key shadow VM stats observed
9. behavior validation result
10. A22C readiness classification
11. A23A timing decision
12. key report paths A20A through A23B
13. final git status --short for top-level and nested repo
14. clear statement that A20-A23 implemented only a shadow VM substrate, not LATPC Regularity Detector, LATC, LATP, or paper speedup reproduction
