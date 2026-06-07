# A19B LATPC module scan guidance

## Goal
Scan code base to locate candidate files, classes, and functions for VM/TLB/PTW/PWC

## Required script
scripts/accelsim/a19b_latpc_module_scan.py

## Tasks
1. Search gpu-simulator/gpgpu-sim/src for:
   - L1/L2 TLB, MSHR allocation functions
   - PTW page table walker issue/complete
   - PW queue enqueue/dequeue/stall
   - PWC lookup/insert
   - Warp memory instruction address sources
   - LD/ST coalescer functions
2. For each found item, record:
   - path
   - symbol name
   - line numbers
   - confidence (HIGH/MEDIUM/LOW)
   - preliminary safe-hook yes/no
3. Output CSV + MD report

## Output files
.local_reports/A19B_latpc_vm_module_scan_<timestamp>.md
.local_reports/A19B_latpc_vm_module_scan_<timestamp>.csv
