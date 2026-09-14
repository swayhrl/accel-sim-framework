# START — Lane B transfer/storage V12

Use Goal mode.

This lane is deliberately **not** a throughput lane while the rented GPU has ready scientific work. Its job is to keep remote artifacts safe and prevent storage pressure from stopping Lane A.

Read:

```bash
git fetch origin hrl/vm-c16-g-retry570-v0 hrl/vm-c16-g-retry570-chatgpt-handoff-v12

git show origin/hrl/vm-c16-g-retry570-chatgpt-handoff-v12:docs/vm_tlb/codex_handoff/c16/retry570/v12/C16_GPU_FIRST_MULTI_WINDOW_HANDOFF_V12.md
```

Do not mutate the active Git worktree. Do not run model workloads, nsys, NVBit, NCU, or create `MEASUREMENT_ACTIVE`.

## Primary goal

Maintain artifact safety and storage headroom with **minimal interference** to Lane A.

Read-only state sources:

- `/root/autodl-tmp/c16_retry570/control/GPU_PIPELINE_STATE.json`
- `/root/autodl-tmp/c16_retry570/control/COPYBACK_QUEUE.json`
- latest active-G compact receipts/manifests

## Policy

### free >= 80 GiB

- do not start ordinary large copyback;
- do not run multi-GB remote SHA scans;
- verify that new `COPYBACK_READY` artifacts already have remote size/SHA/manifest;
- retain remote sources;
- local copyback may wait.

### 50 GiB <= free < 80 GiB

- copy back closed artifacts in batches between formal GPU windows;
- use `GPU_IO_EXCLUSION.lock` with non-blocking/GPU-priority semantics;
- stop/yield when Lane A needs the lock.

### free < 50 GiB

- storage becomes a real GPU blocker;
- tell Lane A to defer new large raw capture;
- copy back already remote-SHA-closed artifacts;
- delete remote copies only after local bytes/SHA equality and cleanup receipt.

## Never delete without

```text
remote bytes known
remote SHA256 known
local copy complete
local bytes == remote bytes
local SHA256 == remote SHA256
transfer receipt written
```

## Do not do now unless explicitly needed to create GPU work

- Qwen7-AWQ full-package remote SHA;
- large model uploads;
- archival compression;
- deep filesystem reorganization.

Those actions are lower priority than a nonempty GPU queue.

## Shared queue state

Advance artifact state only through:

`COPYBACK_READY -> COPYING -> LOCAL_SHA_CLOSED -> REMOTE_CLEANED`

If no transfer is needed because free space is healthy, leave it `COPYBACK_READY`; that is acceptable and not a Goal failure.

## Report cadence

Do not busy-spin. Recheck at reasonable intervals or when Lane A publishes a state change.

Report:

```text
REMOTE_DATA_FREE_BYTES=
COPYBACK_READY_COUNT=
COPYING_COUNT=
LOCAL_SHA_CLOSED_COUNT=
REMOTE_CLEANED_COUNT=
REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=
REMOTE_IO_LOCK_STATE=
GPU_ACTIVE_JOB=
GPU_READY_QUEUE_COUNT=
TRANSFER_ACTION_THIS_CYCLE=
```

Goal remains active until the rental campaign stops or a higher-level closeout explicitly ends it.