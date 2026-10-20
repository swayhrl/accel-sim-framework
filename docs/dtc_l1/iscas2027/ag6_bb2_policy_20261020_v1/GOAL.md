# DTC-L1 / ISCAS 2027 — Lane BB2: Resource Policy B CPU-only Qualification V1

**Authorization:** User explicitly approved a fast, independent **policy-design + CPU-only qualification** after Lane BB's frozen-data diagnosis. **Not** an authorization to implement/activate a new production runtime policy, start simulator, or grant any AG6/BA simulation budget.

**Execution:** ORIGINAL §huangrulin-174§ account/container only; new Codex session and independent worktree/output root. Do not use §174-new§/§109§.
**Branch:** §hrl/iscas2027-dtc-ag6-bb2-policy-174-v1§.
**Frozen origin:** §swayhrl/accel-sim-framework§ commit §ee61be47f5d2e6cbeaa028791f9674b8f092ee86§.
**Completed BB evidence:** §docs/dtc_l1/review_packs/DTC_AG6_IO_DIAG_20261020_V1/§; especially §LATEST_REPORT.md§, §RECOMPUTATION.json§, §STOP_RECONSTRUCTION.tsv§ (28 lines), §OWN_PROCESS_COUNTERS.tsv§, §IO_SOURCE_PROVENANCE.md§, §ROOT_CAUSE_MATRIX.md§, §RESOURCE_POLICY_OPTIONS.md§, §BUDGET_AND_SCIENCE_BOUNDARY.json§.
**Original BA closed anchor:** §d9c192544622579a93d3efad98f56f82536c2fbe§ and its §execution/ag6_actual_cohort_stop_v2/§ receipts. Read only. Historic executed monitor pinned through §62323c40df0add726cae52a96ca946e589f00343§; never infer code from current filename.

## 0. Scientific/authority invariants (must preserve)

- Original AG6: **1/4 actual starts consumed**, AE_GEMM runtime STOP, **0 accepted performance**, remaining 3 registered UUIDs SEALED. **No refund/replacement/restart/UUID reuse**. BA separately **0/32**, BA §/root§ is sole future fullsim dispatcher.
- Final F is NULL; §O = K0 / OO128 / Tag64x8 / AE0 / AD0§ remains **PROVISIONAL_O_WITH_INCOMPLETE_OPT_SCREEN**. Do not assert AE/AD benefit or value correctness from unfinished/fixture results; leave old §SELECTION§, 44/GM12, T/U and CORE intact.
- Current hard floor **strictly >5GiB free on actual output mount** with expected writes; original paired host+cgroup R2 preflight, I/O and memory/OOM controls, exact process authority and existing guard requirements unchanged. The old §IO_FULL_PSI_GT25_THREE_GE30S_SAMPLES§ STOP was correctly applied and is permanently historical.
- **This lane has zero simulator/model/test-kernel/canary/trace-capture starts, zero new performance UUIDs, no Core or production guard changes, no process signals, no supervisor or service launch, no storage cleanup or host/cgroup configuration changes.** CPU-only pure-policy tests are allowed below. No touching active or foreign raw/files/locks or other project workloads. No model binary or large trace reads.

## 1. Objective and pace

Produce a **scientifically defensible, minimal Policy B contract and CPU-only prototype qualification**, in one continuous bounded Goal. Prioritize decisions over audit ceremony; avoid extra rounds, repeating already accepted AG5/SEM/ROB/BB work or waiting for missing historical telemetry. Read the closed indexes once, implement only what directly qualifies new decision semantics, publish, STOP. Normal formatting/source-only test issues: fix and continue without asking. Science/authorization changes: STOP.

**Question:** How could a subsequent separately authorized AG6 cohort avoid treating high *shared-cgroup* I/O PSI alone as a proof of no simulator progress, while keeping **preflight admission strict and actual safety/fairness safeguards**?

## 2. Phase A — Freeze observable signals, scope and policy draft (source-only)

Read BB's complete diagnosis and inspect only the relevant frozen monitor/guard and already available lightweight simulator progress interface in source (no compiler, no simulation, no trace). Clearly distinguish:
1. §preflight§: existing complete paired host+cgroup R2; BOTH host and cgroup I/O full avg10 threshold and all other frozen controls still apply, with >5GiB + projected writes.
2. §runtime_psi§: cgroup I/O full avg10 threshold of 25% proposed as a **warning/diagnostic signal**, not automatically §STOP§. Host/cgroup populations differ; PSI is a stall indicator, not utilization or per-simulator progress.
3. §runtime_hard_safety§: existing hard disk/expected growth, OOM changes, memory/swap safety, ownership/identity, deadline, explicit signals/abort conditions; identify exact existing threshold and which are non-negotiable. Never silently remove a former safeguard: for runtime I/O safety, state clearly which new measurable impact, deadline or fallback rule replaces the prior unconditional STOP; otherwise classification is **DESIGN_ONLY_NOT_SAFE_FOR_PRODUCTION**.
4. §semantic_progress§: name candidate monotonic metrics with exact semantics, such as retired/committed *simulated* instructions or finished CTA/kernel for the same exact root PID/start_ticks, same input/ROI and monotonic timestamp. Record where the existing simulator exposes them, if at all. Neither OS CPU ticks, log growth, trace reads nor mere simulated-cycle advancement alone proves completed work. For long, legitimately non-retiring phases define how the future contract would avoid false no-progress stops; if that cannot be grounded, flag unresolved.
5. §missing/stale/reversed§ timestamps, missing metric, identity discontinuity and monitor failure must fail closed. Do not invent a production window duration or loosen other limits. A CPU prototype may use clearly marked **illustrative caller-supplied test parameters** but cannot turn them into production defaults.

Deliver §POLICY_B_CONTRACT.md§ and §PROGRESS_SIGNAL_FEASIBILITY.md§ with precise state transitions, responsibilities, limits, missing-data behavior, side effects and remaining blockers. Include minimal comparison with A/C. **Policy is proposed, not activated.**

## 3. Phase B — Small isolated CPU-only evaluator and tests

Implement a **pure, opt-in, offline** evaluator under the NEW BB2 review pack (e.g. §policy_b_offline.py§, §test_policy_b_offline.py§), consuming immutable JSON/sample dictionaries and user-supplied *scenario parameters*. No imports or modifications of active BA runtime/guard, no monitoring background process and no calls that spawn a simulator/fixture. Keep code short and verifiable.

State outputs must distinguish:
- §PRELAUNCH_HOLD§ (any failed paired R2/identity/storage/authority);
- §RUNTIME_WARNING§ (PSI alone high but verified semantic progress or within explicitly modeled grace);
- §RUNTIME_STOP_SAFETY§ (actual frozen safety violation);
- §RUNTIME_STOP_NOPROGRESS§ (verified no semantic progress over an explicitly supplied, valid bounded watchdog after handling legitimate long phases);
- §RUNTIME_INSUFFICIENT_EVIDENCE§ / conservative HOLD/STOP (missing, stale, contradictory progress, inconclusive scope, monitor gaps). Unknown must NEVER silently become qualified progress or PASS;
- §COMPLETE_CANDIDATE§ only for natural completion with complete strict/runtime/identity closure, **not** a performance PASS from evaluator alone.

Tests should target at least these **distinct scientific cases**, not proliferate: strict preflight host/cgroup PSI refusal; isolated high cgroup PSI with *synthetic* monotonic valid progress; repeated high PSI without progress and bounded watchdog; missing/stale/nonmonotonic progress; hard disk/estimated writes/memory/OOM/identity protection; recovery/re-entry behavior; actual STOP/run-end never becoming success; no accidental BA/AG6 budget allocation. A synthetic progress sequence must be labeled §DECLARED_SYNTHETIC§ and cannot be relabeled as observed AE_GEMM.

Before CPU-only test subprocess entry, follow the project's CURRENT pre-entry resource/authority contract for this exact lightweight test role, including actual disk strict >5GiB, headroom and full paired R2 where required. If this cannot be met, publish source + expected tests with §NOT_EXECUTED_RESOURCE_HOLD§; do not weaken the contract or spin/retry repeatedly to obtain a pass. Keep tests single-worker, bounded, no performance emulation, no GPU, no CLI shell process trees beyond the necessary interpreter. Preserve exact receipts of real tests if run.

## 4. Phase C — One offline 28-record evaluation and safety case

Feed BB's **original closed 28 rows** and immutable STOP reconstruction into:
- a verified OLD-policy reproduction (STOP at the third qualified high PSI reading), and
- the PROPOSED B evaluator with §semantic_progress=UNAVAILABLE§ (the historical record lacks this measurement). This MUST NOT conclude the old AE_GEMM would have completed or was safe indefinitely. Label counterfactual as §UNDETERMINED_PROGRESS_NO_PRODUCTION_PROMOTION§ and keep historical STOP unchanged.

Optionally pair *declared synthetic* valid-progress/no-progress sequences with the same PSI values to illustrate branches; keep such rows separately labeled and free of speedup. Calculate only logged timings and decisions; no made-up instruction counts, GPU completion events or resource limits.

Summarize measurable overhead and safe scope. BB observed the monitor repeatedly rehashed mappings (8,369 captures, ~100GB rchar). Propose an optional **audit-preserving**, source-only reduction strategy using immutable executable/library identity and event-triggered verification, but do not implement it or relax exact PID/start_ticks/generation/loaded-image checks. Distinguish ideas from proven overhead savings.

## 5. Evidence pack and STOP

Under §docs/dtc_l1/review_packs/DTC_AG6_POLICY_BB2_20261020_V1/§ publish at minimum:
- §LATEST_REPORT.md§: concise scientific verdict, CPU qualification results, unclosed conditions and recommendation;
- §POLICY_B_CONTRACT.md§ and §PROGRESS_SIGNAL_FEASIBILITY.md§;
- §policy_b_offline.py§ and §test_policy_b_offline.py§ (if code/test admission allows; otherwise source-only);
- §HISTORICAL_28_ROW_REPLAY.tsv§: exact old decisions vs new proposal with unknown semantic progress;
- §CPU_QUALIFICATION.json§ and §SCIENCE_AND_BUDGET_BOUNDARY.json§ with exact source/CPU test execution results, no simulator starts, AG6 1/4, BA 0/32, F null;
- small §EVIDENCE_INDEX.md§ with original BB anchor/exact immutable hashes/limited local resource receipts.

No repeated hashing of large files, no copied raw/ELF/trace, no excessive audit metadata. Commit, push, independently fetch exact HEAD/tree/relevant blobs, verify clean worktree. If files are self-referential, use a second lightweight seal commit. Report exact branch/HEAD, what is CPU-tested vs source-only, production blockers, and **whether any new independent AG6 cohort can be recommended for a future explicit authorization**. Then STOP.

## 6. Decision boundary

This Goal **authorizes no production I/O gate change and no simulator or GPU collection**. Passing pure CPU tests is not full guard/monitor integration qualification. If real semantic progress is not currently available, do not claim production-ready policy; provide a minimal prospective integration plan with source-bound, opt-in, fail-closed hooks and a single planned end-to-end qualification under future authorization. The user alone decides new cohort budget, changing a runtime stop rule, and release of fullsim. No use of the unstarted three old AG6 UUIDs.

Priority: **Finish the smallest scientifically meaningful package promptly; one pass, minimal moving parts, publish and stop.**