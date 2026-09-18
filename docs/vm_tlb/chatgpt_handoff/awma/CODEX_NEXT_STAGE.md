# CODEX_NEXT_STAGE

Status: **ACTIVE MAINLINE — 174 CONTEXTUAL REPLAY**

Stage:

`AWMA_Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_174NEW_V1`

Coordination branch:

`hrl/awma-q05-contextual-replay-handoff-v1`

## node174-new — ACTIVE MAINLINE

Execute:

`docs/vm_tlb/chatgpt_handoff/awma/CODEX_RESUME_174NEW_Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_V1.md`

Execution parent:

```text
hrl/awma-q05-warm-prefix-replay-174new-v1
5b9d708087e8ff485f03fd561a15e08baea8ad3a
```

Recommended branch:

`hrl/awma-q05-contextual-warm-prefix-replay-174new-v1`

Formal producer authority:

```text
hrl/awma-q05-prefix-ldc-recovery-109-v1
c6733012c13099c6a86f506fd8c61e351791159e
```

Durable bundle:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native-contiguous-prefix_q05-contiguous-prefix_20260918T022749Z_1fea2d955d1c`

Expected execution:

1. independent 174 consumer/hash/order/context validation;
2. bring forward only the narrow exact-LDC validator semantic patch;
3. fold F0 boundary wording/state cleanup into this run;
4. recompute translation-relevant page overlap using actual VM-entry spaces;
5. create new context-input identities;
6. run P1/P2/P4/P8/P16/P34 contextual rows from fresh simulator processes;
7. collect Q05-only translation + L2-data-cache deltas;
8. compare contextual rows with accepted isolated Q05;
9. report and STOP before any mechanism experiment.

Success marker:

`AWMA_Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_174NEW_V1_COMPLETE_WITH_SCOPE`

## node109

Mainline GPU requirement is currently released.

No mainline GPU task is active while 174 runs.

Side work may run only if separately authorized, is preemptible, and cannot delay a future mainline GPU request.

Do not auto-start unrelated model campaigns or cleanup from this handoff.

## Explicitly forbidden

Do not automatically start:

- new TLB/PTW/cache mechanisms;
- I0 contextual mechanism sweeps;
- latency/capacity/page-size/walker sweeps;
- Segment;
- changing F0 cache/TLB persistence semantics;
- rewriting the formal 109 context bundle;
- forcing broad trace-page overlap to equal TLB residency.

Routine parser/driver/index/telemetry engineering is solve-and-continue when scientific semantics stay unchanged.

Finish report -> review pack -> hashes -> commit -> push -> remote verify -> clean -> STOP.
