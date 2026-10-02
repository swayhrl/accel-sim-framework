# Status after R22F1 and R23G authorization

Date: 2026-10-02

## R22F1 closure

Execution:
`bb5c66c674007cc6c9a77549fb0f81528be30056`

Decision:
`R22F1_FAMILY_GAP_UNRESOLVED`

Accepted facts:
- exact real OAM-S frame55 TP call capture: two callsites, layer0/layer1, each one forward and one force backward;
- same-input atomic and deterministic replay passes the original 5e-5 output/required-gradient contract;
- low-overhead CUDA-event replay:
  - aggregate forward: Dready ~0.272 us slower
  - aggregate backward: Dready ~0.334 us faster
  - combined: Dready ~0.062 us faster (~0.029%)
- five combined group gaps change sign and fail the frozen 3xMAD gate;
- exact low-overhead fixup-only service time remains unknown;
- parent NSYS family negative, exact-input replay mixed, and parent full-model ready-graph positive remain separate evidence levels.

Disposition:
R21A/OEQ target-family line STOP.
No Donline, old holdout, additional profiler, frame/model sweep or hardware work.
The 2.878% complete-region response is not attributed to TP-family.

## E/G state from prior round

R22E remains STOP:
`R22E_EXISTING_EVIDENCE_DOES_NOT_JUSTIFY_NEW_DIAGNOSTIC`

R22G CPU audit remains accepted:
`R22G_R81_DISPATCH_NOT_JUSTIFIED_FROM_EXISTING_EVIDENCE`

The latter left exactly one bounded software-validation proposal because the missing quantity is directly measurable:
exact pre-head union computation + fixed RULE_U01 dispatch + real mixed A0/A3 trajectory cost.

## Authorized next GPU task

Lane G / node109 becomes the sole GPU executor.

Handoff:
`hrl/awma-r23g-r81-live-dispatch-handoff-v1`

Execution:
`hrl/awma-r23g-r81-live-dispatch-109-v1`

Starting HEAD:
`f981039d9289368cc32f761d6e5a79f91a775266`

Goal:
`docs/vm_tlb/chatgpt_handoff/awma/r23g_r81_live_dispatch_v1/LANE_G_R23G_R81_LIVE_DISPATCH_109_GOAL.md`

Purpose:
validate fixed RULE_U01 on a new public structured-generation cohort in one live mixed runner, charging exact CPU union OR+popcount, dispatch, A0/A3 internal costs and arm-transition/cache effects.

Frozen policy:
`legal_union_fraction < 0.01 -> A3; else A0`

No threshold/union-algorithm tuning.

Input source:
public `korotkov/glaive-function-calling-v2-parsed` test split, exact revision resolved/frozen before GPU work; deterministic hash-based row selection; no performance/sparsity-based selection.

This is a software execution validation only.
No hardware, NSYS/NCU/NVBit/SASS, node174 or Accel-Sim work.

## Resource state

- Lane G: only authorized GPU task.
- Lane F: STOP.
- Lane E: STOP.
- R20: CLOSED.
- R21A target-family line: STOP.
- node164 remains durable raw authority.
