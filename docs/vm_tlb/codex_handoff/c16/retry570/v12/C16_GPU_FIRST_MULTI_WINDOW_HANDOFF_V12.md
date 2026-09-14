# C16 Recovery-V3 GPU-first multi-window handoff V12

Status: `READY_FOR_EXECUTION`.

Base active-G checkpoint at handoff creation:

`b1a036162ca379386f93c4fe18c3133b2477338b`

Active scientific branch remains:

`hrl/vm-c16-g-retry570-v0`

Route-B methodology authority remains read-only on:

`hrl/vm-c16-h-memory-fingerprint-v0@9f11256cacdbfb03f367969b23fb7da2dbd13db4`

This V12 branch is a handoff branch only. No worker may replace the active scientific branch with this branch.

## Objective

The rented RTX3090 is the scarce resource. Until the rental campaign stops, optimize for **GPU-dependent evidence production**. CPU-only analysis, publication, copyback, local hashing, asset bookkeeping, and long documentation work must run in parallel or be deferred.

Current key facts at the base checkpoint:

- Qwen0 S3 Prefill V2 R5 has valid address-bearing evidence and an independent reproduction.
- Qwen0 S3 Prefill R6 formal capture is complete; do not rerun it.
- Qwen0 S3 Decode V1 is closed `PREDICATED_OFF_TARGET`; do not widen or blind-scan it.
- Exact Llama-3.2-1B S0/B1/T128/Decode4 campaign G1 census is complete and is now the Route-B selection authority.
- Llama Route-B **formal all-GLOBAL-MREF capture has not started**.
- Qwen0 S1/CODE and Qwen7 raw S2/{TEXT,CODE,STRUCTURED} historical G1 claims were superseded; retained native baselines may be reused only after frozen-identity equality, then campaign-scoped G1 must be regenerated.

## Worker ownership

### Lane A — GPU execution owner

Only Lane A may:

- mutate/deploy the active GPU runtime worktree;
- run model workloads, nsys, NVBit, NCU, Route-B Q1/Q2/canary/formal capture;
- create/clear `MEASUREMENT_ACTIVE`;
- own the scientific execution checkpoint on `hrl/vm-c16-g-retry570-v0`.

Lane A must keep GPU work flowing. If one Route-B software prerequisite is not ready, run another already-authorized GPU job instead of waiting.

### Lane B — transfer/storage owner

Lane B owns copyback, local SHA closure, safe remote cleanup, and storage-watermark monitoring. It must not run scientific GPU workloads or mutate the active Git worktree.

### Lane C — Route-B selection/producer developer

Lane C is CPU/code-only. It owns deterministic Llama Route-B candidate selection, producer development, parser/tests, and Q0 qualification in a **separate worktree/branch**. It must not run GPU workloads and must not mutate Lane A's active worktree.

### Lane D — next-model readiness owner

Lane D is CPU/local-prep only. It closes model/input/binding authority and prepares the next GPU-ready rows. It must not run model workloads and must not perform heavy remote transfer while Lane A has GPU-ready work.

## Hard GPU-first scheduler

If `GPU_READY_QUEUE_COUNT > 0` and `GPU_ACTIVE_JOB=none` for more than 120 seconds, treat it as a scheduling failure unless one of these is true:

1. stale GPU process or `MEASUREMENT_ACTIVE` cleanup is unresolved;
2. exact scientific identity for that GPU job is not frozen;
3. `GPU_IO_EXCLUSION.lock` has a real conflicting owner;
4. remote data free space is below the safety threshold;
5. the next job requires a code artifact that does not yet exist, **and no other GPU-ready job exists**.

Commit/push, Markdown, publication, CPU tests, copyback, local SHA, and AWQ package SHA are not valid reasons to idle a ready GPU.

## Immediate GPU fallback queue

The queue is dynamic, but at V12 creation these are the default fallback classes whenever Route-B map/Q1/Q2 work is not ready:

1. Regenerate campaign-scoped G1 for Qwen0 S1/CODE after frozen-identity equality against its retained valid native baseline.
2. Regenerate campaign-scoped G1 for Qwen7 raw S2/TEXT, S2/CODE, S2/STRUCTURED after frozen-identity equality against retained valid native baselines.
3. Consume newly valid R4/R5/R6 work created by those G1 catalogs.
4. Llama S1-S4 Recovery-V3 GPU work when exact bindings/scopes are ready.
5. Other exact-identity rows only when their R1/R2 authority is closed.

Never rerun Qwen0 S3 Prefill R6 just to keep the GPU busy.

## Route-B pipeline

Route B means representative-kernel capture of **all direct explicit `GLOBAL && has_mref` static instructions**, not one selected PC.

The required sequence is:

1. Exact Llama S0 campaign G1 census — already complete.
2. CPU duration-mass candidate ranking.
3. GPU map-only discovery for candidate exact functions.
4. CPU memory-opportunity proxy and final selection freeze.
5. Route-B append-only producer implementation and Q0 CPU qualification.
6. GPU Q1 tiny fixture.
7. GPU Q2 Llama bridge comparison.
8. GPU bounded canary.
9. GPU formal partitions under `<=4GiB` and `<=20min` per window.
10. Route-C phase coverage validation if rental time remains.

Candidate selection must be frozen before Route-B address outcomes are observed. Per phase, final selected functions are the union of:

- minimum deterministic prefix covering >=70% native duration mass;
- minimum deterministic prefix covering >=80% pre-outcome memory-opportunity proxy, where proxy is `launch_count * CTA_count * warps_per_CTA * static_GLOBAL_MREF_count`;
- actually observed semantic-class anchors from the census, never invented.

## Route-B event schema minimum

Every address-bearing event must retain enough structure for later TLB/cache experiments:

- run/deployment/scenario/phase/decode-step;
- exact function and kernel launch id;
- CTA x/y/z and warp id;
- static index, instruction offset/PC, opcode, MREF ordinal;
- GLOBAL memory space and READ/WRITE/ATOMIC kind;
- width;
- active mask and predicate mask when reliably available;
- active-lane IDs and per-active-lane observed GPU VA;
- append-only observed callback sequence;
- terminal linkage, drop count, overflow count.

The sequence must be labeled `OBSERVED_CALLBACK_ORDER`; it is not hardware-global time order.

## Artifact policy

After each GPU job, Lane A must at minimum close:

- remote bytes;
- remote SHA256;
- compact manifest/receipt;
- retained remote source.

That is sufficient to continue to the next GPU job. Local copyback is asynchronous and may be deferred.

Storage thresholds under `/root/autodl-tmp`:

- free >= 80 GiB: continue GPU; ordinary copyback may wait;
- 50 GiB <= free < 80 GiB: Lane B batch-copies in safe gaps, GPU-ready work still wins;
- free < 50 GiB: pause new large raw capture until enough already-local-closed remote data is safely cleaned.

Never delete the only remote copy before local bytes/SHA equality exists.

## Shared coordination

Remote control root:

`/root/autodl-tmp/c16_retry570/control/`

Required shared files:

- `GPU_PIPELINE_STATE.json`
- `COPYBACK_QUEUE.json`
- `ROUTE_B_MAP_REQUESTS.json` or equivalent compact request artifact
- `GPU_IO_EXCLUSION.lock`

Lane A publishes actual GPU state. Lane B and Lane D read it before remote I/O. Lane C publishes map requests through Git and/or the compact coordination artifact, but never edits Lane A's worktree directly.

## Checkpoint rule

Commit and push every independently reviewable milestone, but never wait for ChatGPT approval between authorized GPU stages.

Examples:

- campaign G1 complete;
- Route-B candidate batch frozen;
- each map batch complete;
- final Route-B selected-kernel manifest;
- producer Q0/Q1/Q2;
- canary;
- each formal partition;
- Route-C closeout.

Raw payloads remain outside Git.

## Problem-solving rule

Ordinary engineering failures are not user blockers. Use:

`observe -> narrow cause -> bounded evidence-preserving fix -> focused validation -> rerun smallest affected gate -> continue`

Only stop for true external authority/resource failures. Independent GPU-ready rows must continue whenever possible.
