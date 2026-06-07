# A22B LATPC shadow VM sanity and sensitivity guidance

## Goal

Run bounded sanity and sensitivity checks for the shadow VM substrate.

This stage should prove the substrate is not only printing markers, but is collecting non-trivial address-derived VM/TLB/PTW stats.

## Required script

Create:

scripts/accelsim/a22b_latpc_shadow_vm_sanity_sensitivity.py

## Inputs

A22A successful outputs.
A21C runner matrix.
A20B architecture.

## Required runs

Run at most these rows on selected workload NW:

1. shadow_vm_default
2. shadow_vm_small_tlb
3. shadow_vm_large_tlb

Do not rerun baseline unless needed.

## Required sanity checks

Check extracted stats.

Core presence:

- latpc_shadow_vm_enabled == 1
- latpc_vm_translation_request_total exists
- latpc_tlb_l1_access_total exists
- latpc_tlb_l1_miss_total exists
- latpc_tlb_l2_access_total exists
- latpc_ptw_request_total exists

Non-triviality:

- translation_request_total > 0
- l1_access_total > 0
- page divergence bin sum > 0
- at least one of l1_miss_total, l2_miss_total, or ptw_request_total > 0 unless documented as trace not translating

Consistency:

- l1_hit + l1_miss should be close to l1_access
- l2_hit + l2_miss should be close to l2_access
- page divergence bin sum should be close to warp_mem_inst_observed or documented denominator
- same_l4pt_translation_total <= l4pt_translation_total
- mshr reservation fail <= mshr alloc attempt
- walk_complete <= walk_issue unless pending completions remain at end and are documented

Sensitivity expectations:

- small TLB should not have fewer L1 misses than large TLB, unless approximation or trace effects are documented
- large TLB should generally reduce or not increase L1 miss rate
- smaller MSHR may increase reservation fail rate
- bigger PTW count may reduce shadow queue stall

Do not hard fail on every sensitivity trend. Use PASS_WITH_WARNINGS if trends are weak but stats are valid.

## Required outputs

.local_reports/A22B_latpc_shadow_vm_sanity_sensitivity_<timestamp>.md
.local_reports/A22B_latpc_shadow_vm_sanity_<timestamp>.csv
.local_reports/A22B_latpc_shadow_vm_sensitivity_<timestamp>.csv
.local_logs/A22B_<timestamp>_default.log
.local_logs/A22B_<timestamp>_small_tlb.log
.local_logs/A22B_<timestamp>_large_tlb.log

## Sanity CSV columns

- check
- status
- value
- expected
- evidence_stat
- notes

## Sensitivity CSV columns

- metric
- default_value
- small_tlb_value
- large_tlb_value
- trend_status
- notes

## Status rules

PASS:
Core stats are non-trivial and consistency checks pass.

PASS_WITH_WARNINGS:
Core stats exist but some sensitivity trends are weak or approximate.

FAIL_STATS_EMPTY:
Stats absent or only sentinel markers.

FAIL_INCONSISTENT_STATS:
Core consistency checks fail badly.

FAIL_RUN:
Sensitivity runs failed.
