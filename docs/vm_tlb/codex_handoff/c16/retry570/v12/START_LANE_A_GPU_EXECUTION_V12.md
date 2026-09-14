# START — Lane A GPU execution V12

Use Goal mode.

Read first, without checking out the handoff branch:

```bash
git fetch origin hrl/vm-c16-g-retry570-v0 \
  hrl/vm-c16-g-retry570-chatgpt-handoff-v12 \
  hrl/vm-c16-h-memory-fingerprint-v0

git show origin/hrl/vm-c16-g-retry570-chatgpt-handoff-v12:docs/vm_tlb/codex_handoff/c16/retry570/v12/C16_GPU_FIRST_MULTI_WINDOW_HANDOFF_V12.md
```

Active scientific branch remains `hrl/vm-c16-g-retry570-v0`. Fast-forward the AutoDL runtime worktree to the latest remote commit on that branch before new execution. Do not checkout/reset/merge the V12 handoff branch or H methodology branch into the active worktree.

## Goal

Keep the rented RTX3090 producing GPU-dependent evidence. Do not spend long intervals on work that can be done later on the local/control server.

At startup publish:

```text
ACTIVE_GIT_HEAD=
GPU_ACTIVE_JOB=
GPU_READY_QUEUE_COUNT=
NEXT_GPU_JOB=
GPU_IDLE_SECONDS=
REMOTE_DATA_FREE_BYTES=
MEASUREMENT_ACTIVE=
ACTIVE_GPU_PROCESS_COUNT=
```

## Immediate scheduling rule

### P0 — execute any ready Llama Route-B map/inventory request

If Lane C has already published a frozen Route-B candidate/map request derived from the exact Llama S0 G1 catalog, execute that map/inventory batch first.

Only map/inventory exact functions named in the frozen request. Do not select kernels from NVBit outcomes.

For each exact function retain:

```text
exact full/mangled identity
phase
grid/block
launch count from G1 authority
static instruction count
GLOBAL+MREF static indices
GLOBAL+MREF count
LDG/STG/ATOM composition
code-object SHA
static-map SHA
remote manifest/SHA
```

Publish a compact checkpoint immediately so Lane C can finalize the memory-opportunity proxy and selected-kernel manifest.

### P1 — while Route-B requests/code are not ready, consume existing GPU backlog

Do not wait for Lane C.

Default fallback order:

1. Qwen0 S1/CODE campaign-scoped G1, but first prove retained native baseline identity equals the frozen current binding. Reuse the valid baseline; do not rerun it unnecessarily.
2. Qwen7 raw S2/TEXT campaign-scoped G1 after identity equality.
3. Qwen7 raw S2/CODE campaign-scoped G1 after identity equality.
4. Qwen7 raw S2/STRUCTURED campaign-scoped G1 after identity equality.
5. Any R4/R5/R6 work lawfully unlocked by those new catalogs.
6. Llama S1-S4 Recovery-V3 GPU work when exact bindings/scopes are ready.

Do not rerun Qwen0 S3 Prefill R6; it is already complete. Do not widen/rescan Qwen0 S3 Decode V1.

### P0 when producer becomes ready

Lane C will report a tested producer commit from its separate branch. Integrate only between measurement windows, after focused review/tests, and only Lane A may mutate the active GPU worktree.

Then execute:

1. Route-B Q1 tiny CUDA fixture;
2. Route-B Q2 Llama bridge comparison;
3. one bounded Route-B canary;
4. formal Route-B partitions if canary PASS;
5. Route-C GPU-dependent reference if rental time remains.

Do not wait for local copyback between these stages.

## GPU idle hard rule

If `GPU_READY_QUEUE_COUNT > 0` and `GPU_ACTIVE_JOB=none` for >120 seconds, immediately start the next ready GPU job unless a documented hard gate from the V12 handoff applies.

CPU-only work must run in parallel or later.

## Artifact closeout

For every GPU job:

```text
finish measurement
-> MEASUREMENT_ACTIVE absent
-> GPU process cleanup
-> remote bytes/SHA/manifest
-> COPYBACK_READY
-> checkpoint commit/push
-> next GPU job
```

Do not wait for Lane B local SHA closure unless remote storage has crossed the safety threshold.

## Shared state

Atomically update:

`/root/autodl-tmp/c16_retry570/control/GPU_PIPELINE_STATE.json`

After every job and before starting another.

Required fields:

```text
git_head
timestamp
gpu_active_job
gpu_ready_queue_count
next_gpu_job
measurement_active
active_gpu_process_count
gpu_idle_seconds
remote_data_free_bytes
transfer_slot_granted
```

Use `/root/autodl-tmp/c16_retry570/control/GPU_IO_EXCLUSION.lock` for formal GPU windows.

## Checkpoint report

After each independently reviewable stage report only:

```text
CHECKPOINT_COMMIT=
MODEL=
SCENARIO=
PHASE=
STAGE=
STATUS=
KEY_RESULT=
REMOTE_SHA_CLOSED=
COPYBACK_STATE=
GPU_READY_QUEUE_COUNT=
NEXT_GPU_JOB=
GPU_IDLE_SECONDS=
REMOTE_DATA_FREE_BYTES=
```

Do not stop Goal for ordinary engineering failures. Fix boundedly and continue.