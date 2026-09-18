# CODEX_NEXT_STAGE

Status: **ACTIVE MAINLINE — 174 LOOKUP-MODEL VALIDITY**

Stage:

`AWMA_Q05_LOOKUP_MODEL_VALIDITY_CLOSURE_174NEW_V1`

Coordination branch:

`hrl/awma-q05-lookup-model-validity-handoff-v1`

## node174-new — ACTIVE MAINLINE

Execute:

`docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE_174NEW_Q05_LOOKUP_MODEL_VALIDITY_V1.md`

Execution parent:

```text
hrl/awma-q05-contextual-lookup-decomposition-174new-v1
07d8c3cdd414b0a881264df341685e864fed2761
```

Recommended branch:

`hrl/awma-q05-lookup-model-validity-174new-v1`

Required sequence:

1. audit 10/80 latency provenance;
2. mine existing lookup/retry/completion accounting;
3. close source semantics of probe-at-service-completion;
4. add disabled-by-default read-only launch-vs-completion residency telemetry;
5. neutrality gate at P34/P8 natural 10/80;
6. rerun only the bounded existing lookup points needed for fill-race explanation;
7. split translation accounting by address space;
8. classify model validity and claim boundary;
9. write future RTX4080 native calibration plan;
10. STOP.

Success marker:

`AWMA_Q05_LOOKUP_MODEL_VALIDITY_CLOSURE_174NEW_V1_COMPLETE_WITH_SCOPE`

## node109

No AWMA task.

Do not use the RTX4080 for calibration in this stage.

## Explicitly forbidden

No architecture mechanism:

- no faster-TLB design;
- no new TLB capacity/ports;
- no PTW/PWC optimization;
- no page-size/segmentation;
- no translation prefetch/speculation;
- no cache redesign.

Routine source/history/log mining, read-only telemetry, bounded diagnostic reruns and node164 storage are solve-and-continue.

Finish report -> review pack -> hashes -> commit -> push -> remote verify -> clean -> STOP.
