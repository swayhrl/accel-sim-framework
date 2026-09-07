# DTC FAST64 Continuous Execution Runbook

Status: **MANDATORY FOR GOAL MODE**

This runbook carries FAST64 from pivot through final review without ordinary
human pauses.

## 1. Start/resume procedure

At Goal start and after every interruption:

1. verify Framework branch is `hrl/decoupled-l1-fast64-v0`;
2. fetch/read the current branch HEAD;
3. verify both Core authorities: the `15cfa76e...` mechanism behavior anchor
   and the `bbcbb5e...` FAST64 formal instrumented Core/runtime; never launch
   a formal row under the former merely because it is the semantic anchor;
4. read, in order:
   - `FAST64_RESEARCH_SCOPE.md`;
   - `FAST64_PLATFORM_CONTRACT.md`;
   - `FAST64_WORKLOAD_MANIFEST.tsv`;
   - `FAST64_EXPERIMENT_MATRIX.md`;
   - `FAST64_ACCEPTANCE_CONTRACT.md`;
   - `FAST64_RESULT_IDENTITY.md`;
   - `FAST64_HEAVY_EVIDENCE_BOUNDARY.md`;
   - latest FAST64 handoff(s);
5. inspect actual live processes before launching anything;
6. never duplicate an already-valid or still-live row.

## 2. Continuous stage machine

Execute continuously:

`FAST64.0 -> FAST64.1 -> FAST64.2 -> FAST64.3 -> FAST64.4 -> FAST64.5 ->
FAST64.6 -> FAST64.7 -> FAST64_COMPLETE_READY_FOR_REVIEW`

A stage transition is not a human approval point.

When all HARD acceptance items pass:

1. write/update the stage handoff;
2. update compact registry/evidence;
3. run `git diff --check`;
4. stage only intended files explicitly (never `git add .` / `git add -A`);
5. commit with a stage-specific message;
6. push the FAST64 branch;
7. reread this runbook and the next-stage acceptance gate;
8. continue automatically.

## 3. Ordinary-problem resolution policy

FAST64 Goal mode must **solve ordinary problems instead of stopping**.

For any ordinary issue, use:

`OBSERVE -> REPRODUCE -> CLASSIFY -> SOURCE/TRACE/CONFIG INVESTIGATE ->
REPAIR/RECONSTRUCT -> REGRESS -> INVALIDATE AFFECTED IDENTITY -> RESUME`

Ordinary issues include, but are not limited to:

- missing dependency/tool;
- build error;
- trace path/layout mismatch;
- kernelslist/postprocess mismatch;
- parser defect;
- stale config option;
- workload-local source incompatibility;
- storage-path problem;
- scheduling/worker failure;
- timeout with healthy progress;
- assertion caused by a source-reachable generic implementation defect;
- missing counter/accounting path;
- incorrect output checker integration;
- one workload failing while independent workloads remain runnable;
- negative or weak speedup;
- host-load/concurrency inefficiency.

Do not ask the researcher merely because the first attempt failed.

## 4. True researcher-decision boundaries

Pause only when continuing would require one of the following:

- changing DTC architectural semantics;
- changing FAST12 membership after performance observation;
- changing a frozen workload input for scientific reasons;
- replacing the 64-SM FAST64 platform definition with a materially different
  research platform;
- accepting a proxy that changes the experiment's meaning;
- choosing between irreconcilable source interpretations that materially alter
  the mechanism or claim;
- deleting unique scientific evidence without an existing retention proof;
- credentials/hardware/storage genuinely unavailable with no source-correct
  alternative;
- final researcher review after `FAST64_COMPLETE_READY_FOR_REVIEW`.

## 5. Parallel scheduling policy

Logical analysis order does not imply physical serialization.  Distinguish
`LOGICAL_STAGE_ACCEPTANCE` (strict FAST64.0 -> FAST64.7 HARD-gate order) from
`PHYSICAL_PRECOMPUTED_ACQUISITION` (identity-frozen rows labeled pending until
their owning stage can accept them).

Before FAST64.1 closes, the only authorized later-stage acquisition is the
source-reachable coupled lower-cap/create-queue FAST64.2 positive stress,
labeled `PRECOMPUTED_FAST64_2_COUPLED_STRESS_PENDING_FAST64_1_ACCEPTANCE`,
plus isolated FAST12 Base@8192 rows labeled
`PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE`.  The completed high-cap stress is
retained as `FAST64_2_HIGH_CAP_NEGATIVE_CONTROL`, not as a positive result.
Do not precompute main-matrix IO/OO rows before FAST64.2 repair PASS.

After FAST64.2 PASS, launch missing Base/IO/OO rows through one dynamic pool;
IO/OO rows obtained before FAST64.3 closes are
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE` and cannot influence membership,
input, or Base-characterization decisions.  Frozen one-dimensional sensitivity
rows may run concurrently after FAST64.2 PASS as
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`.

Whenever dependencies permit:

- independent workloads run concurrently;
- IO and OO rows from different workloads may run concurrently;
- parsing/analysis may overlap unfinished independent rows;
- sensitivity preparation may begin after FAST64.4 identities are frozen even
  while FAST64.5 plots are being generated.

Before each long wave measure:

- cgroup CPU quota/cpuset;
- total and M5 simulator workers;
- aggregate CPU/load;
- p50/p90/p95/max RSS;
- MemAvailable;
- swap `si/so`;
- iowait;
- trace-store read throughput;
- output filesystem free space.

Derive a current `N_safe`; do not retain an old worker limit blindly.  Prefer
one simulator per distinct physical core before SMT.  Ramp in controlled steps
and retain an increase only when aggregate simulated instructions/s materially
improves without CFS throttling, swap pressure, I/O pressure, major-fault
growth, or unsafe output headroom.

Use dynamic refill: when one row exits, validate it and immediately dispatch
the highest-priority eligible row if resources remain safe.

Use `util/dtc_l1/run_fast64_dynamic_pool.sh` for an authorized formal wave.
It pins one Framework source identity for the pool, records isolated rows,
strict-validates each natural terminal before refilling its physical CPU slot,
and fails closed for a missing supervisor, missing terminal state, identity
mismatch, or parser/accounting failure.  It does not authorize a stage; its
pending-class policy remains enforced by the row dispatcher.

Before FAST64.6 acquisition, use the frozen source-control mapping in
`FAST64_SENSITIVITY_CONFIG_PLAN.md`.  Do not generate the sensitivity configs
before FAST64.2 repair PASS.

## 6. Priority within stages

### FAST64.1

1. resolve platform shell/config diff;
2. freeze payload identities;
3. smoke NN/BICG;
4. close lower-cap qualification.

### FAST64.2

1. natural BICG triplet;
2. forced queue-full stress;
3. parser/accounting classification proof.

### FAST64.3

Run all 12 Base rows through a worker pool. Do not drop low-pressure rows.

### FAST64.4

Reuse Base rows and acquire all 24 IO/OO rows. Prefer dispatch diversity so a
single heavy workload cannot hold the whole batch.

### FAST64.5

Analyze as rows close; final PASS waits for all 12 triplets and all causal
classifications.

### FAST64.6

Run frozen BICG/GESUMMV/Btree sensitivity points with one-dimensional changes.

## 7. Runtime/cost controls

A run with healthy forward progress is not failed merely because it is slow.
However, FAST64 exists to avoid avoidable heavy payloads.

For unexpected high cost:

1. verify payload identity and size;
2. verify host throughput/placement;
3. verify observer A1 is active;
4. verify no accidental C2P mechanism or wrong cache geometry was imported;
5. compare simulated instructions/s as well as cycles/s;
6. do not truncate formal runs with a max-cycle cutoff merely to save time;
7. if a frozen workload is unexpectedly pathological, classify the cause and
   ask the researcher only if membership/input meaning would need to change.

## 8. Git/evidence discipline

- Never commit raw multi-GB trace/run outputs.
- Commit compact manifests, hashes, CSV summaries, and raw-log indices.
- Preserve untracked user/scientific artifacts.
- Never use broad staging commands.
- Do not rewrite historical M5 evidence.
- Every source/config behavior change requires an affected-result invalidation
  statement.

## 9. Completion behavior

When FAST64.7 passes:

- push final compact evidence;
- set terminal state `FAST64_COMPLETE_READY_FOR_REVIEW`;
- stop launching new scientific runs;
- present a concise final report of performance, mechanism evidence,
  sensitivities, limitations, and any auxiliary work still running.
