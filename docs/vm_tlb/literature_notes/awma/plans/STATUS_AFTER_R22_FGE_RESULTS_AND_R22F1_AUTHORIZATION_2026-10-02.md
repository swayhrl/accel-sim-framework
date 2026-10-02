# Status after R22 F/G/E results and R22F1 authorization

Date: 2026-10-02

## Completed parallel round

### Lane E / 174-new
Execution:
`4fbef16c342fb409918aef7a3922c4f5334761ac`

Decision:
`R22E_EXISTING_EVIDENCE_DOES_NOT_JUSTIFY_NEW_DIAGNOSTIC`

Accepted interpretation:
- M32/M64 cross-CTA low-bit conversion duplication is real logical work;
- cost-inclusive same-output local sharing performance remains unmeasured;
- no clean same-semantic finite-sharing counterfactual is qualified;
- E1 RAW/AWQ local operator response is strongly shape/implementation dependent but not a pure bitwidth intervention;
- no new C16/E1 GPU/simulator diagnostic is authorized.

Disposition:
CLOSE current R22E audit. Preserve evidence gaps; do not reopen dequant-cache or RAW/AWQ hardware by rename.

### Lane G / node109 CPU-only
Execution:
`296263043f4949467b33c6c99a695ac5c139104d`

Decision:
`R22G_R81_DISPATCH_NOT_JUSTIFIED_FROM_EXISTING_EVIDENCE`

Accepted interpretation:
- fixed RULE_U01 retrospective head-region response is favorable before dispatch cost;
- exact upstream legal IDs exist, but union fraction is not produced before head;
- an exact union/unique or mask OR/popcount must be added;
- its cost and one-trajectory dense/direct transition effects are unmeasured;
- no hardware claim.

Disposition:
retain one software-validation proposal in backlog; do not run while R22F/R22F1 is the active GPU question.

### Lane F / node109
Execution:
`df0e8edd009ee1a56ba65b25b319e8a852f74d27`

Decision:
`R22F_R21A_FAMILY_RESULT_MIXED`

Accepted evidence:
- Aorder cleanly separates sorted-graph atomic from deterministic aggregation;
- profiled Aorder->Dready gross TP forward/backward improves ~3.392 us;
- parent NSYS attributes ~30.160 us deterministic auxiliary fixup cost, yielding a profiled net target-family regression;
- profiled non-target is essentially neutral;
- uninstrumented Aorder->Dready complete energy+force is CLEAR faster by ~13.955 us / 2.878%;
- therefore profiled family sum and uninstrumented complete timing conflict in sign.

No Donline, old holdout or hardware work is justified until this discrepancy is resolved.

## Authorized next GPU task

Only Lane F continues.

Handoff:
`hrl/awma-r22f1-oeq-lowoverhead-replay-handoff-v1`

Execution:
`hrl/awma-r22f1-oeq-lowoverhead-replay-109-v1`

Starting HEAD:
`a6ac7ae69fcbc978ce50e5cac926234b823edcf0`

Goal:
`docs/vm_tlb/chatgpt_handoff/awma/r22f1_oeq_lowoverhead_replay_v1/LANE_F_R22F1_OEQ_LOWOVERHEAD_REPLAY_109_GOAL.md`

Purpose:
capture exact real OAM-S TP call tensors/upstream gradients, replay the same sorted-graph atomic and deterministic OEQ calls with low-overhead CUDA-event timing, and determine whether the NSYS deterministic-fixup regression reflects low-overhead target-family elapsed.

No NSYS/NCU/NVBit/SASS/Accel-Sim/node174 compute.
No Donline/holdout in R22F1.

## Resource state

- F = only authorized GPU task.
- G = CPU-only backlog / STOP current round.
- E = STOP.
- R20 remains CLOSED.
- node164 remains durable raw authority.
