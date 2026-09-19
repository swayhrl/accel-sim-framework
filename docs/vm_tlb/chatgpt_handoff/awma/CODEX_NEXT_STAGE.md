# CODEX_NEXT_STAGE

Status: **ACTIVE MAINLINE — VM PER-ACCESS COVERAGE REPAIR QUALIFICATION**

Stage:

`AWMA_VM_PER_ACCESS_COVERAGE_REPAIR_174NEW_V1`

Coordination branch:

`hrl/awma-vm-per-access-coverage-repair-handoff-v1`

## node174-new — ACTIVE MAINLINE

Execute:

`docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE_174NEW_VM_PER_ACCESS_COVERAGE_REPAIR_V1.md`

Execution parent:

```text
hrl/awma-q05-global-access-determinism-174new-v1
be82faf264e93396b4b7d4fd72078c7e4491e3e4
```

Recommended branch:

`hrl/awma-vm-per-access-coverage-repair-174new-v1`

Required sequence:

1. freeze prior translation-dependent results as legacy-undercoverage pending requalification;
2. directly count untranslated L1D/ICNT admissions in the legacy runtime;
3. prove source path;
4. implement isolated surgical per-access translation gate;
5. unit/synthetic regression;
6. enforce zero untranslated downstream admissions;
7. reproduce legacy P34;
8. run repaired P34 natural;
9. repaired target-I0 only if exact per-access semantics are clean;
10. produce minimal requalification plan;
11. STOP_FOR_SCIENTIFIC_REVIEW if repaired result materially changes claims.

Success marker:

`AWMA_VM_PER_ACCESS_COVERAGE_REPAIR_174NEW_V1_COMPLETE_WITH_SCOPE`

## node109

No active AWMA task.

Final V2.1 evidence is frozen at:

`8a9d96ceb00e36ebdfa3d56cc277f965fffa649c`

Do not start another GPU campaign.

## Forbidden

No TLB/PTW/cache architecture mechanism.

No broad historical replay.

No silent baseline replacement.

Routine source/build/test/telemetry/storage engineering is solve-and-continue.

Finish report -> review pack -> hashes -> commit -> push -> remote verify -> clean -> STOP.
