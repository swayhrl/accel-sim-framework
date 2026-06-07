# A24B LATPC detector-ready stats and sampled VPN stride dump

## Round name

A24B_LATPC_DETECTOR_READY_STATS_AND_SAMPLE_DUMP

## Purpose

A24B makes the A20-A23 shadow VM substrate detector-ready for A25.

A24B does not implement the Regularity Detector. It only exposes enough raw counters, derived CSV fields, and sampled warp VPN/stride sequences so A25 can implement and validate the detector.

Do not inject prefetch requests.
Do not compress MSHRs.
Do not modify timing behavior.
Do not claim speedup reproduction.

## LATPC detector context

The paper Regularity Detector conceptually observes the unique VPN stream for one warp memory instruction after TLB coalescing and produces tuples like:
  VPN, Stride, Index

For A24B, collect detector-ready observations only:
- unique VPN sequence per warp memory instruction
- stride sequence between adjacent unique VPNs
- unique stride count
- same L4 page table group key
- page divergence count
- hook exactness metadata

Keep the original coalescer or thread/lane order. Do not sort VPNs for detector samples unless the existing A20-A23 substrate already did so and changing it would be risky. If order is approximate, report it clearly.

## Implementation task 1: raw detector-ready counters

Add or verify raw stats in latpc_shadow_vm.h and print path.

Recommended numeric stats:
- latpc_detector_warp_sample_total
- latpc_detector_multivpn_warp_total
- latpc_detector_unique_vpn_per_warp_sum
- latpc_detector_stride_adjacent_sample_total
- latpc_detector_unique_stride_per_warp_sum
- latpc_detector_same_l4_warp_total
- latpc_detector_same_l4_translation_total
- latpc_detector_l4_translation_total
- latpc_detector_stride_zero_total
- latpc_detector_stride_pos_1_total
- latpc_detector_stride_neg_1_total
- latpc_detector_stride_pos_2_7_total
- latpc_detector_stride_neg_2_7_total
- latpc_detector_stride_pos_8_31_total
- latpc_detector_stride_neg_8_31_total
- latpc_detector_stride_pos_32_511_total
- latpc_detector_stride_neg_32_511_total
- latpc_detector_stride_out_of_9bit_total
- latpc_detector_stride_irregular_warp_total

Existing A20-A23 stats should remain:
- latpc_vm_warp_mem_inst_observed
- latpc_vm_translation_request_total
- latpc_vm_unique_vpn_total
- latpc_vm_page_div_bin_1
- latpc_vm_page_div_bin_2_3
- latpc_vm_page_div_bin_4_7
- latpc_vm_page_div_bin_8_15
- latpc_vm_page_div_bin_16_31
- latpc_vm_page_div_bin_32
- latpc_vm_unique_stride_sample_total
- latpc_vm_unique_stride_sum
- latpc_vm_same_l4pt_translation_total
- latpc_vm_l4pt_translation_total
- latpc_tlb_l1_access_total
- latpc_tlb_l1_miss_total
- latpc_tlb_l1_mshr_alloc_attempt
- latpc_tlb_l1_mshr_reservation_fail
- latpc_tlb_l2_access_total
- latpc_tlb_l2_miss_total
- latpc_ptw_request_total
- latpc_ptw_queue_shadow_stall_cycle_total
- latpc_ptw_walk_complete_total

If duplicate naming already exists, keep existing names and add a mapping table in the report rather than creating redundant stats.

## Implementation task 2: derived stats CSV

Add a script, preferably:
  scripts/accelsim/a24_latpc_derive_detector_ready_stats.py

The script should parse one or more simulator output logs or stats files and write:
  .local_reports/A24B_latpc_detector_ready_derived_stats_<timestamp>.csv

Required CSV columns:
- run_id
- workload
- variant
- stat_source_path
- warp_mem_inst_observed
- translation_request_total
- unique_vpn_total
- multi_translation_fraction
- avg_unique_vpn_per_warp
- avg_unique_stride_count
- same_l4_fraction
- l1_miss_rate
- l2_miss_rate
- l1_mshr_fail_rate
- ptw_request_per_translation
- ptw_shadow_stall_avg_per_ptw_request
- page_div_bin_1_fraction
- page_div_bin_2_3_fraction
- page_div_bin_4_7_fraction
- page_div_bin_8_15_fraction
- page_div_bin_16_31_fraction
- page_div_bin_32_fraction
- stride_zero_fraction
- stride_pos_1_fraction
- stride_neg_1_fraction
- stride_pos_2_7_fraction
- stride_neg_2_7_fraction
- stride_pos_8_31_fraction
- stride_neg_8_31_fraction
- stride_pos_32_511_fraction
- stride_neg_32_511_fraction
- stride_out_of_9bit_fraction
- hook_address_mode
- hook_sm_id_mode
- hook_cycle_mode
- limitation

Derived formulas:
- multi_translation_fraction = multivpn_warp_total / warp_mem_inst_observed
- avg_unique_vpn_per_warp = unique_vpn_per_warp_sum / warp_mem_inst_observed
- avg_unique_stride_count = unique_stride_per_warp_sum / warp_mem_inst_observed or existing unique_stride_sum / unique_stride_sample_total if only existing stats are available
- same_l4_fraction = same_l4_translation_total / l4_translation_total
- l1_miss_rate = l1_miss_total / l1_access_total
- l2_miss_rate = l2_miss_total / l2_access_total
- l1_mshr_fail_rate = l1_mshr_reservation_fail / l1_mshr_alloc_attempt
- ptw_request_per_translation = ptw_request_total / translation_request_total
- ptw_shadow_stall_avg_per_ptw_request = ptw_queue_shadow_stall_cycle_total / ptw_request_total

Division by zero must produce blank or 0 with a clear note, not a crash.

## Implementation task 3: sampled VPN stride dump

Add optional sample dump support in the shadow VM path.

Recommended environment variables:
- ACCELSIM_LATPC_SAMPLE_DUMP
  - 0 or unset: disabled
  - 1: enabled
- ACCELSIM_LATPC_SAMPLE_LIMIT
  - default 64
  - maximum hard cap 256 unless the user overrides in code intentionally
- ACCELSIM_LATPC_SAMPLE_PATH
  - default .local_reports/latpc_shadow_vm_samples.csv if safe
  - otherwise default current working directory file name and record path

Required CSV header:
  sample_index,sm_id,warp_id,pc,cycle,address_count,unique_vpn_count,unique_vpn_seq,stride_seq,unique_stride_count,same_l4_key,page_div_count,hook_address_mode,hook_sm_id_mode,hook_cycle_mode

Encoding rules:
- PC may be hex or decimal, but be consistent.
- unique_vpn_seq should use a compact separator such as pipe.
- stride_seq should use a compact separator such as pipe.
- Do not print unbounded per-lane addresses.
- Do not dump more than the limit.
- Do not dump sample data to stdout except a short status line.

Sample dump must not alter simulator timing or control flow.

## Implementation task 4: sample dump validation

Run NW with:
  ACCELSIM_LATPC_SHADOW_VM=1
  ACCELSIM_LATPC_SAMPLE_DUMP=1
  ACCELSIM_LATPC_SAMPLE_LIMIT=64

Verify:
- sample CSV exists.
- sample CSV has a header.
- sample CSV has at least one row if shadow VM observed warp memory instructions.
- unique_vpn_count and stride_seq look plausible.
- behavior metrics remain identical to shadow run without sample dump.

## Reports to produce

Write:
- .local_reports/A24B_detector_ready_stats_impl_<timestamp>.md
- .local_reports/A24B_sample_dump_validation_<timestamp>.md
- .local_reports/A24B_latpc_detector_ready_derived_stats_<timestamp>.csv
- .local_reports/A24B_sample_dump_manifest_<timestamp>.md

Each report must include:
- start time
- end time
- wall seconds
- status
- commands
- output summary
- blocker
- limitations

Long logs go to .local_logs.

## Git rules

If simulator source changed, commit in nested repo first with explicit paths:
  cd gpu-simulator/gpgpu-sim
  git add src/gpgpu-sim/latpc_shadow_vm.h src/abstract_hardware_model.cc src/gpgpu-sim/gpu-sim.cc
  git commit -m "feat(latpc): add detector-ready shadow VM stats and samples"

If top-level scripts changed, commit in top-level repo with explicit paths:
  git add scripts/accelsim/a24_latpc_derive_detector_ready_stats.py
  git commit -m "tools(accelsim): add LATPC detector-ready stats derivation"

Never use git add . or git add -A.
Never push.
Do not commit .local_reports, .local_logs, .local_runs, .local_traces, review_packs, traces, or build outputs.

## A24B completion checklist

- Detector-ready raw stats are printed or mapped from existing stats.
- Derived stats CSV script exists and works on at least one NW shadow run.
- Sample dump is optional and capped.
- Sample dump contains PC, warp id, sm id, unique VPN sequence, stride sequence, same-L4 key, page divergence count.
- Sample dump does not change behavior metrics.
- Reports clearly state exact, approximate, and deferred fields.
- No Regularity Detector, LATC, LATP, prefetch, MSHR compression, or speedup claim is added.
