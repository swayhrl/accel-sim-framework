# A18B LATPC stats-only instrumentation guidance

## Goal

Implement safe stats-only instrumentation according to A17D readiness and A18A stats field spec.

A18B is the only stage in A17 plus A18 that may modify simulator source.

## Gate requirement

Before editing simulator source, read latest:

.local_reports/A17D_latpc_readiness_gate_*.md
.local_reports/A17D_latpc_readiness_matrix_*.csv
.local_reports/A18A_latpc_stats_field_spec_*.csv

If A17D mode is DESIGN_ONLY_BLOCKED:

- Do not modify simulator source.
- Write A18B summary with status PASS_DESIGN_ONLY or BLOCKED_FOUNDATION_MISSING.
- Continue to A18E closeout.

If A17D mode is PARTIAL_STATS_ONLY_INSTRUMENTATION:

- Modify only the safe hooks marked by A17D.
- Mark unavailable fields clearly.

If A17D mode is FULL_STATS_ONLY_INSTRUMENTATION:

- Implement all safe counters possible in one pass.
- Still avoid speculative behavior-path edits.

## Preferred implementation strategy

Prefer minimal, low-risk changes.

Priority order:

1. Add counters to an existing stats object or existing simulator class with a known print path.
2. Add small helper functions inside an existing compiled source file if that avoids build-system changes.
3. Add a small header-only helper if several files need to update counters.
4. Add new .cc files only when the build system is simple and you update the relevant Makefile or CMake files explicitly.

Avoid large refactors.

Avoid changing public interfaces unless necessary.

## Counter ownership

Use a clear owner for latpc stats.

Acceptable patterns:

- gpgpu_sim or shader_core_stats owns global counters.
- TLB or VM manager owns TLB/PTW counters.
- A small latpc_stats struct is held by an existing simulator-level object.

Do not use uncontrolled global mutable state unless there is already an established simulator stats pattern. If a small global is the only practical option, document why and keep it simple.

## Stats print requirement

At simulator end, emitted stats must include lines with names beginning with latpc_.

Example format:

latpc_warp_mem_inst_total = 12345
latpc_page_div_bin_1 = 1000
latpc_l1_tlb_mshr_reservation_fail = 42

Follow the repository's existing stat print style.

The parser in A18C must be able to extract these values.

## Warp VPN stats hook

Use the safest hook found by A17B/A17D.

Preferred data source:

- per-lane virtual addresses from a warp memory instruction before or during translation
- active mask or lane activity mask
- page size or page shift if available

Stats-only helper behavior:

1. Collect active-lane addresses for a warp memory instruction.
2. Convert virtual addresses to VPNs.
3. Deduplicate VPNs while preserving lane order.
4. Count unique VPNs.
5. Update page divergence bins.
6. Compute adjacent VPN strides.
7. Compute distinct stride count.
8. Detect consecutive same-stride groups.
9. Compute same L4 PT group key as VPN >> 9 for 4 KB pages.
10. Update prefetch candidate counts.

Do not sort VPNs.

Do not modify the instruction, requests, or queues.

Do not skip memory accesses.

## TLB MSHR stats hook

Use the safe L1 TLB MSHR allocation path found by A17B/A17D.

Counters:

- latpc_l1_tlb_mshr_alloc_attempt
- latpc_l1_tlb_mshr_alloc_success
- latpc_l1_tlb_mshr_reservation_fail
- latpc_l1_tlb_mshr_current_occupancy_sum
- latpc_l1_tlb_mshr_current_occupancy_samples
- latpc_l1_tlb_mshr_max_occupancy

Rules:

- Increment attempt before existing allocation decision.
- Increment success only when existing logic succeeds.
- Increment reservation_fail only when existing logic fails due to full or unavailable MSHR.
- Do not change allocation decision.
- Do not change entry contents.
- Do not change replay or release logic.

If the code does not expose exact success/failure, mark approximate or unavailable.

## PTW stats hook

Use the safe PTW or page walk queue hook found by A17B/A17D.

Counters:

- latpc_ptw_request_total
- latpc_ptw_queue_enqueue_total
- latpc_ptw_queue_stall_cycle_total
- latpc_ptw_queue_full_event_total
- latpc_page_walk_issue_total
- latpc_page_walk_complete_total
- latpc_l4pt_walk_potential_batch_total

Rules:

- Count events around existing enqueue/dequeue/issue/complete logic.
- Do not change queue length.
- Do not change walker availability.
- Do not change issue timing.
- Do not add PTE requests.
- Do not batch page walks.

If stall cycles are not directly available, approximate only if the approximation is clearly documented and cannot affect behavior.

## Translation latency stats

Only implement translation latency if start and end points are clearly available.

Counters:

- latpc_translation_latency_sample_total
- latpc_translation_latency_cycle_sum
- latpc_translation_latency_cycle_min
- latpc_translation_latency_cycle_max

Do not add new per-request state unless it is clearly safe and small.

If safe state tracking is not available, mark unavailable for A18.

## Source code style

Follow existing C++ style.

Avoid advanced C++ features not already used.

Keep changes small and local.

Use comments with prefix:

LATPC A18 stats-only:

Example comment:

LATPC A18 stats-only: count observed unique VPNs, does not affect timing.

## Required reports

Create:

.local_reports/A18B_latpc_stats_instrumentation_summary_<timestamp>.md
.local_reports/A18B_latpc_modified_files_<timestamp>.csv
.local_reports/A18B_latpc_stats_availability_matrix_<timestamp>.csv

Modified files CSV columns:

- path
- change_type
- reason
- behavior_change_expected
- stats_added
- notes

Stats availability matrix columns:

- stat_name
- availability
- source_file
- hook_symbol
- exact_or_approx
- notes

## Status rules

PASS:
Source instrumentation implemented for safe hooks and required reports exist.

PASS_WITH_WARNINGS:
Partial instrumentation implemented and unavailable fields are documented.

PASS_DESIGN_ONLY:
A17D blocked source changes and no source files were modified.

BLOCKED_FOUNDATION_MISSING:
No safe hooks exist.

FAIL_SOURCE_RISK:
Implementation would require behavior-path changes; stop and do not modify.

## Required self-check after source edits

Run:

git diff --stat

Inspect each modified simulator source file.

Confirm in the A18B report:

- no queue size changes
- no latency changes
- no scheduling changes
- no TLB hit/miss behavior changes
- no MSHR allocation behavior changes
- no PTW issue behavior changes
- no prefetch injection

## Do not commit yet

A18B should not commit by itself. Commit after A18E closeout.
