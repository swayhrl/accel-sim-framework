# Post-Round22 execution authorization

Date: 2026-10-02

User authorization: APPROVED.

The post-Round22 plan is now split into one GPU main task and two CPU-only parallel audits.

## Lane F / node109 — only new GPU task

Handoff:
`hrl/awma-r22f-r21a-family-localization-handoff-v1`

Execution:
`hrl/awma-r22f-r21a-family-localization-109-v1`

Starting HEAD:
`c4feee715bdb659d6549fc1f1af229b3604a93a0`

Goal:
`docs/vm_tlb/chatgpt_handoff/awma/r22f_r21a_family_localization_v1/LANE_F_R22F_R21A_FAMILY_LOCALIZATION_109_GOAL.md`

Purpose:
freeze semantic kernel families before profiling; separate ordering, TP forward/backward, deterministic auxiliary cost and non-TP response. Complete-model 5% is not a universal family gate. No Donline/holdout/hardware continuation in this Goal.

## Lane G / node109 — CPU-only

Handoff:
`hrl/awma-r22g-r81-dispatch-audit-handoff-v1`

Execution:
`hrl/awma-r22g-r81-dispatch-audit-109-v1`

Starting HEAD:
`a5fc03704a5ada9c150fc6bc635de4dbebffcccf`

Goal:
`docs/vm_tlb/chatgpt_handoff/awma/r22g_r81_dispatch_audit_v1/LANE_G_R22G_R81_DISPATCH_AUDIT_109_GOAL.md`

Purpose:
using accepted R81 data only, audit whether fixed RULE_U01 (legal_union_fraction<1% -> A3 else A0) can be computed online and remains favorable after cost ownership. No GPU work.

## Lane E / node174-new — CPU-only

Handoff:
`hrl/awma-r22e-c16-e1-family-audit-handoff-v1`

Execution:
`hrl/awma-r22e-c16-e1-family-audit-174new-v1`

Starting HEAD:
`807d89b32516843559d61e6c51dbbaee4675a660`

Goal:
`docs/vm_tlb/chatgpt_handoff/awma/r22e_c16_e1_family_audit_v1/LANE_E_R22E_C16_E1_FAMILY_AUDIT_174NEW_GOAL.md`

Purpose:
audit at most two existing C16/E1 family boundaries. At most one future local diagnostic proposal may survive. No GPU/simulator/new trace work.

## Resource policy

- F is the only task authorized for new CUDA/JIT/profiling.
- G/E are CPU-only.
- G may prepare on node109, but must avoid compile/heavy I/O during F formal timing.
- All F GPU work uses `/data/c16/locks/c16_gpu_campaign.lock`.
- node164 remains durable large-data authority.
- node174 must not stage large trace/raw.
- R20 remains CLOSED.
- Historical execution labels are not retroactively modified.
