# START — Recovery V3 V10 Pipelined Continue

Use this as an in-place continuation of the already-running Recovery-V3 Goal. Do not restart completed work.

## Handoff

```text
branch: hrl/vm-c16-g-retry570-chatgpt-handoff-v10
base active checkpoint: bc4abe769eb548140fd97ce95ff0e6ebe7323331
```

Read:

```text
docs/vm_tlb/codex_handoff/c16/retry570/C16_RECOVERY_V3_GPU_PIPELINE_SCHEDULING_DELTA.md
```

The delta supersedes any earlier serialized interpretation of v9. All scientific/storage/model-scope rules from v9 remain unless this delta explicitly changes scheduling/budget scope.

## Immediate actions

1. Snapshot current transfer worker PID/state and byte progress. Do not discard partial AWQ transfer.
2. Build the current `GPU_READY_QUEUE` from actual R2 receipts and live asset/input availability.
3. If the queue is non-empty, stop merely polling AWQ rsync.
4. Cleanly pause the remote write-heavy transfer before the next timing-sensitive GPU window.
5. Run the highest-priority ready GPU row.
6. Resume AWQ transfer after the GPU window and cleanup.
7. Continue alternating/overlapping preparation and GPU execution so the rented GPU is not idle behind unrelated transfers.

## Current expected ready/near-ready work

Check receipts rather than assuming, but the active branch already contains evidence that makes these the first candidates:

```text
Qwen2.5-7B raw S1 follow-up / Decode-side qualification / next scenario
Qwen2.5-0.5B S1-S4 R3 native baseline+census
Llama S1-S4 as soon as missing bindings are closed
Qwen2.5-7B raw S2-S4
```

Do not wait for Qwen2.5-7B-AWQ transfer to finish before doing the above.

When AWQ transfer/hash closure completes, enqueue AWQ immediately.

Prepare Qwen3-8B and DeepSeek R2 inputs/admission CPU-side concurrently.

Qwen3-30B-A3B remains `EXCLUDED_BY_USER_CURRENT_CAMPAIGN`.

## Historical budget ledgers

Do not reset or rewrite historical ledgers.

Do not use a consumed legacy diagnostic ledger as a permanent blocker for newly authorized Recovery-V3 deployment/scenario/phase work.

Create fresh campaign-scoped budget namespaces for genuinely new R5/R6 rows, while retaining the 4GiB/20min/one-capture-process hard bounds.

Do not repeat an already closed exact capability-limited target merely because a fresh scope exists; move to independent scientifically justified work.

## Status reporting while running

Periodically report compactly:

```text
GPU_READY_QUEUE_COUNT=
GPU_ACTIVE_JOB=
GPU_UTILIZATION_STATE=
REMOTE_TRANSFER_JOB=
REMOTE_TRANSFER_STATE=RUNNING|PAUSED_FOR_MEASUREMENT|COMPLETE
LOCAL_PREP_JOBS=
NEXT_GPU_JOB=
WHY_GPU_IDLE=
```

A long-running transfer is not an acceptable `WHY_GPU_IDLE` when another GPU row is ready.

## Final behavior

Continue the existing full Goal through R9. Do not stop for ordinary implementation problems. Preserve rolling copyback to `/root/share/c16_recovery_v3`, SHA closure, no large root-disk payloads, and zero remote-only required artifacts at closeout.
