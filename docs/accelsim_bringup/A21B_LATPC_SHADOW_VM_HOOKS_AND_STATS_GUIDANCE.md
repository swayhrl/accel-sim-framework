# A21B LATPC shadow VM hooks and stats guidance

## Goal

Hook the shadow VM model into a safe address observation path and stats print path.

A21B may modify nested simulator source only if A20C gate allowed source implementation.

## Inputs

A20C gate.
A21A core implementation report.
A19 hook mapping.
A18 stats print location.

## Hook requirements

### Address hook

Use the safe address or effective-address hook identified in A19/A20C.

The hook should capture one warp memory instruction if possible.

Pass to the shadow VM observe function:

- SM or shader id if available
- warp id if available
- PC if available
- current cycle if available
- active lane addresses
- active mask if available

If only memory request addresses are available and not per-warp instruction addresses:

- hook may still be used as approximate address observation
- mark hook quality as APPROX_MEMORY_REQUEST_LEVEL
- do not claim warp-instruction exact page divergence

### Avoid double counting

A19 found address observation hooks may be generic. If the hook may be called multiple times for one instruction, add a warning in the report.

Do not add complicated de-dup by PC/cycle unless safe.

### Stats print hook

Extend the same stats print path used by A18 sentinel stats.

Print:

- A18 sentinel stats
- shadow VM enabled flag
- shadow VM config values
- raw shadow VM counters

All printed stats must have stable names.

### Environment enable

Initialize shadow config from environment on first use or simulator init.

Recommended:

ACCELSIM_LATPC_SHADOW_VM=1

Default disabled.

If disabled, observe hook should return immediately.

## Required reports

.local_reports/A21B_latpc_shadow_vm_hooks_stats_<timestamp>.md
.local_reports/A21B_latpc_hook_integration_matrix_<timestamp>.csv
.local_reports/A21B_latpc_modified_source_files_<timestamp>.csv

Hook integration matrix columns:

- hook_name
- component
- source_path
- source_symbol
- exactness
- data_available
- behavior_affecting
- risk
- notes

Exactness values:

- WARP_INSTRUCTION_LEVEL
- APPROX_MEMORY_REQUEST_LEVEL
- PRINT_ONLY
- UNAVAILABLE

Modified source files CSV columns:

- path
- repo
- modification
- lines_estimate
- behavior_change_expected
- notes

## Required self-check

After edits:

- run git diff --stat in nested repo
- inspect modified source manually
- confirm no timing/control path was changed
- record diffstat in report

## Status rules

PASS:
Address hook and stats print hook integrated.

PASS_WITH_WARNINGS:
Only approximate address hook available, but stats print works.

PASS_DESIGN_ONLY:
Source implementation blocked.

FAIL_NO_ADDRESS_HOOK:
No address hook could be safely integrated.

FAIL_SOURCE_RISK:
Hook would require behavior change.

## Do not do

Do not implement Regularity Detector.
Do not implement LATC compressed MSHR.
Do not implement LATP prefetch or batching.
Do not add real stalls or wakeups.
