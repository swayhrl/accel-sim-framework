# CODEX_NEXT_STAGE

Status: **ACTIVE MAINLINE — 174 CONTEXTUAL LOOKUP-PATH DECOMPOSITION**

Stage:

`AWMA_Q05_CONTEXTUAL_LOOKUP_PATH_DECOMPOSITION_174NEW_V1`

Coordination branch:

`hrl/awma-q05-contextual-lookup-decomposition-handoff-v1`

## node174-new — ACTIVE MAINLINE

Execute:

`docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE_174NEW_Q05_CONTEXTUAL_LOOKUP_PATH_DECOMPOSITION_V1.md`

Execution parent:

```text
hrl/awma-q05-context-effect-decomposition-174new-v1
b24edffd7a90fc6417b95c6d4198f5c40dcf0b35
```

Recommended branch:

`hrl/awma-q05-contextual-lookup-decomposition-174new-v1`

Required order:

1. close same-trace formal-isolated baseline addendum;
2. audit accepted 10-cycle L1 / 80-cycle L2 lookup service semantics;
3. implement disabled-by-default exact-Q05 target-only latency override;
4. P8/P34 neutrality controls + P34 prior-I0 reproduction;
5. P34 full L1/L2 latency matrix;
6. P8 reduced matrix;
7. compare zero-lookup path against I0;
8. optional force-L1-hit diagnostic only if zero/zero leaves >3% residual;
9. assess P8 screening equivalence;
10. STOP before architecture mechanism design.

Success marker:

`AWMA_Q05_CONTEXTUAL_LOOKUP_PATH_DECOMPOSITION_174NEW_V1_COMPLETE_WITH_SCOPE`

## node109

No AWMA task is active on node109.

The previous unattended side campaign is closed and the RTX4080 is released for user work.

## Forbidden

Do not start:

- TLB capacity/port mechanism sweeps;
- PTW/PWC mechanisms;
- page-size or segmentation;
- translation prefetch/speculation;
- cache redesign.

This is a bounded diagnostic latency decomposition only.

Routine source/build/runner/telemetry/storage engineering is solve-and-continue.

Finish report -> review pack -> hashes -> commit -> push -> remote verify -> clean -> STOP.
