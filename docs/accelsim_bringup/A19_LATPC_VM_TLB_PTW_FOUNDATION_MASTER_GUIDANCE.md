# A19 LATPC VM/TLB/PTW foundation master guidance

## Round name
A19_LATPC_VM_TLB_PTW_FOUNDATION

## Purpose
- Locate and assess Accel-Sim/GPGPU-Sim virtual memory, TLB, PTW, and PWC infrastructure.
- Determine which mechanisms (Regularity Detector, LATC, LATP) can safely hook in.
- Produce a set of readiness/foundation reports for A20 mechanism implementation.
- No LATPC functional implementation yet.

## Subrounds
- A19A: Scope definition and targets
- A19B: Module scan / symbol analysis
- A19C: Hook mapping and safe access points
- A19D: Foundation assessment and risk register
- A19E: Closeout, review pack, final recommendation

## Inputs
- Latest A17/A18 reports (A17A-D, A18A-E)
- A16 variant slot, NW workload
- LATPC paper

## Outputs
- Each subround has MD + CSV
- Review pack under review_packs/A19_LATPC_VM_TLB_PTW_FOUNDATION_review_pack_<timestamp>.tar.gz

## Status labels
PASS / PASS_WITH_WARNINGS / BLOCKED_NO_A16_CONTEXT / FAIL_BUILD / FAIL_NO_RESULTS

## Git rules
- Do not push
- Do not use git add . or git add -A
- Only add explicit tracked paths
