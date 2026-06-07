# A21A LATPC shadow VM core guidance

## Goal

Implement the core shadow VM/TLB/MSHR/PTW substrate, but only if A20C gate allows source implementation.

A21A may modify nested simulator source files.

It must not hook the model into behavior until A21B.

## Gate check

Before editing source, read:

.local_reports/A20C_latpc_implementation_gate_*.csv
.local_reports/A20C_latpc_substrate_implementation_plan_*.md

If gate says DESIGN_ONLY_BLOCKED, do not modify simulator source. Write reports and mark PASS_DESIGN_ONLY.

## Core implementation requirements

Implement a small, self-contained shadow VM model.

Recommended API names, adjusted to project style if needed:

- latpc_shadow_vm_init_from_env()
- latpc_shadow_vm_enabled()
- latpc_shadow_vm_observe_warp_addresses(...)
- latpc_shadow_vm_print_stats(FILE *f)
- latpc_shadow_vm_reset()
- latpc_shadow_vm_drain_until(cycle)

If C++ class style fits better:

- class latpc_shadow_vm_t
- method init_from_env
- method observe
- method print_stats
- method drain_until

## Core state

Config:

- enabled
- page_shift
- l1_entries
- l2_entries
- l1_mshr_entries
- l2_mshr_entries
- ptw_count
- pwq_entries
- ptw_latency
- pwc_enable

Stats:

- all raw stats listed in master guidance
- plus error/sanity counters:
  - latpc_shadow_observe_call_total
  - latpc_shadow_empty_address_observe_total
  - latpc_shadow_duplicate_observation_warning_total
  - latpc_shadow_dropped_due_to_mshr_full_total
  - latpc_shadow_dropped_due_to_pwq_full_total

TLB state:

- L1 TLB per SM if SM id available; otherwise one global approximate L1 TLB
- L2 TLB global
- fully associative LRU is acceptable for first version

MSHR state:

- track outstanding VPNs
- capacity limited
- release on shadow completion
- do not interact with real MSHR

PTW state:

- walker next available cycles
- pending completion events
- completion event contains vpn, sm id, completion cycle
- drain completions before new observation

PWC state:

- optional; if not implemented print PWC stats as 0 and mark PWC deferred in reports

## Observe algorithm

For one observed warp memory instruction:

1. Return immediately if shadow VM disabled.
2. Increment observe call counter.
3. Drain shadow completions up to current cycle or event index.
4. Collect active addresses.
5. Convert each address to VPN by address >> page_shift.
6. Deduplicate VPNs preserving first-seen order.
7. Update page divergence stats.
8. Update stride stats.
9. Update same L4 PT locality stats.
10. For each unique VPN:
    - increment L1 TLB access
    - if L1 hit: increment L1 hit and continue
    - if L1 miss: increment L1 miss
    - attempt L1 MSHR allocation or merge
    - if MSHR full: count reservation fail and continue
    - access L2 TLB
    - if L2 hit: insert into L1 and schedule/release shadow MSHR immediately or at same cycle
    - if L2 miss: enqueue shadow PTW request and schedule completion
11. Do not return any value that changes simulator behavior.

## Deduplication

Use at most 32 active lane addresses for a warp. If more are observed, process all available but increment a warning counter.

Preserve lane order.

Do not sort.

## Same L4 PT locality

Use:

l4pt_key = vpn >> 9

For a warp instruction, group unique VPNs by l4pt_key.

Update:

- latpc_vm_l4pt_translation_total += number of unique VPNs
- latpc_vm_same_l4pt_translation_total += number of translations in groups with size greater than 1
- optional group counter for groups with size greater than 1

## TLB replacement

Use simple LRU.

On hit:

- update last_used.

On insert:

- if existing entry for VPN, update last_used.
- else if invalid entry exists, fill it.
- else evict least recently used entry.

## MSHR model

When a miss reaches the MSHR:

- alloc_attempt++
- if outstanding same VPN exists:
  - hit_under_miss++
  - merge count++
  - do not allocate a new entry
- else if active entries >= capacity:
  - reservation_fail++
  - dropped_due_to_mshr_full++
  - do not schedule a PTW for this VPN
- else:
  - alloc_success++
  - add outstanding VPN

This is a shadow bottleneck model. It does not stall real execution.

## PTW model

Before scheduling a PTW request, check queue capacity.

- if pending requests >= pwq_entries:
  - queue_full_event++
  - dropped_due_to_pwq_full++ or schedule anyway depending on chosen model
  - document choice

Preferred for continuity:

- count queue full event
- still schedule request to keep shadow stats progressing
- record notes that this is a shadow approximation

Issue scheduling:

- find the walker with the smallest next available cycle
- issue_cycle = max(current_cycle, walker_next_available)
- shadow_stall += issue_cycle - current_cycle
- completion_cycle = issue_cycle + ptw_latency
- update walker_next_available = completion_cycle
- push completion event

On completion:

- page_walk_complete++
- insert VPN into L2 TLB
- insert VPN into L1 TLB for the recorded SM if possible
- release outstanding MSHR for VPN

## Required reports

.local_reports/A21A_latpc_shadow_vm_core_impl_<timestamp>.md
.local_reports/A21A_latpc_shadow_vm_core_files_<timestamp>.csv

Core files CSV columns:

- path
- repo
- action
- summary
- behavior_affecting
- notes

## Status rules

PASS:
Core model implemented or source files created, but not necessarily hooked.

PASS_WITH_WARNINGS:
Core model implemented with approximations.

PASS_DESIGN_ONLY:
A20C gate blocked source changes.

FAIL_BUILD_RISK:
Implementation would require risky build changes; stop before making them if possible.

## Important

Do not call the observe function from a real simulator path in A21A unless A21B is also being completed immediately and documented.

Do not change simulator behavior.
