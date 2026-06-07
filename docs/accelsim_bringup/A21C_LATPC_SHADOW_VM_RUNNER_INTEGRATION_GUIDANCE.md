# A21C LATPC shadow VM runner integration guidance

## Goal

Create or update scripts that can run the selected workload with shadow VM enabled and parse latpc shadow stats.

A21C should not modify simulator source unless necessary.

## Required script

Create:

scripts/accelsim/a21c_latpc_shadow_vm_runner.py

## Inputs

A16 selected workload JSON.
A16/A18/A19 existing runner scripts.
A21B hook integration report.

## Required behavior

The script should:

1. Locate selected workload, expected NW.
2. Reuse A16 variant command pattern where possible.
3. Build a run matrix with at least:
   - baseline_no_shadow
   - shadow_vm_default
4. Optionally include:
   - shadow_vm_small_tlb
   - shadow_vm_large_tlb
5. Set environment variables only for shadow VM rows.
6. Write command matrix CSV.
7. Support dry-run mode.
8. Do not run automatically if invoked with dry-run flag.
9. Provide helper parser for latpc_* stats.

A22A and A22B may call this runner.

## Environment rows

baseline_no_shadow:

- no ACCELSIM_LATPC_SHADOW_VM env var
- or ACCELSIM_LATPC_SHADOW_VM=0

shadow_vm_default:

- ACCELSIM_LATPC_SHADOW_VM=1
- ACCELSIM_LATPC_SHADOW_PAGE_SHIFT=12
- default entries

shadow_vm_small_tlb:

- ACCELSIM_LATPC_SHADOW_VM=1
- L1 entries 8
- L2 entries 64
- L1 MSHR entries 4
- PTW count 4

shadow_vm_large_tlb:

- ACCELSIM_LATPC_SHADOW_VM=1
- L1 entries 64
- L2 entries 2048
- L1 MSHR entries 32
- PTW count 32

## Required outputs

.local_reports/A21C_latpc_runner_integration_<timestamp>.md
.local_reports/A21C_latpc_runner_matrix_<timestamp>.csv

Runner matrix CSV columns:

- run_id
- workload
- variant
- env
- command
- cwd
- log_path
- expected_behavior_change
- notes

## Parser requirements

The parser should parse:

- standard stats: cycles, instructions, IPC, L2 accesses, L2 misses
- latpc_* stats in formats:
  - name = value
  - name: value
  - name value

Output extracted stats in later A22 scripts.

## Status rules

PASS:
Runner matrix and parser are ready.

PASS_WITH_WARNINGS:
Runner exists but some rows are dry-run only.

PASS_DESIGN_ONLY:
Shadow source implementation was blocked, runner records no-run mode.

FAIL_NO_A16_COMMAND:
Cannot reconstruct selected workload command.
