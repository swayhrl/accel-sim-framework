# A19A LATPC VM/TLB/PTW scope guidance

## Goal
Define the scope of A19: which modules, files, and simulator constructs will be inspected.

## Required script
scripts/accelsim/a19a_latpc_scope_define.py

## Tasks
1. List all relevant Accel-Sim/GPGPU-Sim modules:
   - L1 TLB, L2 TLB, MSHR
   - Page walk queue (PW Queue)
   - Page table walker (PTW)
   - Page walk cache (PWC)
   - LD/ST coalescer
   - warp instruction and per-lane address sources
2. Define expected stats hooks
3. Identify workload anchor: NW from A16
4. Document scope in CSV and MD

## Output files
.local_reports/A19A_latpc_vm_tlb_ptw_scope_<timestamp>.md
.local_reports/A19A_latpc_vm_tlb_ptw_scope_<timestamp>.csv
