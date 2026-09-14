# START — Lane A GPU execution V12.2

You are the sole GPU execution owner for the C16 Recovery-V3 rental RTX3090 campaign.

Read first:

```bash
git fetch origin hrl/vm-c16-g-retry570-v0 \
  hrl/vm-c16-g-routeb-producer-v0 \
  hrl/vm-c16-g-retry570-chatgpt-handoff-v12

git show origin/hrl/vm-c16-g-retry570-chatgpt-handoff-v12:docs/vm_tlb/codex_handoff/c16/retry570/v12/V12_2_Q1_FIRST_AND_CUTLASS_OWNER.md
```

Do not checkout/reset/merge the handoff branch or producer branch into the active scientific worktree.

Current reviewed active-G checkpoint:

```text
8f2e7cadf3f591548c5fbe5fe685d1d587fb6761
```

Current reviewed producer checkpoint:

```text
2b8ab6512ba60fd1c03144be5f6a3408834ef9bb
```

## P0 now: bounded CUTLASS owner resolution while waiting for Q1 integration

`ROUTE_B_MAP_RESULTS_V2` is terminal 34/36. The two failed rows are the leading CUTLASS functions. Continue only bounded owner-resolution work using a new ownership-observation mechanism.

Especially prioritize the Prefill CUTLASS because its unresolved ~38% phase-duration mass makes the >=70% duration gate impossible.

Do not:

- assign it to `libtorch_cuda.so` by assumption;
- infer owner from short kernel name;
- rerun an identical unresolved calibration repeatedly;
- widen scientific input/model/backend.

For every new attempt retain exact function/mangle/module/owner-source/path/SHA/status evidence.

## Q1 handoff preempts owner debugging

Poll read-only for a Lane-C integration checkpoint based on active-G, expected branch:

```text
hrl/vm-c16-g-routeb-q1-integration-v0
```

Once Lane C publishes `ROUTE_B_Q1_INTEGRATION_READY`, stop further CUTLASS debugging at the next safe measurement boundary and review/import only the minimal Q1 integration commits. Do not merge the whole divergent producer branch.

CPU-focused validation before GPU:

- producer tool builds against NVBit 1.7.5 / CUDA 12.4 / SM86;
- multi-launch sequence is stream-global;
- parser groups `(kernel_launch_id, warp_instruction_instance_id)`;
- terminal event count equals parsed lane-event count;
- actual serialized output cap is fail-closed;
- existing Q0 focused tests pass.

Then immediately run Q1 tiny-CUDA on RTX3090.

## Q1 GPU gate

Q1 must exercise at least two launches of the same exact instrumented function and direct GLOBAL load/store with predication.

PASS requires:

```text
valid nonzero GPU VA only on executing lanes
(static_index,mref_ordinal) exact whitelist closure
READ/WRITE labels correct
observed sequence globally monotonic across multiple launches
launch-scoped warp instance identity consistent
terminal_status=COMPLETE
overflow_count=0
drop_count=0
terminal.event_count == parsed event count
raw SHA closed
parse manifest SHA closed
```

If Q1 fails for an ordinary engineering reason, diagnose -> bounded fix -> focused CPU validation -> rerun the smallest Q1 gate. Do not stop the Goal unless there is a true external blocker.

## Q1 PASS -> Q2 immediately

Run Q2 on the frozen Llama Route-A bridge functions without waiting for final representative selection.

Preferred bounded Q2 anchors:

1. Prefill exact `indexSelectLargeIndex` function;
2. Decode exact `indexSelectSmallIndex` function.

For each function freeze all statically mapped `GLOBAL && has_mref` rows, not only the historic selected PC.

Q2 is the first new dynamic Llama Route-B address evidence. Preserve raw JSONL/manifest/SHA remotely and mark `COPYBACK_READY`; do not wait for Lane B copyback before continuing.

Q2 must compare the historic selected-PC subset against Route-A event/lane/bucket behavior but must not require absolute VA equality across independent processes.

## GPU state / transfer slot

Whenever GPU/measurement is active:

```text
transfer_slot_granted=false
```

Only when measurement is absent and GPU process count is zero may it become true.

Do not let idle Lane B ownership of the I/O lock block GPU work.

## After Q2

If both Q2 anchors pass but Prefill CUTLASS owner is still unresolved:

- retain Q2 as qualified producer evidence;
- do NOT invent representative formal capture;
- return to the unresolved owner or any newly frozen independent GPU row.

## Immediate reporting

After each checkpoint push report:

```text
CHECKPOINT_COMMIT=
GPU_ACTIVE_JOB=
Q1_STATUS=
Q2_PREFILL_STATUS=
Q2_DECODE_STATUS=
CUTLASS_PREFILL_OWNER_STATUS=
CUTLASS_DECODE_OWNER_STATUS=
REMOTE_SHA_CLOSED_COPYBACK_DEFERRED_COUNT=
NEXT_GPU_JOB=
GPU_IDLE_SECONDS=
```
