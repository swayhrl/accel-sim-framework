# CODEX NEXT STAGE — 174-new Repaired Hit-Path Model Validity Resume V2

Date: 2026-09-20

Status: ACTIVE AFTER USER LAUNCH

Mode:
`GOAL MODE / solve-and-continue`

Node:
`174-new`

Stage:
`AWMA_REPAIRED_HIT_PATH_MODEL_VALIDITY_174NEW_V2`

Coordination branch:
`hrl/awma-174-hitpath-resume-handoff-v2`

Read first:

1. `docs/vm_tlb/chatgpt_handoff/awma/REVIEW_174_HITPATH_V1_DEADLINE_2026-09-20.md`
2. `docs/vm_tlb/chatgpt_handoff/awma/POST_PIPELINE_REVIEW_DECISION_2026-09-19.md`
3. `docs/vm_tlb/chatgpt_handoff/awma/NEXT_STAGE_ACCEPTANCE_CONTRACT_V1.md`
4. prior V1 Goal:
   `docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE_174NEW_REPAIRED_HIT_PATH_MODEL_VALIDITY_V1.md`
5. this Goal

## 0. Verify V1 authority first

Expected user-reported V1 branch:

`hrl/awma-repaired-hitpath-validity-174new-v1`

Expected user-reported final commit:

`b9bb4c6c356f2d98b9213d1d2ac3efdade057901`

Before doing any scientific work:

- `git fetch origin`;
- verify the branch exists;
- verify remote branch HEAD equals the expected commit;
- inspect V1 report/review pack;
- record the exact V1 final authority in the V2 review pack.

If the exact commit differs, do not guess. Use the actual remote branch HEAD only after proving it contains the reported V1 closeout and record the discrepancy.

Suggested new execution branch:

`hrl/awma-repaired-hitpath-validity-174new-v2`

Create from the verified V1 final commit.

Do not modify the V1 review pack.

## 1. Fresh stage timing — DO NOT INHERIT OLD DEADLINES

At actual V2 Goal start record:

`V2_START_UTC`

Set:

`V2_DEADLINE_UTC = V2_START_UTC + 12 hours`

Set:

`V2_NO_NEW_TARGET_AFTER = V2_DEADLINE_UTC - 1 hour`

This V2 clock is authoritative for this Goal unless the execution environment/launcher exposes a stricter real deadline.

Explicitly ignore stale deadlines from:
- the previous 20h repaired-requalification campaign;
- V1/V0 `PIPELINE_STATE.json`;
- any earlier no-new-target cutoff.

If a stricter external deadline exists:
- record its value and source in `V2_TIME_AUTHORITY.json`;
- use the stricter deadline;
- do not silently inherit an old review-pack timestamp.

## 2. P0 — Reuse V1 provenance/source work

From verified V1, inspect and reuse:

- `PROVENANCE_CLOSEOUT.md`;
- `REPAIRED_RUNTIME_AUTHORITY.json`;
- `HIT_PATH_TIMING_SEMANTIC_CONTRACT.md`;
- `HIT_PATH_MODEL_SEMANTICS_AUDIT.md`;
- rebuilt binary/source hashes;
- node164 partial 10/80 receipt.

If these artifacts are complete and internally consistent:
do not repeat P0 source/provenance analysis.

Copy only the minimum references/hashes into V2 `SOURCE_ANCHORS.md`.

If a supposedly completed V1 artifact is actually missing:
repair the provenance artifact from existing authority.
Do not rerun science solely to regenerate Markdown/JSON.

## 3. P1 — Qualify the exact rebuilt runtime

The V1 partial P34 10/80 run is NOT admitted and is not resumed unless the simulator has a proven exact checkpoint/resume mechanism for this run identity.

Default:
launch one fresh full P34 repaired natural 10/80 using the exact V1 rebuilt binary.

Do NOT rebuild again if the V1 binary SHA is valid.

Qualification must naturally complete and match:

```text
Q05 cycles                   = 1,619,068
downstream admissions        = 3,090,304
translated admissions        = 3,090,304
untranslated admissions      = 0
unobserved admissions        = 0
post-ready retranslation     = 0
```

Also verify same target instruction/CTA completion.

If exact deterministic reproduction fails:

`STOP_SCIENTIFIC_REBUILT_RUNTIME_MISMATCH`

Do not run latency variants.

If it passes, freeze:

`REBUILT_HITPATH_RUNTIME_QUALIFIED`

and use that exact binary for all V2 points.

## 4. P2 — Repaired P34 target-only lookup-latency matrix

Reuse scientific anchors:

```text
10/80 = 1,619,068 cycles
I0    =   758,082 cycles
```

Run on the exact qualified rebuilt binary, all predecessors repaired natural 10/80.

Only Q05 target receives lookup override.

Required matrix points, in this execution priority:

### Q1
`0/80`

Highest priority after runtime qualification.

### Q2
`0/0`

### Q3
`10/0`

### Q4
`5/80`

### Q5
`2/80`

### Q6
`10/40`

The scientific matrix still contains all six points.
The ordering is only for graceful degradation if an external deadline intervenes.

## 5. Per-run invariants

Every accepted target must naturally complete.

Require:

- exact Q05 trace/context identity;
- same repaired per-access gate;
- zero untranslated;
- zero unobserved;
- zero post-ready retranslation;
- same target instruction/CTA completion.

The 3,090,304 admission invariant should remain exact under the same target scope.
If it changes, STOP and diagnose before interpreting cycles.

Changing lookup timing may legitimately alter:
- L1/L2 hit/miss counts;
- retry/order behavior;
- requester timing.

Record those changes; do not force them back to the 10/80 counts.

## 6. Target-scoped telemetry

For every accepted matrix point collect adjacent Q05 pre/post deltas:

- cycles;
- L1 launches/hits/misses;
- L2 launches/hits/misses;
- L1 service;
- L2 service;
- L2 queue wait;
- MSHR alloc/merge/HWM/full;
- walk starts/completions;
- PWC;
- PTE;
- requester total/mshr wait;
- L2 data;
- DRAM;
- VM coverage.

Do not use whole-prefix cumulative values as target values.

## 7. P3 — Model-validity envelope

Produce:

`REPAIRED_HIT_PATH_LATENCY_MATRIX_V2.tsv`

Compute:

```text
TOTAL_I0_GAP
 = cycles(10/80) - cycles(I0)

L1_ENVELOPE
 = cycles(10/80) - cycles(0/80)

L2_NATURAL_L1_EFFECT
 = cycles(10/80) - cycles(10/0)

ZERO_LOOKUP_RESIDUAL
 = cycles(0/0) - cycles(I0)
```

Normalize each relevant quantity by `TOTAL_I0_GAP`.

Also report:

- 10/80 -> 5/80 -> 2/80 -> 0/80 behavior;
- 10/80 -> 10/40 -> 10/0 behavior;
- hit/miss-count changes;
- requester-component changes;
- whether 0/0 is above or below I0.

Do not force monotonicity.
Do not interpret the envelope as RTX4080 calibrated performance.

## 8. C1 — Optional non-Attention screen

Only after all six Q05 matrix points are accepted.

Preferred:

`PREFILL_GEMM_PRIMARY_OCC0`

Producer authority:

`8f49ba3b9228b5f8a9163e961225ffd415107734`

No recapture.

If exact consumer admission is already qualified or can be qualified without scientific approximation, run at most:

- repaired 10/80;
- repaired 0/80.

No second family.

If the Q05 matrix consumes the available V2 budget, mark:

`SKIPPED_BUDGET_AFTER_PRIMARY_MATRIX`

That is acceptable.

## 9. Solve-and-continue

Routine engineering:
solve and continue.

Task-local scientific STOP:
freeze affected work and preserve evidence.

Whole Goal STOP for:
- V1 authority mismatch;
- rebuilt runtime mismatch;
- Q05/context identity mismatch;
- per-access invariant failure;
- lookup override changes capacity/ports/architecture semantics.

## 10. Forbidden

No:

- TLB capacity/port change;
- PTW/PWC mechanism;
- MSHR/walker sweep;
- page-size/segmentation;
- prefetch/speculation;
- cache mechanism;
- native hardware latency claim.

## 11. Durable output

Large logs:

`/root/share/mnt164/huangrulin/awma_repaired_hitpath_validity_174new_v2/`

Report:

`docs/vm_tlb/codex_handoff/awma/REPAIRED_HIT_PATH_MODEL_VALIDITY_174NEW_V2_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_REPAIRED_HIT_PATH_MODEL_VALIDITY_174NEW_V2/`

Required:

```text
README.md
SOURCE_ANCHORS.md
V2_TIME_AUTHORITY.json
REBUILT_RUNTIME_QUALIFICATION.md
REBUILT_RUNTIME_AUTHORITY.json
REPAIRED_HIT_PATH_LATENCY_MATRIX_V2.tsv
TARGET_DELTA_METRICS.tsv
COVERAGE_INVARIANTS.tsv
NON_ATTENTION_SCREEN_STATUS.md
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

Reference V1 source-audit/provenance artifacts by exact commit/hash rather than duplicating them unnecessarily.

Success marker:

`AWMA_REPAIRED_HIT_PATH_MODEL_VALIDITY_174NEW_V2_COMPLETE_WITH_SCOPE`

Final one-hour reserve:
no new scientific target.

Then:
node164 closure -> report -> pack -> hashes -> commit -> push -> remote verify -> clean -> STOP.

Do not automatically enter mechanism design.
