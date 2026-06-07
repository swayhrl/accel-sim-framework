# A20A LATPC VM substrate requirements guidance

## Goal

Define precise requirements for the minimal VM/TLB/PTW/PWC substrate needed before LATPC mechanisms can be implemented.

A20A is design and reporting only. It must not modify simulator source.

## Required script

Create:

scripts/accelsim/a20a_latpc_vm_substrate_requirements.py

## Inputs

Use latest A19 outputs:

.local_reports/A19A_latpc_vm_tlb_ptw_scope_*.md
.local_reports/A19B_latpc_vm_module_scan_*.csv
.local_reports/A19C_latpc_hook_mapping_*.csv
.local_reports/A19D_latpc_foundation_assessment_*.md
.local_reports/A19E_latpc_foundation_closeout_*.md

Use latest A16 workload selection:

.local_reports/A16A_latpc_selected_workload_*.json

Use LATPC paper facts from:

docs/accelsim_bringup/paper/2025_MICRO_LATPC_TLB_Prefetch_MSHR.pdf

## Required tasks

1. Load A19 foundation conclusion.
2. Confirm selected workload is NW or document fallback.
3. Define why a shadow VM substrate is needed.
4. Define minimum required components:
   - address observation
   - VPN derivation
   - L1 TLB model
   - L2 TLB model
   - shadow MSHR model
   - shadow PTW queue model
   - optional PWC model
   - stats print path
   - runner integration
5. Define what this substrate can and cannot prove.
6. Define the boundary between shadow reproduction and timing reproduction.
7. Write requirements report and CSV.

## Requirements CSV columns

Include at least:

- requirement_id
- component
- requirement
- source_from_a19
- needed_for
- a20_a23_action
- future_latpc_action
- risk
- notes

Required rows:

- address_observation
- vpn_derivation
- page_size_config
- per_sm_l1_tlb
- global_l2_tlb
- l1_tlb_mshr_shadow
- l2_tlb_mshr_shadow
- ptw_shadow_queue
- ptw_shadow_completion
- pwc_optional
- stats_print
- runner_env_enable
- behavior_equivalence
- sensitivity_knobs
- review_pack_patch_capture

## Report sections

The MD report must include:

1. A19 starting point.
2. Why not implement LATPC directly.
3. Shadow VM substrate definition.
4. Required components.
5. Non-goals.
6. Success criteria.
7. Risks.
8. A21 implementation prerequisites.

## Success criteria

A20A passes if:

- A19 context is found or reconstructed.
- Requirements are written.
- It is clear that A20-A23 are not functional LATPC implementation.

## Status rules

PASS:
All required outputs exist.

PASS_WITH_WARNINGS:
A19 context is partial but requirements are reconstructed.

BLOCKED_NO_A19_CONTEXT:
No A19 context and no safe reconstruction is possible.

## Output files

.local_reports/A20A_latpc_vm_substrate_requirements_<timestamp>.md
.local_reports/A20A_latpc_vm_substrate_requirements_<timestamp>.csv
