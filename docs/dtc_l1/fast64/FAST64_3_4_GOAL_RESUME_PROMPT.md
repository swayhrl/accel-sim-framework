# FAST64 Goal Resume Prompt — FAST64.3/4 Prepared

Use this as the Goal-mode startup instruction after syncing the current
`hrl/decoupled-l1-fast64-v0` branch.

```text
START / RESUME GOAL MODE NOW.

GOAL:
Complete the authorized DTC FAST64 state machine continuously through:

  FAST64_COMPLETE_READY_FOR_REVIEW

Framework branch:
  hrl/decoupled-l1-fast64-v0

Do NOT restart the project from FAST64.0 and do NOT duplicate valid or live
scientific rows.

============================================================
0. SAFE RESUME FIRST
============================================================

Before changing anything:

- inspect `git status`;
- fetch the current remote branch;
- preserve every untracked generated scientific-evidence directory;
- never `git clean` scientific evidence;
- if tracked local state is clean, fast-forward to remote;
- if tracked local changes exist, reconcile them source-correctly rather than
  reset/overwrite them;
- inspect actual live simulator/controller processes before launch;
- inspect existing compact evidence before deciding any row needs rerun.

Never use:
  git add .
  git add -A

============================================================
1. REQUIRED AUTHORITY TO READ
============================================================

Read and obey in this order:

1. FAST64_SINGLE_GOAL_CONTRACT.md
2. FAST64_EXECUTION_RUNBOOK.md
3. FAST64_ACCEPTANCE_CONTRACT.md
4. FAST64_EXPERIMENT_MATRIX.md
5. FAST64_STAGE_HANDOFF_SCHEMA.md
6. FAST64_3_4_EXECUTION_CONTRACT.md
7. handoffs/FAST64_3_BASE_CHARACTERIZATION.md
8. handoffs/FAST64_4_PRIMARY_MATRIX.md
9. current FAST64_CODEX_HANDOFF.md
10. current relevant FAST64.1/2/precompute handoffs and generated compact evidence

The new FAST64_3_4_EXECUTION_CONTRACT.md refines execution/reuse/closeout for
FAST64.3 and FAST64.4; it does not weaken FAST64_ACCEPTANCE_CONTRACT.md.

============================================================
2. CURRENT RESUME BOUNDARY
============================================================

Do not assume the stale remote handoff is the newest execution fact if local
immutable generated evidence is newer.

First reconcile the actual current state.

If the complete FAST64.1 immutable R2 alias-aware evidence exists locally and
strictly proves:

- 7/7 natural terminal exit 0;
- exact Core/runtime/A1/scientific Framework/config/payload identities;
- one canonical perf epoch per row with only the documented exact symlink
  alias normalization;
- strict terminal/accounting validation for all seven;
- BICG IO candidate/high EXACT_METRIC_MATCH;
- BICG OO candidate/high EXACT_METRIC_MATCH;
- GESUMMV IO candidate/high EXACT_METRIC_MATCH;
- required candidate cap-full events == 0;

then review it, create the compact evidence manifest, close FAST64.1 as:

  FAST64_1_PLATFORM_PASS

commit/push the compact closeout, and continue immediately.

Do not rerun FAST64.1 merely because the old frozen reader correctly
fail-closed on the already-proven `perf_counter.csv.gz` symlink alias defect.
Keep that frozen failure as negative controller evidence and use the versioned
alias-aware reader only under its documented fail-closed rules.

============================================================
3. FAST64.2 MUST BE SOLVED, NOT SKIPPED OR USED AS A STOP
============================================================

FAST64.2 remains a real logical gate before FAST64.3 promotion and FAST64.4
main IO/OO acquisition authority.

Reuse exact-identity R2 Base/IO/OO normal-triplet evidence where the contract
permits; do not rerun it by default.

For the forced lower-create-queue stress:

- preserve the existing high-cap negative control;
- preserve prior strict negative-pressure attempts as diagnosis evidence;
- inspect the frozen Core/source sequencing and actual observed queue/credit
  behavior;
- construct the smallest source-correct diagnostic that actually reaches the
  required positive path;
- do not change production DTC architectural semantics merely to generate an
  event;
- require natural termination, positive lower-cap/create-queue pressure,
  forward progress, no old assertion, conservation, and terminal drain.

If the first diagnostic does not create pressure, that is an ordinary problem:
inspect why, change only the diagnostic configuration/driver in a
source-correct way, regress, and try again. Do NOT stop and ask the researcher
merely because one stress attempt is negative.

Only when all FAST64.2 HARD requirements pass:

  write/update FAST64_2_REPAIR_QUALIFICATION.md
  -> FAST64_2_REPAIR_PASS
  -> commit/push
  -> continue automatically.

============================================================
4. FAST64.3 — EXECUTE BASE CHARACTERIZATION
============================================================

Use:
  FAST64_3_4_EXECUTION_CONTRACT.md
  handoffs/FAST64_3_BASE_CHARACTERIZATION.md

The roster is exactly the frozen FAST12 12 workloads.

BEFORE LAUNCHING ANY BASE ROW:

- search all current strict-valid compact evidence;
- promote exact-identity valid precomputes after FAST64.1/2 PASS instead of
  rerunning them;
- verify identity/metric completeness, not just workload name.

Known/recent precompute evidence may exist for BICG, NN, ATAX, DWT2D, GEMM,
GESUMMV, or others. Discover what actually exists and reuse only after exact
validation.

Acquire only missing Base rows.

Use immutable/versioned execution controllers, fresh namespaces, exact frozen
identity, topology-aware placement, and measured dynamic N_safe.

Run independent missing Base rows concurrently when resources are safe.
Do not serialize workload-by-workload unnecessarily.

For every accepted Base row collect all required groups in the prepared
handoff:

- cycles/instructions;
- PIB pressure;
- true Tag/cacheline allocation pressure;
- Tag-bank arbitration separately;
- MSHR entry/merge pressure;
- miss/lower/downstream pressure;
- lower/live-miss lifecycle;
- supported cache/traffic fields;
- host runtime/RSS planning data;
- terminal accounting/drain;
- cap-full observation.

Do not drop low-pressure or expensive workloads.
Do not retune membership or inputs.

As rows close, validate and update compact tables incrementally.

FAST64.3 can PASS only after all 12 accepted Base rows and all metric
completeness requirements are closed.

Then set:

  FAST64_3_BASE_PASS

commit/push and continue immediately.

============================================================
5. FAST64.4 — ACQUIRE THE PRIMARY MATRIX
============================================================

Use:
  FAST64_3_4_EXECUTION_CONTRACT.md
  handoffs/FAST64_4_PRIMARY_MATRIX.md

The matrix is exactly:

  12 workloads x {Base, IO, OO} = 36 rows.

Reuse all 12 accepted FAST64.3 Base rows.
Reuse exact-identity valid IO/OO precomputes if any exist under the authorized
classification and pass promotion checks.

Acquire the missing IO/OO rows only after FAST64.2 PASS.
They may physically run before FAST64.3 logical PASS as
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`, but their results must not change
FAST12 membership/input or Base decisions.

Use a dynamic worker pool and high safe concurrency.
Optimize for aggregate useful simulated throughput and total wall-clock time,
not for arbitrary worker count.

Do not serialize by workload when independent rows can run concurrently.

For each triplet require:

- exact common payload identity/order;
- common Core/runtime/A1/scientific Framework identity;
- only documented mode-required config differences;
- instruction/source-operation identity where required;
- natural exit zero;
- strict parser acceptance;
- exact lower/dependency conservation;
- final PIB/inflight/lower drain;
- OO active-ref/reclaim drain;
- no unresolved cap binding.

Compute:

  speedup_IO = cycles_BASE / cycles_IO
  speedup_OO = cycles_BASE / cycles_OO

and geometric means over exactly all 12 frozen members.

Keep negative and zero speedups.
Never tune a workload because of its result.

When all 36 rows are valid and all prepared FAST64.4 HARD checks pass:

  FAST64_4_PRIMARY_PASS

commit/push and continue automatically into FAST64.5.

============================================================
6. PROBLEM-SOLVING MODE — DO NOT STOP ON ORDINARY FAILURES
============================================================

For every ordinary problem, continue the Goal and use:

  OBSERVE
  -> REPRODUCE
  -> CLASSIFY
  -> INVESTIGATE SOURCE / TRACE / CONFIG / PARSER / HOST
  -> TRY A SOURCE-CORRECT REPAIR OR RECONSTRUCTION
  -> REGRESS
  -> INVALIDATE ONLY AFFECTED IDENTITIES
  -> RERUN ONLY WHAT IS AFFECTED
  -> RESUME

Ordinary problems include:

- parser/validator bugs;
- normal file aliases or output-layout changes;
- controller/lock/FD/process-lifetime defects;
- missing telemetry or metric extractor bugs;
- build/config incompatibility;
- trace path/layout mismatch;
- one workload assertion from a generic source defect;
- resource scheduling/concurrency problems;
- disk path/capacity management after evidence is safely retained;
- slow simulation;
- one row failure;
- negative/weak performance;
- a diagnostic that does not initially produce the intended pressure.

Do NOT mark Goal globally blocked after the first failed attempt.
Do NOT ask the researcher for ordinary implementation/execution choices.

Pause only if continuing truly requires:

- changing DTC architectural semantics;
- changing frozen FAST12 membership/input for scientific reasons;
- materially redefining the FAST64 platform;
- accepting a proxy that changes the research question;
- choosing between irreconcilable source interpretations that materially
  change the mechanism/claim;
- deleting unique evidence without a safe retained copy;
- unavailable mandatory hardware/credentials/storage with no source-correct
  alternative;
- final review at FAST64_COMPLETE_READY_FOR_REVIEW.

A HARD gate blocks stage/result promotion, not useful Goal execution.

============================================================
7. EFFICIENCY AND PARALLELISM
============================================================

Use measured dynamic N_safe.

Before every major wave measure:

- cgroup CPU quota/cpuset and throttling;
- physical-core topology;
- live worker count and aggregate useful CPU;
- p95/max RSS;
- MemAvailable and cgroup memory headroom;
- swap in/out delta, OOM, PSI;
- iowait;
- output free space;
- aggregate simulated instructions/sec or equivalent useful progress.

Prefer one worker per physical core before SMT.
Ramp/refill dynamically.
Increase concurrency while aggregate useful throughput improves and resource
safety remains healthy; back off if throughput degrades or real memory/I/O
pressure appears.

Do not confuse host loadavg with cgroup CPU saturation.

============================================================
8. EVIDENCE / GIT DISCIPLINE
============================================================

- preserve untracked generated scientific evidence;
- never broad-stage;
- never commit raw multi-GB simulator outputs;
- commit compact JSON/TSV/CSV/manifests/handoffs/raw-log indices;
- every rerun uses a fresh namespace;
- every obsolete attempt remains explicitly classified;
- do not modify a live long-running script/controller in place; create a
  versioned future-only path instead;
- `git diff --check` before every push.

============================================================
9. CONTINUE BEYOND FAST64.4
============================================================

FAST64.4 is not the terminal Goal.
After FAST64_4_PRIMARY_PASS continue automatically:

  FAST64.5 causal analysis
  -> FAST64.6 sensitivity
  -> FAST64.7 final synthesis
  -> FAST64_COMPLETE_READY_FOR_REVIEW

Do not stop at normal stage boundaries.

START THE GOAL NOW.
```
