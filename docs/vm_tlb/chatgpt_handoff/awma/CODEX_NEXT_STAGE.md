# CODEX_NEXT_STAGE

Status: **ACTIVE MAINLINE — 174 GLOBAL ACCESS DETERMINISM CLOSURE**

Stage:

`AWMA_Q05_GLOBAL_ACCESS_DETERMINISM_CLOSURE_174NEW_V1`

Coordination branch:

`hrl/awma-q05-global-access-determinism-handoff-v1`

## node174-new — ACTIVE MAINLINE

Execute:

`docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE_174NEW_Q05_GLOBAL_ACCESS_DETERMINISM_V1.md`

Execution parent:

```text
hrl/awma-q05-lookup-stream-identity-174new-v1
42f7c134ac9f2d1b0d789ba455a7cea76703ab56
```

Recommended branch:

`hrl/awma-q05-global-access-determinism-174new-v1`

Required order:

1. mine existing per-PC dynamic-inst/active-lane/access counts;
2. freeze trace->GLOBAL coalescing source contract;
3. create timing-independent canonical trace instruction identity;
4. instrument pre-coalescing input + post-coalescing output at generation time;
5. close generation-to-VM UID conservation;
6. exact P34 10/80 neutrality control;
7. run only P34 0/80 as the primary comparison;
8. canonical cross-run diff and delta conservation;
9. add 5/80 only if scientifically needed;
10. classify the source of GLOBAL stream variation;
11. STOP.

Success marker:

`AWMA_Q05_GLOBAL_ACCESS_DETERMINISM_CLOSURE_174NEW_V1_COMPLETE_WITH_SCOPE`

## node109

Independent V2.1 side campaign continues.

Do not use or alter its in-progress results.

## Forbidden

No architecture mechanism or new parameter sweep:

- no faster-TLB design;
- no TLB capacity/port change;
- no PTW/PWC mechanism;
- no page-size/segmentation;
- no cache redesign.

If a scientific simulator defect is proven, diagnose and STOP rather than silently repairing the accepted baseline.

Finish report -> review pack -> hashes -> commit -> push -> remote verify -> clean -> STOP.
