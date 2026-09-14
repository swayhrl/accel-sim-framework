# C16 Recovery V3 — Dual-window coordination contract

## Purpose

Split the active Recovery-V3 Goal into two concurrent Codex windows so local/download/transfer/copyback work no longer serializes GPU execution, while preventing remote I/O from perturbing formal GPU measurements.

The two windows are workers in one campaign, not two independent scientific campaigns.

## Worker roles

### Worker G — GPU / measurement owner

Worker G is the **only** worker allowed to:

- change or deploy experimental/runtime/tracer code;
- own the active Git worktree/branch and create scientific commits;
- run GPU model baseline, nsys census, NVBit static map/canary/repro/formal capture;
- create/remove `MEASUREMENT_ACTIVE`;
- decide the GPU-ready queue and next GPU row;
- classify scientific/diagnostic outcomes.

### Worker T — transfer / local-prep owner

Worker T may:

- download exact-revision assets on the local/control host;
- consolidate models under `/root/share/c16_recovery_v3`;
- hash models/assets/raw payloads;
- create bindings or other CPU-only preparation from frozen receipts;
- upload models/bindings to GPU host;
- copy raw/profiler payloads back to `/root/share/c16_recovery_v3`;
- verify remote/local bytes + SHA;
- clean remote copies **only after** local SHA closure;
- maintain filesystem-side immutable transfer/copyback receipts.

Worker T must **not**:

- start model/GPU execution;
- arm measurement markers;
- run nsys/NVBit/NCU scientific windows;
- change tracer/runtime code;
- commit experimental/scientific code to the active Git branch;
- independently reinterpret scientific results.

If a compact Git receipt needs publication, Worker T leaves it under the bulk receipt root for Worker G to import/commit, or uses a separately coordinated read-only handoff path. Avoid concurrent writes to the same Git worktree/index.

## Local-only work may overlap GPU work

The following Worker-T activities are safe to run while Worker G is measuring, provided they do not materially load the GPU host:

```text
local upstream download
local model hashing
local archive/package preparation
local parser/receipt generation
local metadata search
local `/root/share` organization
```

These should run continuously where useful.

## Remote heavy I/O must not overlap formal measurement

Heavy operations involving the GPU host can perturb timings/census/capture through CPU, page cache, filesystem, network and process scheduling even when GPU utilization itself looks unchanged.

Therefore do **not** overlap with formal unprofiled baseline, duration-bearing nsys census, or formal NVBit capture:

```text
rsync/scp/sftp upload to GPU host
rsync/scp/sftp large copyback from GPU host
large remote SHA scans
large remote archive/compression
large remote filesystem cleanup
```

Worker G has priority whenever `GPU_READY_QUEUE_COUNT > 0`.

## Coordination lock

Use one remote lock path, creating its parent once:

```text
/root/autodl-tmp/c16_retry570/control/GPU_IO_EXCLUSION.lock
```

### Worker G

Wrap every formal GPU measurement/capture command in an exclusive remote `flock` covering preflight through cleanup. Before starting, assert no active transfer worker process is writing large data.

### Worker T

For remote rsync use the same lock on the remote rsync endpoint where practical, for example through an existing equivalent of:

```text
--rsync-path="flock -x /root/autodl-tmp/c16_retry570/control/GPU_IO_EXCLUSION.lock rsync"
```

If the current SSH/rsync wrapper cannot support that exact spelling, implement an equivalent remote exclusive-lock protocol and prove it with a tiny transfer test.

Do not invent a parallel uncoordinated transfer route.

## GPU-priority scheduling

Worker T must not start a new large remote transfer if Worker G reports a ready GPU row.

Worker G should publish/update a lightweight coordination state under the local bulk root, e.g.:

```text
/root/share/c16_recovery_v3/receipts/GPU_PIPELINE_STATE.json
```

with at least:

```text
GPU_READY_QUEUE_COUNT
GPU_ACTIVE_JOB
NEXT_GPU_JOB
MEASUREMENT_ACTIVE
REMOTE_IO_ALLOWED
updated_at
```

Worker T reads this before starting each remote-I/O batch.

If a resumable transfer is already active when a GPU job becomes ready:

1. preserve transfer progress;
2. stop/pause at the earliest safe resumable boundary;
3. release the remote I/O lock;
4. Worker G runs the GPU job;
5. after GPU cleanup, resume transfer.

Never restart a multi-GiB transfer from zero if resumable state exists.

## Copyback cadence

Worker G writes each completed run to the remote retained raw tree and closes the measurement window.

After cleanup, Worker T may immediately acquire the remote I/O lock and copy it back. Worker G need not wait for that copyback before performing CPU-side analysis, but it must not delete the remote sole copy.

Before a later formal window whose remote-disk safety depends on reclaiming space, require the prior copyback SHA closure.

## Git ownership

To avoid worktree/index races:

```text
ACTIVE GIT WORKTREE OWNER = Worker G
BULK FILESYSTEM WORKER    = Worker T
```

Worker T does not run `git reset`, `git checkout`, `git merge`, `git add`, or `git commit` in Worker G's active worktree.

If Worker T needs source inspection, use read-only `git show`, a separate worktree, or the current checked-out files without mutation.

## Status cadence

Worker G reports:

```text
GPU_READY_QUEUE_COUNT=
GPU_ACTIVE_JOB=
NEXT_GPU_JOB=
WHY_GPU_IDLE=
```

Worker T reports:

```text
LOCAL_PREP_JOB=
REMOTE_TRANSFER_JOB=
REMOTE_TRANSFER_STATE=
COPYBACK_JOB=
REMOTE_IO_LOCK_STATE=
```

`WHY_GPU_IDLE` is acceptable only when no executable GPU row exists or at a short preflight/cleanup boundary. A model being transferred is not, by itself, a valid reason to idle the GPU when another row is ready.

## Final invariants

Both workers must converge on:

```text
ALL_REQUIRED_RAW_UNDER_LOCAL_BULK_ROOT=true
ROOT_FS_LARGE_PAYLOAD_LEAK_COUNT=0
REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0
ACTIVE_GPU_PROCESS_COUNT=0
ACTIVE_DIAGNOSTIC_PROCESS_COUNT=0
MEASUREMENT_ACTIVE_AFTER_CAMPAIGN=false
```
