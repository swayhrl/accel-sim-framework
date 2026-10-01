# Codex Goal — Lane F / node109
## AWMA R20R4 CPU-only hybrid active-world headroom audit V1

Date: 2026-10-02

Repository:
`swayhrl/accel-sim-framework`

Execution branch:
`hrl/awma-r20r4-hybrid-headroom-audit-109-v1`

Scientific parent:
`3f4e3409ad629d5302a54e9c3a0f356bdc190456`

Stage:
`AWMA_R20R4_HYBRID_HEADROOM_AUDIT_109_V1`

This Goal is CPU-only.

Do not acquire the GPU campaign lock for execution.
Do not run CUDA.
Do not run NSYS/NCU/NVBit/SASS/Accel-Sim.
Do not modify the accepted solver or candidate.

Purpose:
determine whether the only structurally justified follow-up — keeping baseline execution while active_count>304 and considering active-worklist execution only when active_count<=304 — has enough **ideal** complete-solver headroom to justify a new experiment.

---

# 0. Frozen authority

Use exactly the accepted R20R3P1/R20R3P2 artifacts.

Parent source/candidate:
- selected stage: `_update_gradient_incremental`
- fixed worker count: 304
- parent candidate source SHA:
  `868cf9b0420d61656b3698ba7ddc93b6aa3d6a031d825c939a9868adf916a8e3`

Discovery entries:
128,136,144,152.

Use existing:
- R20R3P1 repaired B0 NSYS report / SQLite / per-kernel manifest on node164
- R20R3P1 `SELECTED_STAGE.md`
- R20R3P2 `ACTIVE_WORK_COUNTS.tsv`
- R20R3P2 `DISCOVERY_TIMING.tsv`
- exact source patch from R20R3P1

Do not generate new timing data.

---

# 1. Reconstruct selected-stage time per outer iteration

From the accepted B0 NSYS raw / SQLite / per-kernel manifest:

For each discovery entry and each outer solver iteration:
- assign only the already-selected `_update_gradient_incremental` kernels using the same verified graph-node sequence logic used in R20R3P1;
- compute GPU kernel time for:
  - H incremental update
  - blocked Cholesky/factor/search
  - other kernels inside the selected stage
  - selected-stage total
- bind the corresponding active-world count from accepted R20R3P2 post-run niter analysis.

Do not reclassify stage membership.
Do not add line-search or constraint time.

Write:
`PER_ITERATION_STAGE_TIME.tsv`

Columns at minimum:
step, outer_iter, active_worlds, active_fraction, H_us, cholesky_us, other_stage_us, stage_total_us.

Verify per-entry and four-entry sums close to accepted selected-stage totals within parsing/rounding tolerance.

If they do not:
`R20R4_PROFILE_DECOMPOSITION_NOT_QUALIFIED`
STOP.

---

# 2. Structural diagnosis of the 304-worker candidate

From the accepted candidate source only, document:

- active-ID build is a single GPU thread scanning 1024 ctx.done flags;
- H and blocked-Cholesky worker kernels launch 304 worker coordinates;
- each worker loops:
  `for active_slot in range(worker, active_count, 304)`;
- therefore for active_count>304 some workers process multiple worlds serially;
- when active_count<=304 each active world can map to at most one worker slot without this cross-world worker-loop serialization.

Do not claim this is the measured cause of all 66.6% slowdown, because S1 was not profiled.

Classify it as:
`STRUCTURAL_EARLY_PHASE_SERIALIZATION_PRESENT`.

---

# 3. Perfect late-phase oracle

Define the only allowed structural switch point:

`active_count <= worker_count = 304`

No fitted threshold.

For every entry/iteration, classify:
- EARLY_BASELINE_REGION: active_count > 304
- LATE_ELIGIBLE_REGION: active_count <= 304

Compute three ideal oracles from B0 only.

## Oracle O1 — impossible perfect elimination of selected-stage late-region time

Assume all selected-stage GPU kernel time in LATE_ELIGIBLE_REGION becomes zero, with no overhead.

This is intentionally optimistic.

For each entry and the four-entry aggregate:
- eligible stage time
- total B0 complete-solver time
- ideal complete-solver time = B0 - eligible_stage_time
- ideal relative improvement

Use accepted B0 complete-solver medians from R20R3P2.
Because NSYS and formal timing are separate runs, report this as a cross-run bounded estimate, not exact paired timing.

## Oracle O2 — perfect elimination of only H + blocked-Cholesky late-region time

Leave other selected-stage kernels untouched.

This is closer to the actual candidate scope.

Compute same metrics.

## Oracle O3 — zero-cost active-list but preserve one-world original arithmetic cost

If raw decomposition supports it without inventing a model, estimate only the cost attributable to completed-world launches/returns in the two candidate-targeted kernels.

If it cannot be source-identifiably separated from active-world work, mark UNKNOWN.
Do not invent utilization assumptions.

---

# 4. Investment rule

The follow-up hybrid is worth a new GPU experiment only if:

1. O2 aggregate ideal complete-solver improvement >= 5%, AND
2. at least 3 of 4 discovery entries individually have O2 ideal improvement > 0, AND
3. the eligible late-region time is not dominated by a single anomalous entry, AND
4. the source admits a bounded online switch using existing device state without future information.

If O2 <5%:
`R20_ACTIVE_WORLD_LINE_CLOSED_AFTER_BOUNDED_SOFTWARE_NEGATIVE`

Interpretation:
natural shrinkage exists, but after removing the fixed candidate's obvious early-phase serialization, the remaining late-phase targeted work does not have enough ideal complete-solver weight to justify another mechanism experiment under the project's investment threshold.

If O2 >=5%:
`R20R4_HYBRID_CANDIDATE_JUSTIFIED_FOR_REVIEW`

This does not execute it.

---

# 5. If O2 >=5%, freeze one candidate design only

CPU-only design, no implementation/run.

The only admissible next candidate is a **structurally gated hybrid**:

- baseline selected-stage path when current active count >304;
- active-ID/worklist selected-stage path only when current active count <=304;
- switch condition uses current online solver state only;
- threshold exactly 304 because it is the frozen worker count, not a tuned performance parameter;
- no worker-count sweep;
- no second stage;
- no use of future niter;
- preserve original world math.

Investigate whether existing device `nsolving` can provide active count without the single-thread 1024-flag scan for the early region.

Prefer:
- avoid building active IDs at all in EARLY_BASELINE_REGION;
- build IDs only in LATE_ELIGIBLE_REGION;
- device-side conditional path, no host read inside solver.

If Warp/CUDA graph support cannot express this boundedly without changing solver lifecycle, record:
`R20R4_HYBRID_IMPLEMENTATION_NOT_CLEAN`.

Write:
`HYBRID_CANDIDATE_DESIGN.md`

Do not run it in this Goal.

---

# 6. Anti-fishing boundary

Forbidden:
- worker sweep
- threshold sweep
- choosing threshold from timing
- second selected stage
- alternate queue algorithms
- re-profile S1
- modifying solver tolerance/iterations
- new scene/batch
- holdout
- hardware mechanism

This audit answers only whether one source-derived hybrid deserves a future experiment.

---

# 7. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_R20R4_HYBRID_HEADROOM_AUDIT_109_V1/`

At minimum:
- README.md
- FINAL_DECISION.md
- PARENT_AUTHORITY.json
- PROFILE_DECOMPOSITION_RECEIPT.json
- PER_ITERATION_STAGE_TIME.tsv
- STRUCTURAL_CANDIDATE_AUDIT.md
- LATE_PHASE_ORACLE.tsv
- ORACLE_DECISION.md
- HYBRID_CANDIDATE_DESIGN.md if justified
- RAW_DATA_INDEX.tsv
- SHA256SUMS

---

# 8. Closure

CPU-only commit/push/fetch-back verify SHA/tree.
No GPU process should exist from this Goal.
Worktree clean.
STOP.

Final Chinese report:
- how much selected-stage time is actually in active_count<=304 iterations;
- O1/O2 ideal complete-solver headroom;
- whether R20 closes or one structurally gated hybrid is justified;
- no performance claim beyond accepted R20R3P2 measurements.
