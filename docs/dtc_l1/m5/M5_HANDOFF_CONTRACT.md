# M5 Substage Handoff Contract

Status: **ACTIVE — M5 v2 COMPUTE + GRAPHICS GOAL AUTHORIZED**

Compute authority: `M5_V1_APPROVAL.md` + `M5_EXPERIMENT_MATRIX.md`.

Post-compute graphics authority: `M5_V2_GRAPHICS_CONTINUATION_APPROVAL.md` + `M5_GRAPHICS_POST_COMPUTE_PLAN.md` + `M5_GRAPHICS_HANDOFF_CONTRACT.md`.

M5 is intentionally split into small independently reviewable substages. Those substages are handoff/quality boundaries, not ordinary human-approval stops. After a substage passes its acceptance criteria, Codex checkpoints evidence, commits/pushes, updates the mutable report, and continues automatically.

## 1. Standard compute handoff artifacts

Each compute substage creates:

`docs/dtc_l1/m5/handoffs/M5_X_<NAME>.md`

and, for major experiment waves, a review pack:

`docs/dtc_l1/review_packs/M5_X_<NAME>/`

Required handoff sections:

1. Status: PASS / RESOLVING_ISSUE / RESEARCHER_DECISION_REQUIRED.
2. Input anchors: Core SHA, Framework SHA, previous handoff SHA.
3. Formal behavior anchor.
4. Workload manifest version.
5. Config manifest/hash.
6. Parser/schema version.
7. Completed experiment IDs.
8. Acceptance checklist with evidence links.
9. Issue/resolution IDs.
10. Invalidated/obsolete result IDs.
11. Result artifacts and raw-log index.
12. Mechanism finding without numeric overclaim.
13. Next executable scope.
14. Do-not-redo list.

## 2. Review-pack minimum contents

For major compute stages (`M5_0`, `M5_2`, `M5_6`) use at least:

- README.md
- SOURCE_ANCHORS.md
- FORMAL_ANCHOR.md
- WORKLOAD_PROVENANCE.md
- CONFIG_MANIFEST.md
- CHANGED_FILES.md
- COMMIT_HISTORY.md
- VALIDATION_SUMMARY.md
- COUNTER_SANITY.md
- RESULT_MANIFEST.tsv
- RAW_LOG_INDEX.tsv
- OPEN_ISSUES.md
- generated/ compact CSV/JSON

Raw simulator logs, binaries, traces, build trees, and large datasets are not committed.

## 3. Acceptance levels

Every acceptance item is one of:

- `CORRECTNESS_HARD`
- `FIDELITY_HARD`
- `MECHANISM_EXPECTATION`
- `DIAGNOSTIC`

Exact thesis speedup values are references, not pass thresholds.

## 4. Compute-stage handoffs

### M5.0A Anchor

Must state exact parents/heads, Release build and DTC CTests, LEGACY/Base/IO/OO sentinels, toolchain/runtime hashes, safe concurrency, and resumable result registry.

PASS -> M5.0B.

### M5.0B Workloads

One row for each of ten compute algorithms:

`paper name | canonical algorithm | mapping status | source version | wrapper | PTX hash | input/dimensions | launch geometry | Base smoke | wall time`.

Explicitly resolve `gemv/gemver`, `gesu/gesummv`, `conv2d/2DConvolution`.

PASS -> M5.0C.

### M5.0C Platform

Must include actual option values/source anchors, SM count, natural downstream caps, Tag-bank/coalescer service comparison, ratio-zero conventional-L1 policy identity, and any repaired fidelity mismatch plus regressions.

PASS -> M5.0D.

### M5.0D Metrics

Freeze Figure 4.2 four structural categories, diagnostic Tag-bank/other stalls, Figure 4.7 common live-miss lifecycle, averages/peaks/denominators/sampling interval, strict parser schema, and directed counter tests.

PASS -> M5.0E.

### M5.0E Fidelity Lock

Include ATAX/SpMV/2MM/Conv2D Base/IO/OO pilots and root-cause classification for surprising results. Freeze `M5_FORMAL_BEHAVIOR_ANCHOR`.

PASS -> M5.1.

### M5.1 Figure 4.2

Ten Base formal runs, four-category percentages/raw counts, diagnostic stalls, paper references, bottleneck classification.

PASS -> M5.2.

### M5.2 Figure 4.5 + 4.7

Ten Base/IO/OO triplets, cycles/speedups, GM-CE/GM-GP, common live misses, speedup/concurrency relation, weak-result causal classification, IO-vs-OO evidence.

PASS -> M5.3.

### M5.3 Figure 4.8

Prove logical size is the intended varied knob; 16/32/64 KiB config identities; IO/OO per-workload/GM sensitivity; optional Base control.

PASS -> M5.4.

### M5.4 Figure 4.9

16.5/24/32/40/48 KiB physical runs, IO-32 KiB normalization, physical pressure/reclaim counters, exact deadlock classification. Generic timeout is never encoded as deadlock/performance zero.

PASS -> M5.5.

### M5.5 Figure 4.10

32/64/128/192 PIB runs, IO-128 normalization, PIB/HOL/concurrency counters, explicit SpMV analysis.

PASS -> M5.6.

### M5.6 Compute causal synthesis

Provide per-workload causal classification covering implementation/modeling, workload/input, downstream/platform, compute-bound, traffic side effect, and genuine mechanism limitation.

M5.6 PASS produces a frozen compute checkpoint, **not the persistent Goal terminal state**.

Required transition artifact:

`docs/dtc_l1/m5/handoffs/M5_6_TO_GRAPHICS.md`

It records immutable `COMPUTE_FREEZE_CORE_SHA` / `COMPUTE_FREEZE_FRAMEWORK_SHA`, compute review pack, reusable result identities, graphics-prep state, and exact graphics-branch creation points.

After M5.6 PASS create isolated graphics branches and continue M5.7 automatically.

## 5. Post-compute graphics handoffs

All graphics-specific details and acceptance requirements are defined in:

`docs/dtc_l1/m5/M5_GRAPHICS_HANDOFF_CONTRACT.md`

Sequence:

`M5.7 -> M5.8 -> M5.9 -> M5.10 -> M5.11 -> M5.12`

Do not rewrite frozen compute results from graphics branches.

## 6. Stage transition rules

At every PASS transition:

1. finish acceptance checks;
2. run strict parser/counter sanity;
3. commit compact evidence with explicit paths;
4. push affected branches;
5. update `codex_handoff/LATEST_REPORT.md`;
6. immediately begin the next authorized stage.

If a resolve-in-goal issue occurs, remain in the current stage, execute the problem-resolution policy, checkpoint when useful, regress/invalidate stale evidence as needed, and continue.

Only a genuine `RESEARCHER_DECISION_REQUIRED` boundary pauses the Goal.

## 7. M5 terminal review states

If source-backed graphics formal reproduction succeeds:

`M5_FULL_REPRO_READY_FOR_REVIEW`

If exhaustive post-compute graphics path recovery proves source-backed reproduction unavailable:

`M5_COMPUTE_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`

Figure 4.6 area/synthesis remains outside M5 and requires separate M6 authorization.
