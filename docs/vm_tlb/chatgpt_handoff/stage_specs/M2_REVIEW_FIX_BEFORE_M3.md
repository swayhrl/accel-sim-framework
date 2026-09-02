# M2-RF — Independent Review Fix Before M3 Continues

## Status

**AUTHORIZED NOW.**

Independent ChatGPT review of the M2 closeout found that the core functional state machine is largely correct and the prior 32–65 GiB runtime-memory blocker was properly diagnosed/fixed. However, M2 is **reopened before M3 continuation** because one remaining retry/observability issue would materially distort later timing experiments and target-paper TLB miss-rate analysis.

A first M3 G3-1 source commit (`8c613a356e6a146951cd59c9929046c6c4cfd856`) already exists on the Track-A Core branch. Do not rewrite or force-push history. Treat that commit as **provisional/unaccepted** and make no further M3 semantic changes until this M2 review fix passes. The M2 fix may be implemented on top of the current branch, after which all M2 regressions and the G3-1 contract test must be rerun.

## Why M2 is reopened

At M2 Core `e7999554200760b31b4efe16d98e050370e1ea71`, every stalled `mem_access_t` calls `translation_controller::translate()` again each cycle while `vm_translation_applied()==false`.

Inside `translate()`, the implementation consumes/probes the L1 TLB and then the shared L2 TLB **before** discovering that the same waiter UID is already registered in an active translation MSHR.

Therefore a single accepted translation miss can repeatedly:

- consume L1/L2 lookup ports while it is merely waiting for the same walk;
- increment L1/L2 access/miss counters every retry cycle;
- create artificial TLB-port contention against unrelated translation requests;
- make measured L2 TLB miss counts depend strongly on PTW latency even when the number of unique walks is unchanged.

The existing M2 integrated evidence already exposes this effect: BFS has 7 walks, but baseline reports 42 L2 misses; increasing fixed walk latency to 50 cycles still has 7 walks while L2 misses rise to 357. This is not acceptable as the basis for later Segmentation-paper L2-TLB miss-rate plots or realistic M3 PTW timing.

The M2 specification explicitly permits retry probes only if event counters are precisely defined; it does not authorize a waiting request to consume lookup bandwidth every cycle without being distinguished from a new translation lookup.

## RF1 — Pending-waiter fast path

Preserve the existing MSHR semantics, but prevent an **already registered waiter** from re-probing TLBs while its translation is still active.

Required behavior:

1. First lookup for a `mem_access_t` proceeds through finite L1/L2 resources normally.
2. On accepted L2 miss, the waiter is allocated/merged exactly once.
3. If the same `(translation key, waiter UID)` retries while that MSHR entry is still active:
   - return `TRANSLATION_PENDING` (or equivalent wait result);
   - do **not** consume an L1 port;
   - do **not** consume an L2 port;
   - do **not** add another L1/L2 access or miss event;
   - do not create another waiter registration or merge.
4. When the walk completes and the MSHR is removed/fills occur, the normal replay may perform one final L1 lookup/hit and complete the data request.
5. A **new waiter UID** for the same key must still perform its own normal lookup before merging into the existing MSHR.
6. Requests rejected because they were never accepted into translation state (for example finite-resource full/backpressure) must retain explicit retry semantics and must not be silently dropped.

A minimal controller-side pending-waiter lookup before TLB port consumption is acceptable if it satisfies the above. A larger `mem_access_t` state-machine refactor is not required unless needed for correctness.

## RF2 — Directed non-reprobe / non-starvation test

Add a deterministic test that proves:

- waiter A incurs one L1 miss + one L2 miss and enters pending state;
- replaying waiter A for several cycles before walk completion does not increase L1/L2 accesses/misses/port stalls;
- waiter A does not consume TLB ports on those pending retries;
- an independent waiter B can use the finite shared L2 port while A is pending;
- A is registered once, awakened once, and completes exactly once after fill;
- no store/atomic/data-side duplicate effect is introduced.

The test must assert exact counts, not only exit 0.

## RF3 — Statistics semantics required before paper-facing use

Keep the existing probe counters if useful, but make the following concepts explicitly separable and documented:

- new translation lookup/request;
- L1/L2 probe access/hit/miss;
- accepted L2 miss that causes MSHR allocation;
- accepted L2 miss that merges a new waiter;
- retry while already pending (must not be a TLB probe after RF1);
- MSHR-full / PWQ-full retry/backpressure;
- translation completion.

Add at least one explicit counter for pending-waiter bypass/retry so the invariant is visible in real runs.

The final M2 docs must state which counters are appropriate for future **TLB miss-rate** calculations. Do not use a counter contaminated by same-waiter polling as a paper-facing miss rate.

## RF4 — Close remaining M2 observability/spec gaps

Before re-closing M2, fill the M2 observability gaps that are cheap and important for later research:

- MSHR occupancy high-watermark and/or histogram;
- merge depth average/max or histogram;
- MSHR entry lifetime aggregate/max (histogram optional if cumbersome);
- full/backpressure event/cycle accounting where meaningfully distinguishable;
- explicit configured page-size/stat label for the 64KB M2 baseline, with the data structure ready for M3 per-page-size expansion;
- retain PWQ wait and walker service counters.

The purpose is research observability, not cosmetic counters. If a requested statistic cannot be implemented cleanly without redesigning M3, document the exact reason and provide the closest machine-checkable equivalent; do not silently omit it.

## RF5 — Kernel-boundary persistence evidence

The project contract says TLB state persists across ordinary kernels in one simulated context. M2 source lifetime appears consistent with this, but the closeout matrix lacks explicit machine-checkable evidence.

Add one of the following, in preference order:

1. a small integrated two-kernel replay demonstrating a translation warmed before an ordinary kernel boundary remains available after the boundary; or
2. a focused simulator/controller test plus source-level proof that ordinary kernel init/done paths do not reset the translation controller.

Do not add a new flush API merely to satisfy the test.

## RF6 — M2 review-pack completeness

The M2 pack currently contains useful mechanism evidence, but it does not satisfy the project-wide review-pack minimum file set in `AGENTS.md`.

Add/update at least:

- `SOURCE_ANCHORS.md`
- `COMMIT_HISTORY.md`
- `CHANGED_FILES.md`
- `VALIDATION_SUMMARY.md`
- `OPEN_ISSUES.md`

Keep the existing `README.md`, directed matrix, invariant report, integrated validation, and raw-log index.

`OPEN_ISSUES.md` must explicitly record:

- M2 TLB hit latency is a functional `MODELING_DECISION` (currently zero hit latency with finite ports), not target-paper exact timing;
- nonzero/configurable TLB lookup latency belongs to the timing-realistic M3 path and must be included in M3 timing decomposition;
- M2 has resident memory only and no real PTE traffic/PWC/2MB behavior yet.

## RF7 — Regression and integrated acceptance

After the fix, rerun from a cold build:

- M1 directed + disabled/ideal transparency;
- all original G2-1/G2-2/G2-3/G2-4 directed tests;
- new pending-waiter non-reprobe test;
- kernel-persistence evidence;
- one-kernel functional replay;
- full LUD and BFS functional replays;
- MSHR/PWQ/walker quiescence/conservation;
- `git diff --check` and clean-worktree/provenance checks.

### Required latency-sensitivity sanity

Repeat the existing BFS fixed-walk-latency comparison (or an equivalent controlled replay) with at least baseline latency and a much larger latency.

Acceptance requires:

- same-waiter polling no longer makes L2 TLB miss/probe counts grow roughly in proportion to walk latency;
- any remaining difference in L2 lookup/miss counts must be attributable to genuinely different first-time translation requests, resource-full retries, or timing-induced instruction overlap and must be quantified;
- pending-waiter bypass counter becomes nonzero when expected;
- no new deadlock/request loss/starvation.

## RF8 — Interaction with existing provisional G3-1 commit

Core commit `8c613a356e6a146951cd59c9929046c6c4cfd856` added a replaceable PTE backend contract after the user reported M2 closeout, before independent review completed.

Do not discard it by force rewrite. Instead:

- pause all further M3 work;
- implement this M2 review fix on the current branch;
- rerun all M2 tests against the resulting head;
- rerun the G3-1 PTE backend/no-recursion unit tests to ensure the provisional commit remains compatible;
- mark G3-1 as accepted only after M2 is reclosed.

If the M2 fix and provisional G3-1 code conflict semantically, STOP and report rather than silently redesigning either stage.

## Acceptance criteria

M2-RF PASS requires all of the following:

1. registered pending waiters do not re-probe/consume L1/L2 ports each wait cycle;
2. exact directed non-reprobe/non-starvation test passes;
3. no duplicate waiter/merge/data-side effect;
4. paper-facing TLB miss-rate counter semantics are explicitly clean/separable;
5. required MSHR observability is added or any narrow exception is justified;
6. kernel-boundary persistence evidence exists;
7. M1 transparency and all M2 regressions pass after cold build;
8. functional LUD/BFS replays complete and quiesce;
9. fixed-walk-latency sensitivity no longer shows retry-pollution-driven L2 miss explosion;
10. M2 review pack meets `AGENTS.md` minimum completeness;
11. provisional G3-1 tests still pass;
12. source/provenance/worktrees are clean and pushed.

## STOP boundary

After M2-RF closeout:

- update `codex_handoff/m1_m3/LATEST_REPORT.md` and `TARGET_PROGRESS.md`;
- update/reclose the M2 review pack;
- push Core + Framework;
- **STOP FOR CHATGPT REVIEW BEFORE G3-2 OR ANY FURTHER M3 SEMANTIC WORK**.

Do not continue to PTE L2/DRAM integration until this independent M2 review fix is accepted.
