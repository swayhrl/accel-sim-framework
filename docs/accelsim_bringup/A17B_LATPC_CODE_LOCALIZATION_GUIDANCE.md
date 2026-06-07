# A17B LATPC code localization guidance

## Goal

Locate the current Accel-Sim code paths relevant to LATPC and classify whether they are safe for A18 stats-only instrumentation.

A17B is an analysis stage. It should not modify simulator source.

## Required script

Create:

scripts/accelsim/a17_latpc_code_locator.py

## Search roots

Search at least these roots if they exist:

gpu-simulator/
gpu-simulator/gpgpu-sim/
gpu-simulator/gpgpu-sim/src/
gpu-simulator/gpgpu-sim/src/gpgpu-sim/
gpu-simulator/gpgpu-sim/src/abstract_hardware_model.*
gpu-simulator/gpgpu-sim/configs/
scripts/accelsim/

Do not assume all paths exist. Record missing roots in the report.

## Required search terms

Use ripgrep or Python file scanning. Search for case-insensitive and case-sensitive variants.

Component search terms:

- tlb
- TLB
- translation
- page walk
- page_walk
- pagewalk
- walker
- PTW
- pw_queue
- page walk queue
- page table
- pte
- PTE
- mshr
- MSHR
- miss status
- coalesc
- coalescer
- ldst
- LDST
- ldst_unit
- shader_core_ctx
- warp_inst_t
- mem_fetch
- virtual address
- vaddr
- VPN
- page size
- page_size
- PWC
- page walk cache

Also search for existing stats print paths:

- print_stats
- visualizer_print
- stats
- shader_print
- cache_stats
- gpgpu_simulation_time
- gpu_sim_cycle
- dump
- fprintf

## Required localization targets

For each target below, produce best candidate paths, symbols, confidence, and safe-hook assessment.

1. Warp memory instruction address source
   - Where per-lane memory addresses are available.
   - Where active mask is available.
   - Where warp instruction memory operation type is known.

2. TLB coalescer or translation request coalescing
   - Where unique page/VPN requests are generated.
   - Whether order follows thread index.
   - Whether coalescer output is accessible.

3. L1 TLB
   - TLB access function.
   - Hit/miss decision.
   - TLB fill path.
   - TLB stats.

4. L1 TLB MSHR
   - Allocation path.
   - Reservation failure path.
   - Release path.
   - Subentry or replay path.

5. L2 TLB
   - Access path.
   - MSHR path.
   - Fill path.

6. Page walk queue
   - Enqueue/dequeue.
   - Queue full or queueing.
   - Stall tracking.

7. Page table walker or page walk buffer
   - Walk issue.
   - Walk completion.
   - PTE return path.
   - PWC lookup if present.

8. Stats print path
   - Where final simulator stats are printed.
   - Where new latpc_* stats could be emitted.

9. Config path
   - Whether adding an enable or metadata config is easy.
   - A18 should avoid behavior-changing config.

10. Existing A16 runner path
   - How to run NW baseline and no-op variants.
   - Which script should be reused by A18C.

## Symbol scan CSV columns

Include at least:

- search_term
- path
- line_number
- line_text
- component_guess
- confidence
- notes

## Localization matrix CSV columns

Include at least:

- requirement_id
- requirement_name
- component
- candidate_path
- candidate_symbol
- candidate_lines
- hook_type
- confidence
- safe_for_a18
- reason
- missing_reason
- next_action

hook_type should be one of:

- READ_ONLY_STATS
- COUNTER_INCREMENT_ONLY
- PRINT_ONLY
- CONFIG_METADATA_ONLY
- UNSAFE_BEHAVIOR_PATH
- NOT_FOUND

confidence should be one of:

- HIGH
- MEDIUM
- LOW
- NONE

safe_for_a18 should be one of:

- yes
- partial
- no

## Report requirements

The MD report must include:

1. Summary.
2. Search roots inspected.
3. High-confidence paths.
4. Medium-confidence paths needing manual review.
5. Missing or weak paths.
6. A18 instrumentation opportunities.
7. A18 instrumentation risks.
8. Recommendation for A17D readiness gate.

For each high-confidence path, include a short snippet or line reference. Do not paste huge files.

## Required output files

.local_reports/A17B_latpc_code_localization_<timestamp>.md
.local_reports/A17B_latpc_code_localization_matrix_<timestamp>.csv
.local_reports/A17B_latpc_symbol_scan_<timestamp>.csv

## Status rules

PASS:
At least one safe hook is found for warp VPN stats and one stats print path is found.

PASS_WITH_WARNINGS:
Some hooks are found but TLB or PTW paths are partial.

BLOCKED_FOUNDATION_MISSING:
No safe hooks for warp address/VPN stats and no TLB/PTW foundation is visible.

## Do not do

Do not edit simulator source.
Do not implement counters.
Do not run full benchmarks.
