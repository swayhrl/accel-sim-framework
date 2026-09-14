# START Lanes B/D — Primary-Model Support V12.3

Primary model is now exclusively:

```text
Llama-3.2-1B / S0 / B1-T128-Decode4
```

Read:

```text
docs/vm_tlb/codex_handoff/c16/retry570/v12/V12_3_PRIMARY_MODEL_COMPLETION_MODE.md
```

## Lane B — storage/copyback

Do not proactively drain all `COPYBACK_READY` artifacts while remote free space is safe.

Priority:

```text
GPU production
> remote SHA/manifest closure
> storage safety
> copyback
```

Rules:

- never hold `GPU_IO_EXCLUSION.lock` while idle;
- never transfer during `MEASUREMENT_ACTIVE` or when `transfer_slot_granted=false`;
- if remote free >=80 GiB, ordinary copyback may remain deferred;
- 50–80 GiB: batch copyback only between GPU windows;
- <50 GiB: storage relief becomes mandatory;
- never delete the only remote copy without local byte/SHA closure;
- prioritize Llama Q1/Q2/Route-B/Route-C artifacts if space pressure appears;
- unrelated AWQ package SHA or large transfers remain lower priority until Llama is complete.

Do not block Lane A on copyback.

## Lane D — paused/fallback-only

Pause broad model readiness expansion.

Do not work on Qwen/AWQ/Qwen3/DeepSeek/GLM unless Lane A explicitly requests one of:

1. a single already-frozen fallback GPU row because Llama is CPU-blocked >120s;
2. a missing local authority directly required to finish Llama;
3. emergency storage/runtime repair affecting the primary model.

Do not create new GPU-ready rows merely to increase queue depth.

If fallback is requested, prepare exactly that row and stop again after handoff.

## Reporting

Lane B:

```text
REMOTE_DATA_FREE_BYTES=
MEASUREMENT_ACTIVE=
TRANSFER_SLOT_GRANTED=
COPYBACK_PENDING_COUNT=
LLAMA_COPYBACK_PENDING=
REMOTE_IO_LOCK_STATE=
```

Lane D:

```text
STATE=PAUSED_PRIMARY_MODEL_MODE
FALLBACK_REQUESTED=
FALLBACK_READY=
BLOCKER_IF_ANY=
```
