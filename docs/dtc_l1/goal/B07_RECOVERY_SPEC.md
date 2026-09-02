# DTC-L1 B07 Recovery Specification

Status: **AUTHORIZED RECOVERY TASK**

Scope: resolve the M1 `B07` HARD failure, re-close M1, then resume the already-authorized M2 -> M4 continuous goal only if all M1 HARD gates pass.

## 1. Current failure

The current `PAPER_BASE` same-line many-warp merge-full test reaches `MSHR_MERGE_ENRTY_FAIL` and then deadlocks instead of draining. The failure was observed with a temporary validation-only MSHR `entries=1, max_merge=1` override and is recorded in `codex_handoff/LATEST_REPORT.md`.

Do not begin M2 until this is resolved and all M1 gates are revalidated.

## 2. ChatGPT source review finding

Source review identified a concrete Paper-Base PIB-lifetime defect that must be verified first.

In the current `ldst_unit::L1_latency_queue_cycle()` L1-hit completion path, the code calls:

`m_core->warp_inst_complete(mf_next->get_inst());`

when the final pending register write for the load completes, but that path does **not** call `dtc_l1_retire(...)`.

Other tracked memory-instruction completion paths already pair `warp_inst_complete(...)` with `dtc_l1_retire(...)`.

Because `PAPER_BASE` PIB admission is keyed by the dynamic instruction UID, an L1 hit that completes without `dtc_l1_retire` leaves a stale live PIB entry. The B07 same-line workload is especially sensitive: after the first miss fills, younger same-line requests become hits; if those completions do not retire their PIB entries, the default 8-entry PIB can remain permanently full and stop forward progress.

Treat this as the primary root-cause candidate and verify it with bounded instrumentation before making broader changes.

## 3. Required recovery sequence

### R07.1 Reproduce and localize before fix — HARD

Using the current failing Core SHA, reproduce B07 with bounded diagnostics sufficient to show:

- PIB admits/retires/occupancy around the failure;
- live tracked UIDs near no-progress;
- at least one same-line access transitions to L1 `HIT` after the first miss fill;
- whether that hit calls `warp_inst_complete` without removing the UID from the DTC PIB live set;
- MSHR state around the first fill and subsequent retry.

Do not add unbounded request logging.

Pass for localization: evidence must either confirm the missing-hit-retire leak or disprove it clearly.

If disproved, STOP and report rather than guessing a different fix.

### R07.2 Minimal completion-lifecycle fix — HARD

If R07.1 confirms the leak, make the smallest source fix that guarantees:

> every `ldst_unit` completion of a tracked Paper-Base memory instruction that reaches the simulator's true `warp_inst_complete` point retires its PIB lifecycle exactly once.

Expected minimal location: the L1-latency hit path immediately adjacent to the existing `warp_inst_complete(mf_next->get_inst())` event.

Requirements:

- do not change upstream cache hit/miss/MSHR semantics;
- do not change L1 latency, scheduling, coalescing, or writeback timing;
- `dtc_l1_retire` must remain idempotent for any path that can report completion more than once at the source level;
- do not release a PIB entry before the source's actual completion event;
- audit all `warp_inst_complete` call sites inside `ldst_unit` and document whether each tracked memory-instruction path is paired with DTC retirement or is intentionally outside the DTC lifecycle.

### R07.3 Add a regression invariant/test — HARD

Add a directed regression that fails if an L1-hit-completed tracked instruction leaks its PIB entry.

At minimum require at drain:

- `pib_admits == pib_retires`;
- PIB occupancy == 0;
- tracked live UID set empty;
- application self-check PASS.

Prefer a specific counter/assertion for hit-completion retire coverage if it can be added without timing impact.

### R07.4 Re-run B07 with source-supported configuration — HARD

The current cache configuration parser already carries both conventional MSHR entry count and max-merge depth. Re-run B07 without an uncommitted source-only max-merge override wherever practical.

Use a reproducible config/preset or test harness that explicitly records the effective conventional L1 MSHR `entries` and `max_merge` values.

Required B07 behavior:

- `MSHR_MERGE_ENRTY_FAIL > 0` in the controlled test;
- the blocked same-address request retries rather than being dropped;
- the first lower miss/fill completes;
- forward progress resumes after MSHR capacity becomes available;
- application self-check PASS;
- no deadlock watchdog event;
- PIB accounting closes at drain;
- conventional MSHR accounting/state drains.

Run at least one less-pathological merge limit (for example max_merge 2, 4, or the existing default) in addition to the stress `max_merge=1` case if the test harness permits, and show that the failure/recovery semantics are consistent.

### R07.5 Clean-upstream differential check — HARD

Run the frozen clean upstream Core (`91880c53383d5a6a6742bfb1be2c5f34e39c7871`) with the same conventional L1 cache/MSHR geometry and same B07 workload, without the Paper-Base PIB layer.

Purpose: establish the source's native traditional-MSHR merge-full behavior.

Record:

- completion vs deadlock;
- merge-full count;
- L1 accesses/misses/pending hits;
- lower request count when deterministically exposed.

Interpretation:

- if clean upstream makes progress and fixed `PAPER_BASE` does too, B07 can pass;
- if clean upstream itself deadlocks under exactly the same conventional MSHR settings, do not silently change baseline MSHR semantics. Report this as source behavior and STOP for specification review;
- do not weaken the gate merely to continue.

### R07.6 Full M1 revalidation — HARD

After the fix, re-run all M1 HARD validation items, not only B07:

- B01A-E;
- B02-B09;
- LEGACY neutrality exact checks;
- primary stall accounting closure;
- PIB accounting closure;
- lower-outstanding token closure;
- parser/machine-readable summary checks;
- release build / deterministic tests;
- `git diff --check`;
- clean worktrees.

Create `docs/dtc_l1/review_packs/M1_FOUNDATION/` only after all M1 HARD gates pass.

## 4. Acceptance criteria for B07 recovery

B07 recovery is PASS only when all of the following are demonstrated:

1. the pre-fix deadlock is localized to a source-backed cause;
2. the fix is minimal and does not change conventional MSHR/cache semantics;
3. the L1-hit completion path no longer leaks Paper-Base PIB state;
4. controlled merge-full is observed;
5. the blocked request eventually progresses after capacity becomes available;
6. B07 application completes and self-checks;
7. PIB and MSHR state drain cleanly;
8. clean-upstream differential evidence is recorded;
9. LEGACY neutrality still matches the frozen upstream exactly;
10. all other M1 HARD gates still pass.

## 5. Progression rule

If the full M1 revalidation passes:

- mark `M1_FOUNDATION` PASS;
- create/push its review pack;
- update `LATEST_REPORT.md`;
- resume the existing continuous `M2 -> M3 -> M4` goal automatically.

If any HARD item fails, record evidence and STOP.

Do not begin M5.