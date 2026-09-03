# M5 Parallel Batch Execution Policy

Status: **ACTIVE — REQUIRED FOR LONG INDEPENDENT SIMULATION WAVES**

Purpose: minimize wall-clock time without changing simulator semantics or compromising reproducibility. This policy applies to Extended-20 and may also be reused for Paper-10 sweeps when experiments are independent.

## 1. Default policy: worker pool, not serial execution

Do not execute long independent workloads one-by-one by default.

Materialize every experiment as a job in a resumable registry and keep a dynamic worker pool filled up to the current safe host-concurrency limit.

A job identity must include at least:

`experiment_id | workload | mode | Core_SHA | Framework_SHA | config_hash | source_hash | PTX_hash | input_hash | parser_schema`

Job states:

- `PENDING`
- `RUNNING`
- `PASS`
- `RESOLVING_ISSUE`
- `RETRY_READY`
- `FAILED_HARD`
- `OBSOLETE`
- `SKIPPED_IDENTITY_MATCH`

Never rerun a completed result whose full identity tuple already matches unless an explicit reproducibility repeat is required.

## 2. Determine safe concurrency from measurements

Reuse the M5.0A host calibration when still representative. Recalibrate if Core memory usage, workload mix, machine load, or graphics work materially changes.

Let `N_safe` be derived from measured:

- available logical CPU capacity;
- per-process CPU behavior;
- per-process RSS distribution, especially p90/p95;
- host free memory and swap policy;
- I/O pressure;
- currently running non-M5 jobs.

Use conservative headroom rather than saturating RAM. The runner must record the chosen `N_safe`, measurement time, host CPU count, free RAM, and assumptions.

Do not hard-code a universal parallelism number into the scientific result.

## 3. Heavy-job admission control

Use historical wall time, trace/input size, or early runtime samples to label jobs approximately `LIGHT`, `MEDIUM`, or `HEAVY` for scheduling only.

Rules:

- keep the total active jobs <= `N_safe`;
- do not fill all slots with historical Q4/HEAVY jobs unless measurements prove memory headroom;
- initial heavy-slot budget should be conservative (for example about one third of active slots) and may be adjusted from measured RSS/CPU behavior;
- a heavy job finishing should immediately release a slot to the pending queue;
- scheduling class affects wall-clock orchestration only, never simulator configuration.

## 4. Queue strategy

For the 60-run Extended-20 wave, enqueue all Base/IO/OO jobs after identity validation.

Recommended scheduler:

1. maintain at least one job from different workloads/modes when possible;
2. mix light/medium/heavy jobs to avoid a long heavy tail;
3. when any job exits, validate its result and immediately dispatch the next eligible job;
4. do not wait for all three modes of one workload before starting other workloads;
5. triplet interpretation waits for all three FORMAL members, but execution order does not.

Base/IO/OO processes may run concurrently because host scheduling does not alter simulated cycle semantics. Wall-clock duration is diagnostic only and never compared as DTC performance.

## 5. Progress and timeout handling

A wall-clock timeout is not automatically a simulator deadlock.

For each workload derive a bounded allowance from historical cost and observed progress. During long runs record low-cost progress evidence such as:

- process CPU time advancing;
- output/perf-counter/log file growth;
- periodic simulator cycles/instructions when available;
- last committed/progress state where source supports it.

Classify:

- progress continues -> `SLOW_BUT_PROGRESSING`, extend within a documented bound;
- simulator deadlock detector/assertion fires -> source-level issue lifecycle;
- no host/simulator progress beyond the documented watch window -> investigate before retry.

Do not weaken simulator deadlock/assertion logic merely to keep the queue moving.

## 6. Failure isolation and queue continuity

One failed job does not stop unrelated independent jobs.

When a job finds an ordinary resolvable issue:

1. mark the affected identity `RESOLVING_ISSUE`;
2. continue unrelated queued jobs whose correctness/fidelity cannot be affected by the suspected bug;
3. diagnose/repair under `M5_PROBLEM_RESOLUTION_POLICY.md`;
4. identify the exact invalidation scope;
5. mark stale results `OBSOLETE` rather than deleting them;
6. rerun only affected identities;
7. refill the worker pool.

If the issue may affect all modes/workloads, stop launching new FORMAL jobs until the invalidation scope is known, but preserve already-running processes unless continuing them risks misleading state or corrupted evidence.

## 7. Resource coordination across Codex windows

Compute and graphics-research windows share the same physical host unless explicitly placed elsewhere.

The graphics M5.7/M5.8 research window should be mostly source/artifact work and must not consume simulation slots reserved for active compute waves.

If graphics research starts expensive compilation/capture work, it must inspect current host load first and remain within the shared concurrency budget.

M5.9+ graphics simulation/integration begins only after compute freeze, so it does not contend with the primary compute FORMAL campaign by design.

## 8. Required batch artifacts

Before a major wave:

- `JOB_MANIFEST.tsv`
- `BATCH_POLICY.md` or run metadata with `N_safe` and heavy-slot cap

During/after:

- resumable registry with state transitions;
- `RAW_LOG_INDEX.tsv`;
- result identity hashes;
- retry/obsolete reasons;
- start/end/wall-time values for operational planning only.

Do not commit raw logs, binaries, traces, build trees, or large datasets.

## 9. Acceptance

A batch wave is orchestration-clean only if:

- independent jobs were dispatched up to measured safe parallelism rather than unnecessarily serialized;
- no result depends on host wall-clock timing;
- every PASS result has a complete identity tuple;
- failures/retries/obsolete results are preserved and classified;
- no data race/shared-output-path collision exists among concurrent jobs;
- each job uses an isolated output directory;
- final parser/counter sanity passes.
