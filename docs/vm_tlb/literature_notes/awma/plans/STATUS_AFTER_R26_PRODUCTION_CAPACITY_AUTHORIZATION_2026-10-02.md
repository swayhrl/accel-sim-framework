# Status after R26 production-capacity authorization

Date: 2026-10-02 (Asia/Shanghai)

This supersedes STATUS_AFTER_R25_REVIEW_2026-10-02.md only for current authorization.
Historical execution evidence, results and labels remain unchanged.

## Current state

- Lane G / node109: R26 AUTHORIZED / HANDOFF_READY. This publication does not
  establish that the node has started execution.
- Only new AWMA GPU authorization: `AWMA_R26_TIED_WEIGHT_PRODUCTION_CAPACITY_BOUNDARY_109_V1`.
- R25 / R24 / R23G remain COMPLETE / STOP.
- Lane F / R22F1 and Lane E / R22E remain STOP.
- R20 remains CLOSED.
- No node174/Accel-Sim, profiler, hardware/PPA, deployment or later-stage task.

The user accepted production-integration + real memory-feasibility validation
after the R25 review. Do not treat the attached older R23G-active context or
the historical M4 root files as current authorization.

## Exact launch authority

Repository: swayhrl/accel-sim-framework

Handoff branch:
`hrl/awma-r26-tied-weight-production-capacity-handoff-v1`

Handoff HEAD:
`67bb4c00236e52657130dd91ddf44fb6a2e22c87`

Handoff tree:
`309903b65d4c0aaf13a4506efb5a9ce93d508608`

Execution branch to create:
`hrl/awma-r26-tied-weight-production-capacity-109-v1`

Entry:
`docs/vm_tlb/chatgpt_handoff/awma/r26_tied_weight_production_capacity_v1/START_HERE.md`

Full Goal:
`docs/vm_tlb/chatgpt_handoff/awma/r26_tied_weight_production_capacity_v1/LANE_G_R26_TIED_WEIGHT_PRODUCTION_CAPACITY_109_GOAL.md`

Code parent: `2581b6592e79691c4c3e57fe31a339eba9f6b7dd`.
Scientific review parent: `b2ba7f67a46e95ba45073c2a4deb54ee83a5401a`.

## R26 scope

One integrated component, default C1 policy and explicit S2 capacity policy,
for tied-weight-only fine-tuning. Use the same accepted Llama-3.2-1B model and
ADOPTED_LLAMA_S0_T128_V1 token IDs. T=127, BF16 W, FP32 AdamW moments, frozen
optimizer/CCE meta and 32MiB FP32 tile rule.

Only physical batch increases by materialized repetition of the same frozen
sequence. This is neither new training content nor an independent data holdout.

B1 one/four/32-step consistency, checkpoint resume and policy-switch checks
precede implementation freeze. Then bracket natural complete-step CUDA OOM,
B in [1,512], clean process per trial; verify endpoints and a same-batch witness
3/3. Only one common-batch C1/S2 formal timing point is allowed.

Primary outcome: whether S2 passes the same complete training batch at which
C1 naturally OOMs. Target allocator savings alone do not answer this question.
Shared backbone/forward limits may produce a valid no-extension result.
Ceiling without OOM is right-censored, not negative and not permission to expand.

Timing and capacity remain separate. Repeated-batch consistency is not
convergence or task-quality evidence. No artificial ballast/VRAM limit, tile
tuning, offload, all-parameter training, new inputs/models or old-Goal restart.

## Resource and closure

All CUDA/JIT:
`/data/c16/locks/c16_gpu_campaign.lock`.

node164 retains large raw/checkpoint authority. Code and compact reports stay
in Git. Exact result commit/push/fetch-back SHA/tree, node164 verification,
campaign-process exit, lock release and clean worktree are required.

After R26 closure, STOP for review. No next-stage execution is automatic.

Plan: R26_TIED_WEIGHT_PRODUCTION_CAPACITY_PLAN_2026-10-02.md.
Authoring/remote publication receipt:
R26_HANDOFF_PUBLICATION_RECEIPT_2026-10-02.json.
