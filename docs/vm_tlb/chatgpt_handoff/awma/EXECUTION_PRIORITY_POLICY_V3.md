# AWMA Execution Priority Policy V3

Date: 2026-09-22
Ownership: ChatGPT
Status: ACTIVE POLICY

## 1. Core rule

AWMA mainline has absolute priority over candidate side lanes on both 174-new and node109.

Current mainline:

`AWMA_CROSS_TARGET_HITPATH_VALIDITY_AND_NATIVE_CROSSVIEW_V1`

Current scientific question:

> Is the large repaired translation hit-path sensitivity robust across representative AI kernel families, or specific to Q05 / current simulator timing semantics?

## 2. Mainline ordering

```text
P0:
  109 pause active MoE causal-closure at safe checkpoint
  174 finish V4 remote publication

P1:
  174 Prefill GEMM repaired hit-path screen
  109 exact-target native evidence closure

P2:
  174 Decode GEMV repaired hit-path screen

P3:
  Cross-view synthesis and scientific review

STOP before architecture mechanism
```

No side-lane experiment may delay these steps.

## 3. 109 / RTX4080 priority

The GPU is a mainline resource first.

If a side-lane campaign is running when mainline becomes READY:

1. do not kill an in-flight CUDA call mid-operation;
2. stop at the smallest safe checkpoint supported by the campaign;
3. persist already-completed evidence and scheduler state;
4. mark unfinished work `PAUSED_FOR_AWMA_MAINLINE`;
5. publish the paused state remotely;
6. release `/data/c16/locks/c16_gpu_campaign.lock`;
7. switch to mainline.

A side lane must not insist on using its originally allocated 20h window.

## 4. 174-new priority

174 is Simulation-plane mainline owner.

Before a new scientific stage starts:

- prior accepted report/review pack must be remotely published;
- execution branch remote HEAD must equal local accepted HEAD;
- required scientific files must be visible in the remote tree.

A local-only or node164-only result is:

`PROVENANCE_CLOSEOUT_REQUIRED`

and blocks the next 174 science stage.

Publication failure never authorizes science rerun.

## 5. Candidate side lanes

Candidate side lanes are preserved research assets, not abandoned work.

They may resume only when:

- no mainline task is READY on that node;
- ChatGPT explicitly reactivates the candidate;
- continuation answers a predeclared research question;
- it does not mutate mainline runtime/model/input authority.

## 6. Selection discipline

New mainline experiments are selected by scientific question, not asset availability.

Do not run a model, scenario, operator, or mechanism merely because:

- the model is already downloaded;
- an input pool exists;
- a profiler script already works;
- GPU/CPU time is otherwise idle.

## 7. Mechanism gate

No TLB/PTW/cache/MoE scheduling/AWQ optimization mechanism is authorized until the current mainline Cross-view stage is reviewed.

## 8. Solve-and-continue

Routine engineering issues:

- build;
- paths;
- parser;
- selector;
- receipt;
- transfer;
- Git publication;
- exact-target adapter;

are solve-and-continue.

Stop for scientific review only when continuation changes:

- workload/target identity;
- model revision;
- simulation functional/timing semantics beyond the declared diagnostic;
- evidence classification;
- claim boundary.


## 9. Default dependency-first parallel execution

For every stage containing multiple runs, targets, configurations, captures,
analysis jobs, transfers, or publication tasks, Codex MUST perform a
dependency/resource audit before defaulting to serial execution.

### 9.1 Classify dependency, not just ordering

Each pending task must be classified as one of:

- `INDEPENDENT`: no result from another task is needed to execute it;
- `SPECULATIVE_DEPENDENT`: execution can proceed now, but scientific admission
  depends on an upstream gate;
- `STRICT_DEPENDENT`: execution inputs or semantics cannot be known until an
  upstream result is available;
- `SERIALIZED_MUTABLE_RESOURCE`: tasks would write the same mutable state,
  reuse a non-concurrent-safe lock/device, or otherwise cannot safely overlap.

Only `STRICT_DEPENDENT` and `SERIALIZED_MUTABLE_RESOURCE` tasks should be
forced to wait.

A scientific gate is NOT automatically an execution dependency.  If a
downstream run can be executed safely with already-frozen inputs, it may run
speculatively and remain quarantined until its upstream gate passes.

### 9.2 Mandatory resource audit

Before launching a parallel batch, inspect the resources that can actually
limit the stage.

For CPU simulation / analysis:

- logical and physical core topology;
- current load and per-process CPU utilization;
- available memory and swap pressure;
- measured RSS of an existing representative process when available;
- storage free space;
- I/O wait / shared trace-read pressure;
- existing simulator/process count.

For GPU work:

- GPU lock ownership;
- free VRAM and baseline VRAM;
- active GPU processes;
- whether the tool/runtime safely supports concurrent GPU jobs;
- host memory / CPU / storage bandwidth needed by those jobs.

For storage/network work:

- node164 mount health;
- free space;
- whether multiple writers target the same directory/file;
- network or SSH bottlenecks when relevant.

### 9.3 Maximize safe concurrency

After the audit, choose the highest safe concurrency supported by:

1. the dependency graph;
2. immutable/read-only sharing rules;
3. observed resource footprint;
4. host headroom;
5. tool/runtime concurrency constraints.

Do not artificially cap concurrency at 1 or 2 merely because runs were listed
in sequence in the Goal.

If N independent/speculative tasks are ready and resources safely support N,
launch all N.

If resources support fewer than N, launch the largest safe subset and refill a
slot immediately when one finishes.

### 9.4 Isolation contract

Concurrent runs must have distinct:

- run/output directories;
- effective-config copies;
- stdout/stderr logs;
- receipt files;
- temporary files;
- mutable checkpoint/state files.

Immutable traces, model assets, compatibility maps, source trees, and accepted
read-only authorities may be shared.

Do not allow concurrent jobs to modify a shared config/map/manifest in place.

When useful, pin CPU-bound simulator processes to disjoint physical cores or
CPU sets.  Host wall time, CPU affinity, and scheduling policy are engineering
controls and are not scientific metrics.

### 9.5 Speculative-result quarantine

A task executed before its upstream scientific gate closes must be labelled:

`SPECULATIVE_PRE_GATE`

Its raw result may be preserved, but it enters the accepted scientific matrix
only after:

- all upstream gates pass; and
- its own terminal/coverage/identity/invariant gates pass.

If an upstream gate fails, already-computed speculative results are
quarantined rather than silently admitted or automatically deleted.

### 9.6 Continuous refill

Codex should not leave resources idle while executable mainline work remains.

After any job finishes:

1. evaluate its hard gates;
2. checkpoint/hash the completed evidence;
3. immediately launch the next ready independent/speculative task if resources
   remain available;
4. perform report generation, hashing, copying, or analysis concurrently with
   remaining long-running simulations whenever they use independent resources.

### 9.7 Scientific boundaries remain unchanged

Parallel execution must never relax:

- exact target/workload identity;
- frozen model/config semantics;
- terminal/coverage requirements;
- fail-closed admission;
- claim boundaries;
- mandatory remote publication.

Parallelism changes wall-clock scheduling only, not scientific acceptance.
