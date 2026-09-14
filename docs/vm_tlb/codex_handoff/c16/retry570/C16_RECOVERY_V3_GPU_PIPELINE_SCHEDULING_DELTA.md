# C16 Recovery V3 — GPU Pipeline Scheduling Delta

This delta supersedes any interpretation of the v9 Goal that serializes **all** asset preparation before GPU execution.

## Why this delta exists

The current campaign has already proven that the GPU runtime is usable, and several deployment/scenario rows are ready or nearly ready while unrelated asset transfers continue. Leaving the rented RTX3090 idle for long rsync/hash/download phases is unnecessarily expensive.

The campaign must therefore operate as a pipeline with independent queues:

```text
LOCAL_PREP_QUEUE      metadata, exact-revision recovery, downloads, hashing, receipts
REMOTE_TRANSFER_QUEUE model/package rsync to GPU host
GPU_READY_QUEUE       rows whose R2/runtime/input/resource gate is satisfied
COPYBACK_QUEUE        completed raw/profiler data -> /root/share + SHA closure
PUBLICATION_QUEUE     compact Git receipts/manifests/tests
```

A queue must not block unrelated queues.

## Non-negotiable scheduler invariant

```text
IF GPU_READY_QUEUE != empty
AND no timing-sensitive GPU window is active
THEN do not wait for unrelated model transfer/download/metadata work to finish.
```

Start the highest-priority ready GPU row instead.

Asset preparation for other models continues in parallel on the local/control host.

## Remote transfer vs scientific measurement

Large rsync/scp writes to the **same GPU host** may perturb host CPU/disk/I/O and must not overlap timing-sensitive scientific windows.

Therefore:

1. remote transfer workers may run while the GPU is idle or during non-measurement preparation;
2. before an unprofiled baseline, nsys census used for duration, NVBit canary/repro, or formal capture, pause the remote transfer worker cleanly;
3. confirm no active write-heavy rsync/scp/sftp process on the GPU host;
4. run the GPU window;
5. after cleanup and evidence closure, resume the transfer worker from its partial state.

Do **not** restart a multi-GiB transfer from byte zero merely to pause it. Use resumable rsync/partial semantics or an equivalent retained partial.

Local-host downloads/hashing under `/root/share` may continue while the GPU runs, because they do not touch the GPU host.

## Current checkpoint facts to schedule around

Active branch checkpoint at delta creation:

```text
bc4abe769eb548140fd97ce95ff0e6ebe7323331
```

Evidence already published on the active branch:

### Qwen2.5-0.5B

- exact asset and all frozen scenario bindings are already hash-closed;
- R2 preflight passed;
- S0 native baseline + G1 lightweight census completed;
- R4 S0 plan frozen;
- its historical six-window R5 control ledger is exhausted by retained diagnostics.

**Scheduling consequence:** do not leave the GPU idle because S0 R5 is temporarily budget-limited. Immediately run independent ready work: Qwen0 S1/S2/S3/S4 R3 native baseline+census, then R4 plans, while budget-scope repair proceeds independently.

### Qwen2.5-7B raw

- exact model is dual-endpoint SHA-closed;
- all non-S0 scenario bindings are materialized/closed;
- S1/CODE runtime preflight passed;
- S1 native/G1 work has executed;
- S1 Prefill has already consumed bounded direct-memory diagnostic work and closed two exact launched GLOBAL MREF targets with zero address records.

**Scheduling consequence:** that Prefill target-path limitation does not stall the model. Continue independent GPU work: Decode-side target qualification and/or next ready scenarios (S2 first, then S3/S4 as admitted).

### Qwen2.5-7B AWQ

- local exact model/input package exists under `/root/share`;
- remote model transfer was still in progress at the latest live observation.

**Scheduling consequence:** AWQ transfer is a background dependency, not a reason to idle the GPU. Pause it during ready GPU measurement windows, resume afterward.

### Qwen3-8B

- exact-revision local bulk asset is already hash-closed;
- runtime input/resource-admission remains to be closed.

**Scheduling consequence:** complete its CPU-only binding/admission prep in parallel with other GPU runs, then enqueue it immediately.

### DeepSeek-V2-Lite

- current active commit registers a closed non-destructive local asset copy;
- runtime-input/resource closure may still be pending.

**Scheduling consequence:** finish only the missing compact/input/runtime gate in parallel; enqueue once R2-ready.

### Llama

- accepted S0 checkpoint remains inherited;
- S1-S4 remain in authoritative scope.

**Scheduling consequence:** prepare any missing S1-S4 bindings CPU-side in parallel and enqueue ready rows; do not wait for AWQ/Qwen3 transfers.

### Qwen3-30B-A3B

```text
EXCLUDED_BY_USER_CURRENT_CAMPAIGN
```

Never schedule it in this Goal.

## GPU priority queue

Use this priority unless a row is not actually R2-ready:

```text
P0  Qwen2.5-7B raw: already-live S1 follow-up / Decode qualification / next R3 scenario
P0  Qwen2.5-0.5B: S1 -> S2 -> S3 -> S4 native baseline+census
P1  Llama: S1 -> S2 -> S3 -> S4 native baseline+census and authorized target work
P1  Qwen2.5-7B raw: S2 -> S3 -> S4
P2  Qwen2.5-7B AWQ as soon as remote hash closure passes
P2  Qwen3-8B as soon as R2 passes
P2  DeepSeek-V2-Lite as soon as R2 passes
P3  GLM only after exact identity closes
```

Within a deployment, favor **R3 native/census coverage first** because it creates useful scientific progress and future target plans even if a particular NVBit target path is capability-limited.

## Fresh budget namespaces for new scientific rows

Historical diagnostic/control ledgers are immutable evidence, but they must not permanently prohibit newly authorized Recovery-V3 model/scenario work.

Do not reset, delete, edit, or reclassify old ledger rows.

For every new Recovery-V3 deployment/scenario that needs R5/R6, create a fresh campaign-scoped ledger namespace, for example:

```text
campaign_id = c16_full_authority_recovery_v3
budget_scope = <deployment>/<scenario>/<phase-target-class>
```

The new scope must preserve all global capture bounds:

```text
one GPU capture process at a time
<= 4 GiB per window
<= 20 min per window
raw outside Git
rolling copyback required
```

A consumed legacy diagnostic ledger may be cited as history, but not used as a terminal blocker for a newly authorized scenario/target class.

For an already published capability-limited exact target (for example Qwen7 raw S1 Prefill direct-memory V1/V2), do not blindly retry the same target just because a new scope exists. Move to a scientifically justified independent phase/target/scenario.

## Utilization discipline

While a rented GPU instance is active, every scheduler cycle must report:

```text
GPU_READY_QUEUE_COUNT=
GPU_ACTIVE_JOB=
REMOTE_TRANSFER_JOB=
LOCAL_PREP_JOBS=
NEXT_GPU_JOB=
WHY_GPU_IDLE=
```

`WHY_GPU_IDLE` is valid only when the GPU-ready queue is empty or when a short mandatory cleanup/preflight boundary is in progress.

Waiting for an unrelated model's transfer/hash/download is not a valid idle reason if another row is ready.

## Acceptance

This scheduling delta is satisfied when:

- ready GPU rows are executed without waiting for unrelated asset completion;
- remote transfers are paused during timing-sensitive measurement and resumed afterward;
- local downloads/hash/prep proceed concurrently with GPU execution;
- historical ledgers remain unchanged;
- new authorized R5/R6 work uses fresh campaign/scenario budget scopes;
- no Qwen3-30B-A3B work is scheduled;
- all completed large payloads still obey rolling `/root/share` copyback and SHA closure.
