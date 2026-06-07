# A19C LATPC hook mapping guidance

## Goal
Map safe hooks for stats-only instrumentation.

## Required script
scripts/accelsim/a19c_latpc_hook_mapping.py

## Tasks
1. From A19B module scan CSV, select HIGH confidence symbols
2. Attempt to identify safe read-only stats hooks:
   - Warp memory instruction VPN collection
   - L1 TLB access / MSHR allocation
   - PTW enqueue/dequeue
   - PWC lookup/insert
3. Map each hook to a field defined in A18A stats spec
4. Document approximate hooks (if safe but limited) and unavailable hooks
5. Output CSV + MD report

## Output files
.local_reports/A19C_latpc_hook_mapping_<timestamp>.md
.local_reports/A19C_latpc_hook_mapping_<timestamp>.csv
