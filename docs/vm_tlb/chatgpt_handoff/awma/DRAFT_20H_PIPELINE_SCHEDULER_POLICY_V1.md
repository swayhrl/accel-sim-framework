# DRAFT — AWMA 20h Pipeline Scheduler Policy V1

Date: 2026-09-19

Status: `PRE_REPAIR_DRAFT_NOT_EXECUTABLE`

This policy defines how the post-repair unattended campaign uses solve-and-continue Goal mode
without turning idle resources into unbounded experimental scope.

## 1. Scheduler objective

Maximize useful scientific progress during a bounded 20-hour unattended window while preserving:

- scientific identity;
- accepted-source semantics;
- claim boundaries;
- GPU ownership;
- node164 provenance;
- finalization time.

The scheduler optimizes for completed, interpretable experiment units, not device utilization.

## 2. Queue classes

### MANDATORY

Tasks required by the final scientific contract.

They have first claim on node resources.

### CONDITIONAL

Tasks with pre-frozen entry gates. They execute only if the gates pass.

### OPPORTUNISTIC

High-value independent work that may consume remaining budget after mandatory work is closed or
while another resource is naturally idle.

### DEFERRED

Tasks explicitly excluded from this unattended campaign.

No task may promote itself from DEFERRED to another class.

## 3. Resource model

### GPU109

Exclusive resource.

Before GPU work:

1. inspect `nvidia-smi`;
2. verify expected RTX4080 identity / UUID;
3. inspect the campaign lock;
4. acquire `/data/c16/locks/c16_gpu_campaign.lock` normally;
5. never kill / bypass a legitimate owner.

Only one GPU task may be RUNNING.

### CPU174

May run one simulator-heavy experiment and lightweight analysis only if doing so does not
invalidate runtime isolation or exhaust local storage.

Large outputs go directly to node164 authority.

### STORE164

Accepted destinations are immutable.

Use unique run IDs and `.partial` transfer paths.
Never have two writers target the same accepted path.

## 4. Task states

Each task uses:

`BLOCKED`
`READY`
`RUNNING`
`TRANSFER`
`ANALYZE`
`ACCEPTED`
`PARTIAL`
`FAILED_ENGINEERING`
`STOP_SCIENTIFIC`
`SKIPPED_BUDGET`
`SKIPPED_GATE`

A task can advance only through documented gates.

`PARTIAL` never satisfies a complete-evidence dependency unless the downstream contract
explicitly accepts partial evidence.

## 5. Solve-and-continue handling

### Engineering fault

Examples:

- build failure caused by path/config;
- profiler timeout;
- stale local cache;
- parser bug;
- interrupted rsync;
- derived metadata regeneration.

Action:

1. diagnose;
2. perform bounded safe repair;
3. record repair;
4. rerun the affected local check;
5. continue.

Do not ask for user review.

### Scientific fault

Examples:

- target is not the frozen semantic operator;
- natural route authority differs from the planned route;
- actual kernel path is a different implementation family;
- required same-source pairing cannot be achieved;
- new source change would alter architecture semantics;
- result interpretation needs a broader/narrower claim.

Action:

1. freeze the affected task;
2. preserve evidence;
3. mark `STOP_SCIENTIFIC`;
4. continue independent pre-authorized tasks that do not depend on it;
5. surface the issue in the final report.

Only shared scientific faults stop the entire campaign.

## 6. Time scheduler

Final coordination supplies:

`CAMPAIGN_START_UTC`
`CAMPAIGN_DEADLINE_UTC`

Hard rule:

`NO_NEW_SCIENTIFIC_TARGET_AFTER = CAMPAIGN_DEADLINE_UTC - 2h`

During the final two hours:

- do not start new GPU target;
- do not start new simulator target;
- finish only already-running bounded work if it can still close safely;
- transfer;
- verify hashes;
- admit / ACK;
- generate reports;
- generate review packs;
- commit/push/remote-verify;
- release locks;
- clean worktrees.

If an active task cannot close before the deadline, terminate it through its tool-defined safe
boundary and mark `PARTIAL`.

## 7. 109 queue

### 109-M0 — existing-family native resource closure

Class: MANDATORY

Targets:

- Q05 Prefill Flash;
- Prefill GEMM Primary;
- Decode GEMV Primary;
- Decode Flash Primary-1.

Reuse accepted evidence first.
Collect only missing native / NCU evidence.

Primary-2 remains a tiny control and is not a dense profiling target.

### 109-M1 — E1 core matrix

Class: MANDATORY

`{down_proj,q_proj} × {M1,M256} × {raw,AWQ}`

Must close implementation fingerprint, numeric check, native timing, and selected resource
metrics.

Conditional dtype bridges are part of M1 if required by the measured runtime.

### 109-C1 — E3 natural / controlled routing

Class: CONDITIONAL

Entry gates:

- M1 accepted or explicitly closed without unresolved shared environment defect;
- accepted Q30 exact S2 state/replay authority remains intact;
- same expert execution backend can be used under the planned resident-weight policy;
- enough budget remains for N/P/U-active plus finalization.

Required first-wave cases:

- N natural;
- P histogram-preserving permutation;
- U-active active-set-preserving balancing.

No full dynamic trace by default.

### 109-O1 — G1 scenario extension

Class: OPPORTUNISTIC

Priority:

1. B1/T8192/D32;
2. B4/T2048/D32 if input/state authority can be frozen cleanly.

Native timing + lightweight census first.
No default detailed trace.

### 109-O2 — G2 same-quantized-weight execution decomposition

Class: OPPORTUNISTIC

Use an already-qualified E1 operator.
Compare actual AWQ path against bounded dequantized-reference execution only if exact frozen
runtime exposes a trustworthy reference path.

Do not build a new quantization backend.

### 109-O3 — G3 profiling protocol sensitivity

Class: OPPORTUNISTIC

Targets:

- Q05 Prefill Flash;
- Prefill GEMM Primary.

Compare approved NCU replay/cache-control variants if the installed NCU version supports them.
This is a measurement-protocol diagnostic, not a TLB cold/hot experiment.

### 109-O4 — G4 Llama raw shape holdout

Class: OPPORTUNISTIC

Reuse existing Llama-3.2-1B authority.
At most two linear semantic roles × M1/M256.
This validates shape trend only, not AWQ effect.

### 109-CAP — bounded detailed capture

Class: CONDITIONAL

May start only after pre-frozen selection rule identifies a pair whose effect:

- exceeds measured native noise;
- distinguishes at least one competing explanation;
- has exact semantic / implementation identity;
- fits remaining transfer/finalization budget.

Default maximum new detailed raw in this campaign: 16 GiB total.
Existing stricter per-target accepted limits remain in force.

## 8. 174 queue

### 174-M0 — approved post-repair requalification

Class: MANDATORY if final handoff enables it.

Exact run list comes from the post-repair review.
Reuse matching qualification runs rather than rerunning them.

Expected candidate identities:

- formal isolated repaired R0;
- formal isolated repaired I0;
- P34 repaired R0;
- P34 repaired Q05-only I0;
- P8 repaired R0;
- bounded translation/timeline sanity.

This list is a candidate template, not final authorization.

### 174-O1 — existing cross-family evidence analysis

Class: OPPORTUNISTIC / CPU-only.

Build a consistent family comparison from accepted trace/census/native evidence.
Do not infer TLB misses from page footprint.

### 174-C1 — first non-Attention repaired R0/I0 screen

Class: CONDITIONAL.

Entry gates:

- repaired runtime formally accepted by final handoff;
- Q05 minimal requalification is accepted;
- chosen non-Attention target has qualified consumer input;
- enough time remains for a complete paired experiment.

Priority:

1. Prefill GEMM Primary;
2. Decode GEMV Primary only if the first target is not qualified.

At most one family and one R0/I0 pair.

No architecture sweep.

## 9. Priority arbitration

If two READY tasks compete for the same resource:

1. mandatory task with dependency-unblocking value;
2. mandatory task with shortest bounded closeout;
3. conditional task that validates a central claim;
4. opportunity task in listed order.

Do not prioritize a task because pilot results appear more positive.

## 10. Adaptive branching allowed

The scheduler may adapt only inside pre-frozen branches.

Examples:

- if E1 shows dtype mismatch, run required bridge points;
- if E1 native effect is within noise, skip detailed capture;
- if Q30 state authority is missing, skip E3 and continue G1/G2/G3/G4;
- if long-context scenario cannot preserve frozen input identity, skip it rather than inventing input;
- if G3 profiler semantics are unavailable, report `COUNTER_OR_MODE_UNAVAILABLE` and continue.

## 11. Adaptive branching forbidden

Codex may not decide to:

- download a new model because a planned model fails;
- change model revision;
- substitute another semantic operator;
- reduce validation until a run passes;
- change simulator architecture to obtain a result;
- expand a sweep because a trend looks interesting;
- consume holdout results and then still call them independent validation.

## 12. Checkpointing

The 109 Goal should create a lightweight scheduler state after each accepted task:

`docs/vm_tlb/review_packs/<FINAL_109_PACK>/PIPELINE_STATE.json`

The 174 Goal should do the same in its own review pack.

State must include:

- campaign start/deadline;
- task status;
- task dependencies;
- run IDs;
- node164 ACK status;
- remaining eligible queue;
- scientific stops;
- budget skips.

The scheduler state is metadata, not a replacement for per-task receipts.
