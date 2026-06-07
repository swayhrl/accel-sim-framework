# A18A LATPC stats field specification guidance

## Goal

Define the stats fields that A18 should implement or mark unavailable.

This is a specification stage. It may create scripts and reports, but should not modify simulator source.

## Required script

Create:

scripts/accelsim/a18_latpc_stats_field_spec.py

## Inputs

Latest A17A target stats:

.local_reports/A17A_latpc_target_stats_from_paper_*.csv

Latest A17D readiness matrix:

.local_reports/A17D_latpc_readiness_matrix_*.csv

## Required output files

.local_reports/A18A_latpc_stats_field_spec_<timestamp>.md
.local_reports/A18A_latpc_stats_field_spec_<timestamp>.csv

## Field naming rules

All new fields must start with:

latpc_

Do not reuse existing stat names.

Do not use ambiguous names that imply functional LATPC is implemented.

Use names that describe stats-only observation.

## Required stats fields and definitions

Warp and page divergence:

1. latpc_warp_mem_inst_total
   - Count warp memory instructions observed by the stats hook.

2. latpc_warp_mem_inst_with_translation_total
   - Count warp memory instructions for which VPN translation stats were collected.

3. latpc_translation_request_total
   - Count unique VPN translation requests observed across warp memory instructions.

4. latpc_page_div_bin_1
5. latpc_page_div_bin_2_3
6. latpc_page_div_bin_4_7
7. latpc_page_div_bin_8_15
8. latpc_page_div_bin_16_31
9. latpc_page_div_bin_32
   - Histogram by unique VPN count per warp memory instruction.

Stride and regularity:

10. latpc_unique_stride_sample_total
    - Count warp instructions with at least two unique VPNs and stride analysis.

11. latpc_unique_stride_sum
    - Sum of number of distinct adjacent VPN strides per analyzed warp instruction.

12. latpc_unique_stride_hist_0
13. latpc_unique_stride_hist_1
14. latpc_unique_stride_hist_2
15. latpc_unique_stride_hist_3
16. latpc_unique_stride_hist_4_plus
    - Histogram of distinct stride count.

17. latpc_stride_group_total
    - Number of detected consecutive same-stride groups.

18. latpc_prefetch_candidate_translation_total
    - Count non-base translations that could be represented as prefetch candidates in detect-only analysis.

L4 page table locality:

19. latpc_l4pt_locality_sample_total
    - Count warp instructions analyzed for same L4 PT locality.

20. latpc_same_l4pt_translation_total
    - Count translations that share the same L4 PT group as another translation in the same warp instruction, or count translations in same-L4 groups according to the chosen documented formula.

21. latpc_l4pt_translation_total
    - Denominator for same-L4 locality.

22. latpc_same_l4pt_group_total
    - Count groups of translations in the same L4 PT with group size greater than one.

TLB MSHR:

23. latpc_l1_tlb_mshr_alloc_attempt
24. latpc_l1_tlb_mshr_alloc_success
25. latpc_l1_tlb_mshr_reservation_fail
26. latpc_l1_tlb_mshr_current_occupancy_sum
27. latpc_l1_tlb_mshr_current_occupancy_samples
28. latpc_l1_tlb_mshr_max_occupancy

PTW and page walk:

29. latpc_ptw_request_total
30. latpc_ptw_queue_enqueue_total
31. latpc_ptw_queue_stall_cycle_total
32. latpc_ptw_queue_full_event_total
33. latpc_page_walk_issue_total
34. latpc_page_walk_complete_total
35. latpc_l4pt_walk_potential_batch_total

Translation latency:

36. latpc_translation_latency_sample_total
37. latpc_translation_latency_cycle_sum
38. latpc_translation_latency_cycle_min
39. latpc_translation_latency_cycle_max

Derived fields in reports, not necessarily raw simulator stats:

40. latpc_page_divergence_multi_translation_fraction
41. latpc_avg_unique_stride_count
42. latpc_same_l4pt_fraction
43. latpc_l1_tlb_mshr_reservation_failure_rate
44. latpc_avg_translation_latency

## Formula details

VPN calculation:

- For 4 KB pages, VPN = virtual_address >> 12.
- If page size is available in config, use page_size_bits.
- If page size is not available, use 12 and clearly document the approximation.

Unique VPN order:

- Preserve lane or thread-index order.
- Do not sort VPNs.
- Deduplicate VPNs while preserving first occurrence order.

Stride calculation:

- For adjacent unique VPNs, stride = VPN_i_plus_1 - VPN_i.
- For LATPC compatibility, also compute 9-bit stride value as stride modulo 512 when needed.
- Negative strides should remain visible in debug or derived stats.

Same L4 PT calculation:

- For 4 KB pages and x86-64 style 512-entry L4 leaf page table, same L4 PT group key = VPN >> 9.
- Count locality only within a warp memory instruction.

Page divergence bins:

- unique_vpn_count == 1 goes to bin_1.
- 2 to 3 goes to bin_2_3.
- 4 to 7 goes to bin_4_7.
- 8 to 15 goes to bin_8_15.
- 16 to 31 goes to bin_16_31.
- 32 or more goes to bin_32, but also record notes if greater than 32 occurs.

## Availability classification

Each field must be classified as:

IMPLEMENTED:
A18B source instrumentation will emit it.

DERIVED:
A18 scripts compute it from emitted stats.

APPROXIMATED:
It is computed using an approximate hook or assumption.

UNAVAILABLE:
No safe hook exists in this repository.

DEFERRED:
Reserved for A20 plus mechanisms.

## CSV columns

Include at least:

- stat_name
- category
- paper_figure_hint
- raw_or_derived
- required_hook
- formula
- availability_after_a17d
- implementation_plan
- validation_plan
- notes

## MD report sections

1. Summary.
2. Field list by category.
3. Implemented vs approximate vs unavailable.
4. Formulas.
5. A18B implementation instructions.
6. Known limitations.

## Status rules

PASS:
Spec generated for all required fields.

PASS_WITH_WARNINGS:
Spec generated, but many fields are unavailable due to A17D readiness.

BLOCKED_NO_A17D:
A17D readiness output is missing.
