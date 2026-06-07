# A17C LATPC minimal mechanism design guidance

## Goal

Synthesize a concrete LATPC design plan for this repository based on A17A paper requirements and A17B code localization.

A17C should tell future rounds exactly where and how to implement LATPC, while keeping A18 limited to stats-only instrumentation.

## Required script

Create:

scripts/accelsim/a17_latpc_design_synthesizer.py

## Inputs

Latest A17A files:

.local_reports/A17A_latpc_mechanism_requirements_*.csv
.local_reports/A17A_latpc_target_stats_from_paper_*.csv

Latest A17B files:

.local_reports/A17B_latpc_code_localization_matrix_*.csv
.local_reports/A17B_latpc_code_localization_*.md

## Required output files

.local_reports/A17C_latpc_minimal_design_<timestamp>.md
.local_reports/A17C_latpc_future_implementation_plan_<timestamp>.csv

## Design principles

Preserve these principles:

1. A18 is stats-only.
2. A20 and later can implement mechanisms.
3. Baseline behavior must remain identical when LATPC mechanisms are disabled.
4. Every mechanism should have a disabled default.
5. Mechanism implementation should be separable:
   - detect-only
   - latc_only
   - latp_only
   - latpc
6. Do not combine LATC and LATP before each is validated independently.

## Required design sections

The MD design must include:

1. Current repository support summary

Classify each foundation component as:

- PRESENT_HIGH_CONFIDENCE
- PRESENT_PARTIAL
- NOT_FOUND
- UNKNOWN_REQUIRES_MANUAL_REVIEW

Components:

- warp memory instruction address source
- TLB coalescer or equivalent
- L1 TLB
- L1 TLB MSHR
- L2 TLB
- L2 TLB MSHR
- page walk queue
- page table walker
- page walk cache
- stats print path
- config path
- A16 runner reuse path

2. Regularity Detector future design

State where it should hook.

Stats-only A18 behavior:

- compute unique VPNs per warp memory instruction
- preserve lane order, do not sort
- compute adjacent VPN strides
- compute unique stride count
- compute same-L4-PT locality
- compute prefetch candidate translations
- emit only counters

Future A20 behavior:

- produce triples VPN, Stride, Index
- distinguish demand vs prefetch
- provide group metadata to TLB path
- add detector latency only when mechanism is enabled, not in stats-only

3. LATC future design

State where L1 TLB MSHR changes should be made.

Stats-only A18 behavior:

- count L1 TLB MSHR allocation attempts if hook exists
- count allocation successes if hook exists
- count reservation failures if hook exists
- estimate compressible groups from Regularity Detector stats
- do not change allocation decision

Future A21 behavior:

- add Base VPN, Stride, Valid Mask
- implement compressed MSHR match
- preserve subentry and replay semantics
- handle hit-under-miss and miss-under-miss
- maintain exact release semantics

4. LATP future design

State where PTW/PW buffer changes should be made.

Stats-only A18 behavior:

- count PTW requests
- count queue stall cycles if available
- count same-L4-PT potential batching
- do not issue extra requests
- do not suppress page walks

Future A22 behavior:

- add Valid Mask and Stride to PW buffer if present
- preserve L1-L3 page walk logic
- batch or coalesce L4 walks only when safe
- ensure PTE fill and MSHR release order is correct

5. Stats-only implementation design

Define where the counters should live.

Preferred order:

- existing simulator stats object if clear
- existing TLB/PTW class stats if clear
- a small latpc stats helper included from one existing compiled unit
- as a last resort, partial script-only extraction and PASS_DESIGN_ONLY

Avoid adding new .cc files unless build system updates are simple and explicit.

6. Validation design

A18 must compare baseline vs stats-only for:

- cycles
- instructions
- IPC
- L2 accesses
- L2 misses

The comparison should use exact equality for integer fields and strict relative tolerance for floating fields.

7. Risk register

Include at least these risks:

- no VM/TLB model in current tree
- TLB code exists but no per-warp VPN hook
- stats print path difficult to extend
- instrumentation accidentally changes timing
- build-system changes are brittle
- NW trace too small or not TLB-pressure representative
- some paper metrics require approximation

## Future implementation plan CSV columns

Include at least:

- future_round
- mechanism
- target_component
- target_path
- planned_change
- a18_status
- implementation_risk
- validation_needed
- notes

Future rounds to include:

- A19 variant/config framework
- A20 Regularity Detector detect-only to functional metadata
- A21 LATC implementation
- A22 LATP implementation
- A23 LATPC integration
- A24 targeted validation
- A25 NW paper-style result

## Status rules

PASS:
Design completed and A18 path is clear.

PASS_WITH_WARNINGS:
Design completed but some target components are partial or missing.

BLOCKED_FOUNDATION_MISSING:
No safe A18 instrumentation path exists.

## Do not do

Do not edit simulator source.
Do not implement counters in A17C.
