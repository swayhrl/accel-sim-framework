# A17A LATPC paper requirements guidance

## Goal

Extract and record LATPC paper requirements in a form that can guide code localization and stats-only instrumentation.

A17A is a documentation and script stage. It must not modify simulator source.

## Required script

Create:

scripts/accelsim/a17_latpc_paper_requirements.py

## Inputs

Paper:

docs/accelsim_bringup/paper/2025_MICRO_LATPC_TLB_Prefetch_MSHR.pdf

A16 context, if present:

.local_reports/A16A_latpc_paper_profile_*.md
.local_reports/A16A_latpc_selected_workload_*.json
.local_reports/A16E_latpc_final_summary_*.md

## Script behavior

The script should:

1. Record start time, end time, and wall seconds.
2. Check whether the LATPC paper PDF exists.
3. Try to extract PDF text with pdftotext if available.
4. Continue with manual paper facts if text extraction is unavailable.
5. Locate latest A16 selected workload JSON.
6. Write a paper requirements MD report.
7. Write a mechanism requirements CSV.
8. Write a target stats CSV.

## Manual paper facts to encode

Encode these facts directly in the script so that the report is robust even if PDF text extraction fails.

Paper identity:

- title: LATPC: Accelerating GPU Address Translation Using Locality-Aware TLB Prefetching and MSHR Compression
- venue: MICRO 2025
- simulator: Accel-Sim
- main idea: combine locality-aware TLB prefetching and TLB MSHR compression

Mechanism 1: Regularity Detector

- Located after the TLB coalescer.
- Input is unique VPNs from one warp memory instruction.
- Output is VPN, Stride, Index.
- Demand request uses Stride=0 and Index=0.
- Prefetch candidate uses non-zero Stride and non-zero Index.
- Processes VPNs in thread-index order from the coalescer output.
- Does not require sorting.
- Uses 9-bit stride logic to stay within a 512-page L4 page table boundary.
- Detect-only mode in A18 should record groups, strides, and candidate translations without injecting prefetches.

Mechanism 2: LATC

- Target is L1 TLB MSHR.
- Extends one valid bit to a 32-bit Valid Mask.
- Adds or tracks Base VPN and 9-bit Stride.
- One entry can represent up to 32 in-flight TLB misses from a warp instruction.
- The i-th Valid Mask bit corresponds to Base VPN + Stride * i.
- A18 must not implement compression; it should only locate MSHR reservation failures and potential compressible groups.

Mechanism 3: LATP

- Target is Page Table Walker or Page Walk Buffer.
- Exploits page table locality within one warp instruction.
- Uses same L4 PT locality because 512 PTEs fit in a 4 KB row.
- Conceptually keeps L1-L3 walks unchanged and extends L4 handling.
- A18 must not batch page walks; it should only record same-L4-PT locality and potential batching opportunities.

Evaluation facts:

- Default page size is 4 KB except large-page sensitivity.
- LATPC paper reports baseline without TLB prefetching.
- LATPC paper evaluates 24 workloads.
- Workloads include Rodinia NW, LUD, backprop, and BFS variants.
- A16 selected NW as the first trace-available anchor.

## Mechanism requirements CSV columns

Include at least:

- mechanism
- paper_section_hint
- paper_requirement
- required_sim_component
- required_hook
- a18_action
- future_a20_plus_action
- risk
- notes

Example rows:

- Regularity Detector, coalescer output, unique VPN stream, LDST or TLB coalescer, warp memory instruction unique VPNs, stats only group detection, future prefetch candidate generation, medium
- LATC, L1 TLB MSHR, valid mask and stride, L1 TLB MSHR allocation, reservation failure and MSHR occupancy, stats only potential compression, future compressed MSHR matching, high
- LATP, PTW or PW buffer, same L4 PT batching, page walk queue or PTW, PTW queue stall and page walk events, stats only locality potential, future L4 page walk batching, high

## Target stats CSV columns

Include at least:

- stat_name
- category
- paper_figure_hint
- exact_or_proxy
- formula_or_definition
- required_hook
- default_availability
- notes

Required target stats:

- latpc_warp_mem_inst_total
- latpc_translations_total
- latpc_page_div_bin_1
- latpc_page_div_bin_2_3
- latpc_page_div_bin_4_7
- latpc_page_div_bin_8_15
- latpc_page_div_bin_16_31
- latpc_page_div_bin_32
- latpc_unique_stride_samples
- latpc_unique_stride_sum
- latpc_unique_stride_hist_1
- latpc_unique_stride_hist_2
- latpc_unique_stride_hist_3
- latpc_unique_stride_hist_4_plus
- latpc_same_l4pt_translation_total
- latpc_l4pt_translation_total
- latpc_l1_tlb_mshr_alloc_attempt
- latpc_l1_tlb_mshr_alloc_success
- latpc_l1_tlb_mshr_reservation_fail
- latpc_ptw_request_total
- latpc_ptw_queue_stall_cycles
- latpc_translation_latency_samples
- latpc_translation_latency_cycles_sum
- latpc_prefetch_candidate_translations

## Required output files

.local_reports/A17A_latpc_paper_requirements_<timestamp>.md
.local_reports/A17A_latpc_mechanism_requirements_<timestamp>.csv
.local_reports/A17A_latpc_target_stats_from_paper_<timestamp>.csv

Optional:

.local_reports/A17A_latpc_paper_text_extract_<timestamp>.txt

## Status rules

PASS:
PDF exists and all required reports are written.

PASS_WITH_WARNINGS:
Manual facts are written but PDF text extraction failed.

BLOCKED_NO_PDF:
PDF is missing.

## Validation

Run:

python3 scripts/accelsim/a17_latpc_paper_requirements.py

Inspect latest A17A report and CSVs.

## Do not do

Do not modify simulator source.
Do not run full benchmarks.
Do not implement LATPC.
