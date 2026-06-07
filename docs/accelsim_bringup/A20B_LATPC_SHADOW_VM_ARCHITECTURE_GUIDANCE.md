# A20B LATPC shadow VM architecture guidance

## Goal

Define the architecture of the shadow VM/TLB/MSHR/PTW/PWC substrate.

A20B must not modify simulator source. It produces an architecture document that A21 will implement.

## Required script

Create:

scripts/accelsim/a20b_latpc_shadow_vm_architecture.py

## Inputs

Latest A20A outputs.

Latest A19 hook mapping and module scan.

## Architecture to specify

### Enable and defaults

The shadow VM substrate must be disabled by default.

Recommended enable variable:

ACCELSIM_LATPC_SHADOW_VM=1

Recommended defaults:

- page_shift = 12
- l1_entries = 32
- l2_entries = 1024
- l1_mshr_entries = 16
- l2_mshr_entries = 128
- ptw_count = 16
- pwq_entries = 128
- ptw_latency = 300
- pwc_enable = 0 in first implementation

These match the spirit of LATPC paper evaluation defaults but should be documented as a shadow model, not a faithful reproduction of the paper simulator.

### Address observation

Input data needed:

- shader or SM id if available
- warp id if available
- program counter if available
- per-lane effective addresses
- active lane mask
- current simulator cycle if available

Minimum acceptable input:

- a list of effective addresses for one warp memory instruction
- a current cycle or monotonic event counter

If current simulator cycle is not safely available, use an event index for shadow queue ordering and mark PTW stall cycles as approximate or unavailable.

### VPN derivation

For each active address:

vpn = address >> page_shift

Deduplicate unique VPNs while preserving lane order.

Do not sort.

### Page divergence

Update bins based on unique VPN count:

- 1
- 2 to 3
- 4 to 7
- 8 to 15
- 16 to 31
- 32 or more

### Stride and locality

Adjacent stride:

stride_i = vpn_i_plus_1 - vpn_i

Unique stride count is the number of distinct adjacent stride values.

Same L4 PT key:

l4pt_key = vpn >> 9

Reason:

4 KB page table page contains 512 PTEs, so 9 VPN bits select an entry within the L4 page table page.

### Shadow L1 TLB

Preferred:

- per-SM vector of fully associative entries
- LRU replacement using a monotonically increasing timestamp
- fields: valid, vpn, last_used

Fallback:

- global L1 TLB if SM id unavailable, clearly marked approximate

### Shadow L2 TLB

Preferred:

- global L2 TLB
- approximate fully associative LRU first
- default 1024 entries

Set-associative can be deferred unless easy.

### Shadow MSHR

Fields:

- valid
- vpn
- target_level
- allocate_cycle
- completion_cycle
- merged_count

Stats:

- alloc_attempt
- alloc_success
- reservation_fail
- hit_under_miss

Rules:

- if a VPN is already outstanding, count hit_under_miss and do not allocate another entry
- if capacity full, count reservation_fail and do not affect real simulation
- if capacity available, allocate and schedule shadow PTW or L2 completion

### Shadow PTW

Use a completion queue.

Before processing new observations:

- drain all completions with completion_cycle <= current_cycle
- insert completed VPNs into L2 and relevant L1
- release shadow MSHRs

When a page walk is needed:

- choose earliest available walker
- issue_cycle = max(current_cycle, walker_next_available_cycle)
- completion_cycle = issue_cycle + ptw_latency
- shadow_stall += issue_cycle - current_cycle if positive
- update walker_next_available_cycle
- enqueue completion event

PWQ capacity:

- if number of pending completions or pending requests exceeds pwq_entries, count queue_full_event
- still may schedule for stats continuity, but document this as shadow-only behavior

### Shadow PWC

First implementation may defer PWC.

If implemented:

- use separate small fully associative caches for L1/L2/L3 page table levels
- use page-table index keys derived from VPN
- count hit/miss only
- do not use it to change real behavior

### Stats print

Print raw counters only.

Derived metrics should be computed by scripts.

### Behavior preservation

The architecture must state exactly where the substrate is side-effect-free.

Allowed side effects:

- counter increments
- shadow state updates
- extra wall-clock runtime
- extra stats print lines

Forbidden side effects:

- real simulator data structure changes
- memory request changes
- scheduler changes
- queue changes
- latency changes

## Required output files

.local_reports/A20B_latpc_shadow_vm_architecture_<timestamp>.md
.local_reports/A20B_latpc_shadow_vm_architecture_matrix_<timestamp>.csv

## Architecture matrix columns

Include:

- component
- design_choice
- default_value
- implementation_location_preference
- fallback
- affects_real_timing
- validation_method
- notes

## Status rules

PASS:
Architecture is complete and implementable.

PASS_WITH_WARNINGS:
Architecture is complete but has approximations.

BLOCKED_NO_A20A:
A20A requirements missing.
