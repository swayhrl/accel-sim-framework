# M5 Substage Handoff Contract

Status: **ACTIVE — M5 v1 GOAL AUTHORIZED**

Authority: `M5_V1_APPROVAL.md` + `M5_EXPERIMENT_MATRIX.md`.

M5 is intentionally split into small independently reviewable substages, but those substages are **handoff boundaries, not human-approval stop boundaries**. After a substage passes its acceptance criteria, Codex must checkpoint evidence, commit/push, update the mutable report, and continue automatically.

---

## 1. Standard handoff artifacts

Each substage `M5_X` creates:

`docs/dtc_l1/m5/handoffs/M5_X_<NAME>.md`

and, for major experiment waves, a review pack:

`docs/dtc_l1/review_packs/M5_X_<NAME>/`

The handoff is a compact executable state transition, not a prose diary.

Required sections:

1. **Status**: PASS / RESOLVING_ISSUE / RESEARCHER_DECISION_REQUIRED.
2. **Input anchors**: Core SHA, Framework SHA, previous handoff SHA.
3. **Formal behavior anchor**: the Core behavior/timing SHA used by the runs.
4. **Workload manifest version**.
5. **Config manifest/hash**.
6. **Parser/schema version**.
7. **Completed experiment IDs**.
8. **Acceptance checklist** with evidence links.
9. **Issues encountered and resolution IDs** from `implementation/M5_ISSUE_LOG.md`.
10. **Invalidated/obsolete result IDs**, if any.
11. **Result artifacts**: CSV/JSON names, raw-log-index location.
12. **Mechanism finding**: one concise paragraph describing what the stage established, without overclaiming numerical thesis reproduction.
13. **Next executable scope**: exact next experiment IDs and permitted changes.
14. **Do-not-redo list**: valid evidence the next stage should reuse.

---

## 2. Review-pack minimum contents

For major stages (`M5_0`, `M5_2`, `M5_6`, and final compute closeout), use at least:

- `README.md`;
- `SOURCE_ANCHORS.md`;
- `FORMAL_ANCHOR.md`;
- `WORKLOAD_PROVENANCE.md`;
- `CONFIG_MANIFEST.md`;
- `CHANGED_FILES.md`;
- `COMMIT_HISTORY.md`;
- `VALIDATION_SUMMARY.md`;
- `COUNTER_SANITY.md`;
- `RESULT_MANIFEST.tsv`;
- `RAW_LOG_INDEX.tsv`;
- `OPEN_ISSUES.md`;
- `generated/` compact CSV/JSON.

Raw simulator logs, binaries, traces, build trees, and large datasets are not committed.

---

## 3. Acceptance levels

Every acceptance item is labeled one of:

- `CORRECTNESS_HARD`: output/accounting/source identity must pass before data interpretation;
- `FIDELITY_HARD`: experiment must match the frozen mechanism/workload/config/metric contract;
- `MECHANISM_EXPECTATION`: trend to investigate, **not** a numeric pass/fail target;
- `DIAGNOSTIC`: useful evidence that cannot block a source-correct result.

Example:

- `create==complete`, output correct, dynamic counts equal -> CORRECTNESS_HARD.
- logical-cache sweep changes only logical size -> FIDELITY_HARD.
- IO should generally become more physical-capacity-sensitive than OO -> MECHANISM_EXPECTATION.
- thesis exact +22% speedup -> DIAGNOSTIC reference, not acceptance threshold.

This prevents Goal mode from either overfitting thesis numbers or ignoring real correctness/fidelity failures.

---

## 4. Stage-specific handoffs

### M5.0A Anchor handoff

Must state:

- exact M1-M4 parents;
- M5 branch heads;
- release build/test status;
- M4 sentinel differentials;
- runtime-library/toolchain hashes;
- safe simulation concurrency;
- formal result cache/resume mechanism.

Pass -> continue M5.0B.

### M5.0B Workload handoff

Must contain one row for each of the 10 compute algorithms:

`paper name | canonical algorithm | mapping status | source version | build wrapper | PTX hash | input/dimensions | launch geometry | Base smoke | wall time`.

Explicitly resolve `gemv/gemver`, `gesu/gesummv`, `conv2d/2DConvolution`.

Pass -> continue M5.0C.

### M5.0C Platform handoff

Must include:

- actual option values;
- source anchors for each architecture-sensitive knob;
- actual SM count;
- natural downstream caps;
- Tag-bank/coalescer service comparison across Base/IO/OO;
- any repaired fidelity mismatch plus regressions.

Pass -> continue M5.0D.

### M5.0D Metrics handoff

Must freeze formulas and counter names for:

- Figure 4.2 four structural categories;
- diagnostic Tag-bank/other stalls;
- Figure 4.7 common live-miss lifecycle;
- averages, peaks, denominators, sampling interval;
- strict parser schema.

Directed counter tests must be included.

Pass -> continue M5.0E.

### M5.0E Fidelity-lock handoff

Must include ATAX/SpMV/2MM/Conv2D pilot triplets and for every surprising result a completed issue/root-cause classification.

This handoff defines the first `M5_FORMAL_BEHAVIOR_ANCHOR`. Once emitted, formal paper-figure runs may start.

Pass -> continue M5.1.

### M5.1 Figure-4.2 handoff

Must include:

- 10 Base formal runs;
- four-category percentages and raw counts;
- full diagnostic stall table;
- paper reference averages separately;
- workload-by-workload bottleneck classification.

Pass -> continue M5.2.

### M5.2 Main-result handoff

Must include:

- 10 Base/IO/OO triplets;
- per-workload cycles/speedups;
- GM-CE and GM-GP;
- average concurrent misses Base/IO/OO;
- speedup/concurrency relationship;
- per-workload root-cause classification for weak/negative results;
- IO-vs-OO HOL/OOO evidence.

Pass -> continue M5.3.

### M5.3 Logical-sweep handoff

Must prove logical size is the only changed mechanism knob, list 16/32/64KB exact config hashes, report IO/OO per-workload/GM sensitivity, and optional conventional Base control.

Pass -> continue M5.4.

### M5.4 Physical-sweep handoff

Must list 16.5/24/32/40/48KB runs, normalized IO-32KB basis, physical pressure/reclaim counters, and exact deadlock classifications. Never encode generic timeout as deadlock or performance zero.

Pass -> continue M5.5.

### M5.5 PIB-sweep handoff

Must list 32/64/128/192 runs, normalized IO-128 basis, PIB/HOL/concurrency counters, and explicit SpMV behavior analysis.

Pass -> continue M5.6.

### M5.6 Causal-synthesis handoff

Must provide a per-workload causal classification with evidence from all prior runs and explicitly distinguish:

- implementation/modeling;
- workload/input;
- downstream/platform;
- compute-bound;
- traffic side effect;
- genuine mechanism limitation.

This stage may use prior data without rerunning simulations.

Pass -> terminal compute state `M5_COMPUTE_READY_FOR_REVIEW`.

---

## 5. Stage transition rules

At every PASS transition Codex must:

1. finish acceptance checks;
2. run strict parsers/counter sanity;
3. commit compact evidence with explicit paths;
4. push both affected repositories;
5. update `codex_handoff/LATEST_REPORT.md`;
6. immediately begin the next authorized stage.

Do not ask for confirmation between M5 substages.

If a resolve-in-goal issue occurs, remain in the current stage, execute `M5_PROBLEM_RESOLUTION_POLICY.md`, checkpoint when useful, and continue after regression.

Only `RESEARCHER_DECISION_REQUIRED` pauses the Goal.

---

## 6. Final compute handoff

The compute portion of M5 ends at:

`M5_COMPUTE_READY_FOR_REVIEW`

Required final evidence:

- all ten compute workloads resolved;
- Figure 4.2 compute reproduction;
- Figure 4.5 compute main result;
- Figure 4.7 common concurrent-miss result;
- Figure 4.8 logical sensitivity;
- Figure 4.9 physical sensitivity;
- Figure 4.10 PIB sensitivity;
- integrated causal synthesis;
- graphics-preparation status;
- no unclassified correctness/fidelity issue;
- both M5 branches pushed/clean.

This is a review boundary before optional graphics execution and M5.7+ supplemental studies.
