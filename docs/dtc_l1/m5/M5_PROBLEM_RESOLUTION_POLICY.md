# M5 Problem Resolution Policy

Status: **ACTIVE — M5 v1 GOAL AUTHORIZED**

Authority: `M5_V1_APPROVAL.md` + `M5_EXPERIMENT_MATRIX.md`.

M5 is a long-running experimental Goal. Its default behavior is to **solve problems and continue**, not stop at the first missing workload, build error, assertion, timeout, or disappointing speedup.

The purpose is scientific: determine whether observed performance comes from the DTC mechanism, implementation fidelity, workload/input behavior, or the surrounding simulator platform.

---

## 1. Resolve-in-Goal issues

The following are normally **not stop conditions**:

- workload binary/input missing;
- suspected thesis workload alias or naming mismatch;
- wrapper/build/PTX extraction failure;
- parser/counter field missing;
- instrumentation definition mismatch;
- simulator assertion in M5 workload bring-up;
- Base/IO/OO operation-count mismatch;
- unexpected slowdown or lack of DTC benefit;
- IO/OO difference smaller/larger than expected;
- timeout while measurable simulator progress continues;
- a workload does not fill PIB/MSHR as the thesis discussion suggests;
- Tag-bank or downstream resource unexpectedly dominates;
- formal batch job interrupted;
- a new source-backed implementation bug in M5 code;
- a prior formal result becomes stale after a behavior/timing repair.

Codex must diagnose, repair/reconstruct where scientifically justified, regress, invalidate stale evidence when required, and resume the same substage.

---

## 2. Mandatory issue loop

For every nontrivial issue create/update an entry in `implementation/M5_ISSUE_LOG.md` with state:

`OBSERVED -> REPRODUCED -> CLASSIFIED -> REPAIRED/RESOLVED -> REGRESSED -> CLOSED`.

Required fields:

- issue ID and stage;
- Core/Framework/config/workload identities;
- minimal reproduction;
- source/thesis evidence;
- root-cause category;
- fix or resolution;
- changed files/commits;
- regression set;
- invalidated result IDs;
- resume point.

Do not leave a performance anomaly with only "different from thesis" as the diagnosis.

---

## 3. Performance diagnosis decision tree

When performance is weak, negative, or very different from the thesis, apply this order.

### A. Correctness and identity

Check first:

- same workload/PTX/input across Base/IO/OO;
- exact dynamic instruction and source-domain op counts;
- application output;
- PIB/lower/dependency/credit/Ref drain;
- no assertion/watchdog/stale-fill issue.

Failure here => **IMPLEMENTATION/EXPERIMENT INFRA**. Fix and rerun; do not interpret performance.

### B. Does Base exercise the intended structural bottleneck?

Inspect:

- PIB peak/full;
- true Tag/cacheline allocation failures;
- MSHR entry/merge failures;
- miss-queue/downstream pressure;
- coalesced unique 128B references per memory instruction;
- average concurrent misses.

If the paper-discussed workload never stresses the relevant Base structure => **WORKLOAD / INPUT / PLATFORM FIDELITY**. Recheck algorithm mapping, standard dataset, launch geometry, occupancy, and config. Do not select inputs by DTC speedup.

### C. Does DTC remove the Base bottleneck?

If Base is structurally limited but DTC does not increase admissible/live concurrent misses, inspect:

- DTC PIB service;
- Tag-bank consistency;
- physical allocation/reclaim;
- pending-hit merge;
- lower issue/cap;
- unintended conventional path;
- common coalescing and pipeline throughput.

Failure => **IMPLEMENTATION/MODELING FIDELITY**. Repair while preserving frozen architecture, rerun M1-M4 sentinels, invalidate affected M5 runs, resume.

### D. DTC increases concurrency but performance does not improve

Inspect:

- natural lower outstanding cap;
- L2/NoC/DRAM saturation;
- average/queue latency;
- request bytes/traffic;
- duplicate-after-eviction ratio;
- bandwidth utilization proxies;
- compute intensity.

Classify as **DOWNSTREAM/PLATFORM BOTTLENECK**, **TRAFFIC SIDE EFFECT**, or **COMPUTE-BOUND**. Do not redesign L2/NoC/DRAM merely to force the thesis speedup. A valid mechanism result may show increased concurrency with no speedup under a saturated downstream platform.

### E. OO vs IO behavior

If OO gives little advantage over IO, inspect:

- IO head-not-ready and ready-younger HOL cycles;
- OO out-of-order retire count;
- long-latency store/atomic presence;
- memory-latency variance.

If the workload contains little HOL opportunity, classify as **WORKLOAD BEHAVIOR**. If HOL exists but OO cannot exploit it, inspect implementation fidelity.

### F. Genuine mechanism limitation

If source/workload/config/implementation are all sound and the result is still weak or negative, classify it as **GENUINE MECHANISM LIMITATION** and keep the data. Do not tune it away.

---

## 4. Workload recovery policy

Missing ready binaries are not a stop condition.

Codex should:

1. search current workload checkout;
2. resolve aliases using algorithm/source comparison;
3. obtain canonical PolyBench/Parboil source where permitted;
4. build a source-equivalent wrapper and extract PTX;
5. choose standard input according to the Base-only full-load policy;
6. record provenance and mapping status;
7. validate output before formal use.

No algorithm substitution is allowed merely because a different benchmark is easy to run.

---

## 5. Timeout policy

A fixed wall-clock limit is a diagnostic tool, not a deadlock definition.

On timeout:

1. sample simulator progress, committed instructions/cycles, queue occupancy, and last-progress cycle;
2. classify `SLOW_BUT_PROGRESSING`, `RESOURCE_STALL_WITH_PROGRESS`, `NO_PROGRESS_DEADLOCK`, or `OTHER_HARD_FAILURE`;
3. if progressing, a longer bounded allowance or smaller canonical-but-still-full-load standard dataset may be used, based on workload/runtime criteria rather than speedup;
4. if no-progress, find root cause and repair/classify before continuing.

Do not record an arbitrary timeout as performance zero.

---

## 6. Formal-data invalidation policy

### Behavior/timing change

If a Core change can affect simulation behavior or timing:

- all downstream FORMAL runs produced from the old behavior anchor are `OBSOLETE`;
- rerun affected stages after regression.

### Instrumentation-only change

If source review suggests counters only:

1. run exact sentinel differential for cycles, dynamic instructions, and existing memory counts;
2. if exactly neutral, old performance cycles may remain usable where their required counters already exist;
3. any new/changed counter requires rerunning the workloads needed for that metric.

Every retained result must explicitly state why the old behavior SHA remains comparable.

---

## 7. Regression after M5 Core changes

Any M5 Core repair affecting load/cache completion or resource timing must at minimum rerun:

- release build;
- all DTC CTests;
- LEGACY VecAdd;
- PAPER_BASE VecAdd;
- PAPER_IO VecAdd;
- PAPER_OO VecAdd;
- MODERN_OO_SECTOR VecAdd;
- one M4 Store/Atomic/bypass mixed sentinel if the touched code can affect non-load paths.

Mechanism-specific fixes add the relevant M2/M3/M4 regression case.

Do not regenerate old review packs unless their accepted semantics changed; cross-reference the regression from M5 evidence.

---

## 8. What may actually pause/stop the persistent Goal

Codex should exhaust source/thesis/canonical-workload evidence before escalating. A Goal pause is reserved for a real researcher-decision boundary such as:

1. the only apparent fix requires changing a frozen M0/M1-M4 architecture semantic rather than correcting implementation fidelity;
2. two source-supported, scientifically different metric/workload interpretations remain possible and the thesis does not resolve them;
3. a required compute algorithm cannot be reconstructed or verified even after canonical-source audit, and accepting a proxy would materially change the experiment meaning;
4. a new finding invalidates the user's explicitly frozen M5 metric definition;
5. compute M5 reaches its planned terminal state `M5_COMPUTE_READY_FOR_REVIEW`.

Graphics unavailability does **not** stop compute M5. It remains a parallel preparation track and can end in a documented feasibility classification.

---

## 9. Goal communication policy

Ordinary progress messages, safe checkpoint commits, resolved bugs, completed workload recovery, individual figure completion, or surprising-but-classified performance are not human-approval boundaries.

At every substage PASS, follow `M5_HANDOFF_CONTRACT.md`: write the handoff, commit/push compact evidence, update `codex_handoff/LATEST_REPORT.md`, and continue automatically.

If a stage has an active issue, `LATEST_REPORT.md` should say `RESOLVING_ISSUE` and identify the issue ID/resume point while work continues. Use `RESEARCHER_DECISION_REQUIRED` only for the pause conditions in section 8.
