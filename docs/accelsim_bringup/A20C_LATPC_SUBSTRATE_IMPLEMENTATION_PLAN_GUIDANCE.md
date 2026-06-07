# A20C LATPC substrate implementation plan guidance

## Goal

Create a concrete source-file plan and implementation gate for A21.

A20C must decide whether source implementation is allowed and exactly where it should go.

A20C must not modify simulator source.

## Required script

Create:

scripts/accelsim/a20c_latpc_substrate_implementation_plan.py

## Inputs

A20A and A20B outputs.

A19 module scan and hook mapping.

Current git status for:

- top-level repo
- nested gpu-simulator/gpgpu-sim repo

## Required tasks

1. Inspect A19 high-confidence address observation hooks.
2. Inspect stats print path from A18.
3. Inspect build system risk.
4. Decide implementation mode:
   - SHADOW_VM_IMPLEMENTATION_ALLOWED
   - SHADOW_VM_PARTIAL_IMPLEMENTATION_ALLOWED
   - DESIGN_ONLY_BLOCKED
5. Produce source file plan.
6. Produce gate CSV.
7. Write MD report.

## Implementation mode criteria

SHADOW_VM_IMPLEMENTATION_ALLOWED:

- safe address or effective-address hook exists
- safe stats print path exists
- build command exists
- nested repo source can be modified and committed cleanly
- no known behavior-path modification is required

SHADOW_VM_PARTIAL_IMPLEMENTATION_ALLOWED:

- stats print path exists
- address hook exists but may be approximate or duplicated
- source changes can still be made safely
- report must label stats as approximate where needed

DESIGN_ONLY_BLOCKED:

- no safe address hook
- or build system risk too high
- or source changes would require real behavior path changes

## Source file plan

Prefer one of these patterns.

Pattern A, preferred if build-system update is simple:

- add gpu-simulator/gpgpu-sim/src/gpgpu-sim/latpc_shadow_vm.h
- add gpu-simulator/gpgpu-sim/src/gpgpu-sim/latpc_shadow_vm.cc
- update the relevant Makefile or CMake file explicitly
- call observe function from safe address hook
- call print function from gpu-sim.cc stats print path

Pattern B, preferred if adding a new .cc file is risky:

- add gpu-simulator/gpgpu-sim/src/gpgpu-sim/latpc_shadow_vm.h
- implement small inline or header-local helper
- include it only from the safe hook source and gpu-sim.cc if necessary

Pattern C, fallback:

- implement a small local stats-only helper inside an existing compiled source file
- use this only if it avoids build-system risk
- document technical debt

Do not choose a pattern that requires large refactoring.

## Gate CSV columns

Include:

- gate_item
- status
- evidence_path
- evidence_symbol
- implementation_decision
- notes

Gate items:

- top_level_git_clean_before_start
- nested_git_clean_before_start
- selected_workload_available
- address_hook_available
- stats_print_available
- build_command_available
- source_file_pattern_selected
- behavior_preservation_plan_clear
- review_patch_capture_plan_clear
- source_implementation_allowed

## Source file plan CSV columns

Include:

- path
- repo
- action
- reason
- expected_change_size
- build_system_change_needed
- risk
- notes

## Required output files

.local_reports/A20C_latpc_substrate_implementation_plan_<timestamp>.md
.local_reports/A20C_latpc_source_file_plan_<timestamp>.csv
.local_reports/A20C_latpc_implementation_gate_<timestamp>.csv

## Status rules

PASS:
Implementation allowed and source plan is clear.

PASS_WITH_WARNINGS:
Partial implementation allowed.

PASS_DESIGN_ONLY:
Implementation blocked but design complete.

FAIL_DIRTY_TREE:
Unexpected git dirtiness before source implementation that is not explained.

## Important instruction

A21 must not modify simulator source unless A20C gate says implementation is allowed or partial implementation is allowed.
