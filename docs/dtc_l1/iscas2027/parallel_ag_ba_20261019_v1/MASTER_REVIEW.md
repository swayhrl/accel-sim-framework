# DTC-L1 AG5 + BA parallel coordination review — 2026-10-19

**Status: PUBLISHED NON-EXECUTABLE PLAN. This document creates NO simulation budget, UUIDs, executable prerregistration, approval to restart AG3/AG4, background dispatch, or change to BA's published 32-start cap.**

## Authorities and evidence

- AG5 completed CPU-only repair at Framework `9793e998d60cb5a7f064a46ecd6be242eda61b7c`, `docs/dtc_l1/review_packs/DTC_LANE_AG5_RETIRED_PID_REPAIR_V1/LATEST_REPORT.md`. `PASS_BOUNDED_CPU_RETIRED_PID_REPAIR`: 53 bounded CPU checks, **zero** simulator starts and zero optimization performance results. CPU-only guard refuses SIMULATION.
- AG4 terminal `d8d0401dab0a1d9cb949302bcc05148328421cc2`. Old AG3 GEMM BASE: 1,071,405 cycles, full strict. AG4 Gaussian BASE: 3,278,356 cycles, full strict, but AG4 failed global executor qualification. Preserve both as source-bound historical observations; neither is automatically qualified for a new cohort. AE_GEMM failed after explicit owner signal; other ON points were not started. No AE/AD speedups.
- BA existing execution branch latest read-only snapshot `7cdc27a7f4d7f13e11f942d6afdc5529121e6c3c`, `docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/`. It has three worker preparations, imported controls and `0/32` new simulations as of that published snapshot. Its global shared observer/real multi-role qualification remains incomplete. Existing provisional O = K0/OO128/Tag64x8/AE0/AD0; it does **not** prove AE/AD useless.
- User reported disk free about **12.2 G** after cleanup; this has **not** been verified in the production output mount and is not a substitute for fresh paired R2 admission. Previous recorded host IO-full avg10 exceeded 25%. No inference that IO has recovered.

## Decision: parallelize evidence preparation, not dispatch ownership

AG and BA may run separate read-only code/source/plan work in parallel with isolated branches and output. AG supplies an independent AG5-to-BA guard/ownership interface review and designs a bounded AG6 optimization screen. BA consumes the AG5 findings, owns production shared-observer qualification, all actual simulation authorization, resource/authority admission and single global dispatcher. There is **no second concurrent full-simulation dispatcher**.

AG5's changed `ownership.py` is **not** byte-identical to AG4, while the published BA vendored `ownership.py` was inherited from AG4. BA's own `guarded_process.py` already contains a separately developed retired-PID fix and has bounded AST/real-CPU receipts. Compare AG5's guard + ownership + authority as a semantic package against BA's multi-root/shared-observer callers; cherry-picking one file without interface verification is forbidden. Do not rerun all 53 AG5 tests; test only the integrated changed path and BA's unqualified shared-role scope.

AG may not run a CPU fixture in the original shared namespace while BA's authority would classify its new PID/script/lock as unregistered. Use source-only preparation until BA has registered its exact CPU role and fresh R2 CPU admission, or use a verified independent pre-existing authorized environment. No renaming/path wildcard to dodge checks. Do not disrupt EP-L2 or other projects.

## Time-efficient science ordering

1. **Now / independently:** AG prepares two frozen-BASE reuse dossiers and an AE-only / AD-only four-point AG6 proposal without new UUIDs; BA finishes its exact shared observer, SEM1 and ROB1 prepared qualification as resources permit. No extra generic security framework.
2. **Before any new full simulation:** verify actual disk mount free >= 10 GiB and BOTH host/cgroup IO-full PSI and memory/OOM thresholds with fresh >=10s paired samples. Keep 10 GiB an unchanged hard threshold; 15–20 GiB is prudent **headroom advice**, not a new science/R2 hard rule. A cleanup-induced IO spike may independently block launch.
3. **User authorization for AG6:** If user explicitly approves a new **up-to-four actual-start** AG6 screen and both old BASEs pass independent reuse gates, register fresh AE_GEMM, AE_Gaussian, AD_GEMM, AD_Gaussian (or an equally immutable scientifically justified order) with unchanged K0/Tag64x8/OO128/finite service/one optimization ON. Every failed fork counts. No late hidden sixth start. If either BASE fails identity/reuse, STOP and propose a separately authorized fully paired (up to six starts) alternative; no automatic expansion. BA is the sole dispatcher and maintains AG6's separate ledger, distinct from its 32 closure cap.
4. **Candidate decision:** A newly qualified AG6 screen may be evaluated using the already published minimum per-input speedup >=0.98, GM >=1.02 and fixed global tie policy, but cannot silently amend BA's frozen `PROVISIONAL_O_WITH_INCOMPLETE_OPT_SCREEN`. A new explicit science decision and preregistration must reconcile candidate/F selection before changing the BA P matrix. If AG6 is not authorized or incomplete, keep provisional O and the existing BA plan; do not stall all independent tests indefinitely.
5. **After fixed F decision or under the existing BA-approved provisional scope:** perform main eight-input F/C+ coverage, negative cases, service 4-to-1 sensitivity, and only source-qualified N1/N2/N3 inputs. Do not use AG discovery results to choose new sizes, hashes, per-input variants or exclusions.
6. **Writeup:** v0.18 remains an English pending-results draft. All new claims need strict source/input/runtime/denominator/scope; original 44/GM12 and independent controls remain separate. DC is user-owned.

## Disk and timing guard

12.2 G user-reported free space exceeds the strict >=10 GiB minimum nominally but leaves little margin. Confirm filesystem and sample again after additional cleanup. Do not create bulky duplicate raw, copy frozen large traces, or launch simultaneous memory/I/O-intensive tasks while near the threshold. Prefer manifest reuse and links only when they preserve identity and immutability. Historical raw, original executable mappings, other-project data and locked files are not cleanup candidates without their owners' authorization.

## Handoff and STOP rules

- AG publishes static comparison, base eligibility findings and proposed cohort/selection delta in its own new branch; **PREPARED_ONLY** until separate budget and actual launch receipts.
- BA reads exact AG5 and AG proposal commits via GitHub, not an earlier handoff screenshot, and updates its own state with exact SHA/qualification before any performance gate.
- Identity/semantic/strict failures STOP the affected registered cohort; negative speedup is measured, not suppressed. Neither lane can reset, patch-resume or reuse AG3/AG4 attempts.
- Do not infer current processes or actual resource availability from GitHub snapshots. Do not install recurring dispatchers or promise background auto-resume.
