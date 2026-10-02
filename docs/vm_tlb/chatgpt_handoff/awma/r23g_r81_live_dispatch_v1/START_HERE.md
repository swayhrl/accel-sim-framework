# START HERE — AWMA R23G R81 live mixed-dispatch validation

Date: 2026-10-02

User authorization: inherited from approved post-Round22 continuous execution.

Scientific parent:
`296263043f4949467b33c6c99a695ac5c139104d`

Parent decision:
`R22G_R81_DISPATCH_NOT_JUSTIFIED_FROM_EXISTING_EVIDENCE`

Accepted gap:
- RULE_U01 retrospective head-region response is favorable before dispatch cost;
- exact union fraction is not available before the head in the accepted runner;
- exact union publication + dispatch cost and real mixed-trajectory cache/transition effects are UNKNOWN.

This Goal measures exactly that missing software cost in one live runner.

Execution branch:
`hrl/awma-r23g-r81-live-dispatch-109-v1`

Lane G / node109 becomes the only GPU executor.
Lane F STOP after R22F1.
Lane E STOP.
R20 and R21A target-family lines remain CLOSED/STOP.

All CUDA/JIT/generation work must hold:
`/data/c16/locks/c16_gpu_campaign.lock`
