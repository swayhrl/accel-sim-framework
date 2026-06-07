# A17D LATPC readiness gate guidance

## Goal

Decide whether A18 can safely add stats-only instrumentation to the simulator source.

A17D is a gate. It must prevent speculative or unsafe modifications.

## Required script

Create:

scripts/accelsim/a17_latpc_readiness_gate.py

## Inputs

Latest A17B localization matrix:

.local_reports/A17B_latpc_code_localization_matrix_*.csv

Latest A17C design:

.local_reports/A17C_latpc_minimal_design_*.md
.local_reports/A17C_latpc_future_implementation_plan_*.csv

Latest A16 selected workload JSON:

.local_reports/A16A_latpc_selected_workload_*.json

## Required output files

.local_reports/A17D_latpc_readiness_gate_<timestamp>.md
.local_reports/A17D_latpc_readiness_matrix_<timestamp>.csv

## Readiness checks

Create one row per check.

Required checks:

1. paper_pdf_exists
2. a16_selected_workload_exists
3. selected_workload_is_nw_or_documented_fallback
4. a16_runner_or_command_path_found
5. warp_address_or_vpn_hook_found
6. unique_vpn_or_coalescer_hook_found
7. l1_tlb_hook_found
8. l1_tlb_mshr_hook_found
9. l1_tlb_mshr_reservation_failure_hook_found
10. l2_tlb_hook_found
11. ptw_or_page_walk_queue_hook_found
12. ptw_queue_stall_hook_found
13. stats_print_path_found
14. build_command_found
15. source_instrumentation_safe

Each row should include:

- check
- status
- evidence_path
- evidence_symbol
- confidence
- required_for_full_a18
- required_for_partial_a18
- notes

status values:

- PASS
- PARTIAL
- FAIL
- NOT_REQUIRED

## Readiness mode decision

At the end, assign one mode.

FULL_STATS_ONLY_INSTRUMENTATION:

Required:

- selected workload exists
- runner or command path exists
- warp address or VPN hook exists
- stats print path exists
- build command exists
- source instrumentation safe

Plus at least partial support for:

- L1 TLB MSHR reservation failure
- PTW or page walk queue

PARTIAL_STATS_ONLY_INSTRUMENTATION:

Required:

- selected workload exists
- runner or command path exists
- at least one safe stats hook exists
- stats print path or log extraction path exists
- build command exists

DESIGN_ONLY_BLOCKED:

Use when:

- no safe stats hook exists
- or stats print path cannot be found and no log extraction is possible
- or source instrumentation would require speculative behavior-path changes
- or selected workload cannot be run

## MD report required sections

1. Gate summary.
2. Chosen readiness mode.
3. Checks that passed.
4. Checks that are partial.
5. Checks that failed.
6. A18B permission:
   - allowed full instrumentation
   - allowed partial instrumentation
   - source changes forbidden
7. Required caution notes for A18B.
8. Stop condition if blocked.

## Status rules

PASS:
Mode is FULL_STATS_ONLY_INSTRUMENTATION.

PASS_WITH_WARNINGS:
Mode is PARTIAL_STATS_ONLY_INSTRUMENTATION.

PASS_DESIGN_ONLY:
Mode is DESIGN_ONLY_BLOCKED but A17 design outputs are complete.

BLOCKED_FOUNDATION_MISSING:
The tree lacks necessary VM/TLB/PTW foundation and no safe source hook exists.

## Important instruction for Codex

If A17D mode is DESIGN_ONLY_BLOCKED, do not edit simulator source in A18B. Continue with A18A stats spec and A18E closeout, and mark A18B/A18C/A18D as blocked or design-only as appropriate.
