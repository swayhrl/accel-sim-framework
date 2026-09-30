# Authorized next step — CCE zero-init software counterfactual V1

Date: 2026-09-30

User approved one bounded follow-up after EXACT_LOSS_STATE_LIFETIME_RESIDUAL_PRESENT.

Scientific parent:
ad9a302a49cdb3b1e75a9bbf04dab819c362cb1a

Handoff branch:
hrl/awma-exact-loss-zero-init-handoff-v1

Handoff HEAD:
9413136d633615f3d56aa4c5f788f81cca3f0b41

Execution branch:
hrl/awma-exact-loss-cce-zero-init-removal-109-v1

Goal:
docs/vm_tlb/chatgpt_handoff/awma/exact_loss_zero_init_v1/CODEX_GOAL_109_CCE_ZERO_INIT_REMOVAL_V1.md

Scope:
- Lane G / node109 only
- frozen real T255/H896/V151936 shape only
- C0 accepted CCE exact vs one C1 init-aware accumulation counterfactual
- remove full dC pre-zero without changing FP32 accumulation, chunking, full gradients or BF16 output
- one NSYS causal check; no NCU
- no second shape/model, no 174, no hardware mechanism

Lane F and Lane E remain STOP.
R102 remains dormant awaiting real update authority.
