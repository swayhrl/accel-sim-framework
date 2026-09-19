# CODEX NEXT STAGE — 174-new Repaired Hit-Path Model Validity V3

Date: 2026-09-20

Status: ACTIVE AFTER USER LAUNCH

Mode:

`GOAL MODE / solve-and-continue`

Node:

`174-new`

Stage:

`AWMA_REPAIRED_HIT_PATH_MODEL_VALIDITY_174NEW_V3`

Coordination branch:

`hrl/awma-174-hitpath-resume-handoff-v3`

Read first:

1. `docs/vm_tlb/chatgpt_handoff/awma/REVIEW_174_V2_AUTHORITY_RECOVERY_2026-09-20.md`
2. recovered V1 review pack at:
   `hrl/awma-repaired-hitpath-validity-174new-v1-recovered @ b9bb4c6c356f2d98b9213d1d2ac3efdade057901`
3. V2 stop pack at:
   `hrl/awma-repaired-hitpath-validity-174new-v2 @ aa303057188e4bcf7cc3119798cb90aba095f0c6`
4. this Goal

Suggested execution branch:

`hrl/awma-repaired-hitpath-validity-174new-v3`

Create from:

`aa303057188e4bcf7cc3119798cb90aba095f0c6`

Do not modify V1/V2 review packs.

## 0. Authority preflight

Run `git fetch origin`.

Verify:

```text
origin/hrl/awma-repaired-hitpath-validity-174new-v1-recovered
  = b9bb4c6c356f2d98b9213d1d2ac3efdade057901

origin/hrl/awma-repaired-hitpath-validity-174new-v2
  = aa303057188e4bcf7cc3119798cb90aba095f0c6
```

Verify:

`aa303057^ = b9bb4c6c...`

and:

`b9bb4c6^ = a7110f78...`

This is now an engineering provenance check.

If these exact relationships hold, authority is closed.

Do not stop merely because the original deleted V1 branch name is still absent.

## 1. Fresh V3 time authority

At actual start record:

`V3_START_UTC`

Set:

`V3_DEADLINE_UTC = V3_START_UTC + 12 hours`

Set:

`V3_NO_NEW_TARGET_AFTER = V3_DEADLINE_UTC - 1 hour`

Do NOT inherit:

- prior 20h campaign deadline;
- V1 deadline;
- V2 time authority;
- any old no-new-target cutoff.

If an external launcher/runtime exposes a stricter deadline, record its exact source/value and use the stricter one.

Produce:

`V3_TIME_AUTHORITY.json`

## 2. P0 — Reuse V1 provenance and source audit

Reuse by exact remote commit/hash:

- `PROVENANCE_CLOSEOUT.md`
- `RECOVERED_APPLIED_REPAIRED_SOURCE.patch`
- `HIT_PATH_TIMING_SEMANTIC_CONTRACT.md`
- `HIT_PATH_MODEL_SEMANTICS_AUDIT.md`

Do not repeat this analysis.

The V1 partial P34 run remains historical:

`PARTIAL_NOT_ADMITTED`

Do not extrapolate from it.

## 3. P1 — Materialize a durable rebuilt runtime bundle

First inspect whether the exact V1 rebuilt binary still exists and is hash-bound.

If yes:
- verify it against V1 build/source authority;
- reuse it.

If no:
- rebuild once from the exact recovered source semantics;
- do not alter source;
- do not add new instrumentation except already accepted target-delta/coverage telemetry.

Freeze:

- base framework commit;
- core/source identity;
- recovered patch SHA;
- compiler/build command/environment;
- simulator binary SHA256;
- relevant shared-library SHA256;
- config SHA.

Publish a small durable runtime bundle/receipt under node164, for example:

`/root/share/mnt164/huangrulin/awma_repaired_hitpath_runtime_v3/`

The purpose is to prevent another authority loss.

Produce:

`REBUILT_RUNTIME_AUTHORITY_V3.json`

The rebuilt binary is an execution authority only after P2 passes.

## 4. P2 — Complete repaired P34 10/80 qualification

Run one fresh full P34 repaired natural 10/80.

Do not resume the V1 partial run unless there is a proven exact simulator checkpoint contract.

Required natural completion:

```text
Q05 cycles                  = 1,619,068
downstream admissions       = 3,090,304
translated admissions       = 3,090,304
untranslated admissions     = 0
unobserved admissions       = 0
post-ready retranslation    = 0
same target instruction/CTA completion
```

If exact deterministic reproduction fails:

`STOP_SCIENTIFIC_REBUILT_RUNTIME_MISMATCH`

No lookup variants may be interpreted.

If it passes:

`REBUILT_HITPATH_RUNTIME_QUALIFIED`

Freeze the exact binary SHA for all remaining runs.

## 5. P3 — Six-point repaired target-only matrix

Accepted reused anchors:

```text
P34 repaired 10/80 = 1,619,068
P34 Q05-only I0    =   758,082
```

All predecessor kernels remain repaired natural 10/80.

Only Q05 target receives the lookup-latency override.

Required points:

```text
Q1  0/80
Q2  0/0
Q3  10/0
Q4  5/80
Q5  2/80
Q6  10/40
```

Priority is intentional:
the first three close the main scientific endpoints.

## 6. Bounded CPU pipeline scheduling

After P2 qualifies the runtime, independent matrix points may run concurrently to improve wall-clock efficiency if and only if:

- each run uses a separate working/output directory;
- simulator binary/config/trace inputs are read-only;
- no shared writable simulator state exists;
- node164 destinations are distinct;
- memory/CPU preflight shows safe headroom.

Default maximum:

`MAX_PARALLEL_SIM_RUNS = 2`

Codex may use 3 only if preflight demonstrates ample RAM/CPU and no shared mutable state.

Suggested waves:

Wave A:
- 0/80
- 0/0

Wave B:
- 10/0
- 5/80

Wave C:
- 2/80
- 10/40

If parallelism would risk correctness or storage pressure, run serially.

Simulation cycle counts are scientific outputs; wall-clock throughput is not.

## 7. Per-run acceptance

Every accepted point must naturally complete.

Require:

- exact Q05 trace/context identity;
- exact repaired per-access gate;
- same binary/config except target lookup override;
- 3,090,304 target downstream admissions;
- zero untranslated;
- zero unobserved;
- zero post-ready retranslation;
- same target completion identity.

If admission count or target identity changes:
freeze that run and diagnose before interpretation.

Lookup timing may legitimately change:
- hit/miss counts;
- request ordering;
- merge behavior;
- requester timing.

Record those changes.

Do not force additive behavior.

## 8. Target-boundary metrics

For every accepted point collect target-scoped pre/post deltas:

- Q05 cycles;
- L1 lookup launches/hits/misses;
- L2 lookup launches/hits/misses;
- L1 service cycles;
- L2 service cycles;
- L2 queue wait;
- MSHR alloc/merge/HWM/full;
- walk starts/completions;
- PWC;
- PTE;
- requester total latency;
- requester MSHR wait;
- L2 data;
- DRAM;
- coverage invariants.

Never use whole-prefix cumulative values as target values.

## 9. P4 — Model-validity envelope

Produce:

`REPAIRED_HIT_PATH_LATENCY_MATRIX_V3.tsv`

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

Report normalized fractions versus TOTAL_I0_GAP.

Also report:

- 10/80 -> 5/80 -> 2/80 -> 0/80 behavior;
- 10/80 -> 10/40 -> 10/0 behavior;
- hit/miss changes;
- requester component changes;
- whether 0/0 is above/below I0.

Do not force monotonicity.

Do not convert requester cycles directly into exposed GPU stall cycles.

Do not claim RTX4080 hardware latency.

## 10. C1 — Conditional non-Attention screen

Only after all six Q05 matrix points are accepted.

Preferred:

`PREFILL_GEMM_PRIMARY_OCC0`

Producer authority:

`8f49ba3b9228b5f8a9163e961225ffd415107734`

No recapture.

If exact consumer admission closes, run at most:

- repaired 10/80
- repaired 0/80

Label:

`ISOLATED_SCREEN_ONLY`

unless a same-source predecessor context is separately proven.

If budget is insufficient:

`SKIPPED_BUDGET_AFTER_PRIMARY_MATRIX`

This is acceptable.

## 11. Solve-and-continue

Engineering issues:
solve and continue.

The deleted old V1 ref is no longer a scientific STOP because the exact commit now has a recovered remote ref.

Task-local scientific STOP:
freeze affected task only.

Whole Goal STOP for:

- recovered V1 commit/hash mismatch;
- rebuilt runtime qualification mismatch;
- Q05/context identity mismatch;
- per-access coverage invariant failure;
- lookup override changes architecture semantics beyond service timing.

## 12. Forbidden

No:

- TLB capacity/port mechanism;
- PTW/PWC mechanism;
- MSHR/walker capacity sweep;
- page-size/segmentation;
- prefetch/speculation;
- cache mechanism;
- native hardware latency claim.

## 13. Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/REPAIRED_HIT_PATH_MODEL_VALIDITY_174NEW_V3_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_REPAIRED_HIT_PATH_MODEL_VALIDITY_174NEW_V3/`

Required:

```text
README.md
SOURCE_ANCHORS.md
V3_TIME_AUTHORITY.json
REBUILT_RUNTIME_AUTHORITY_V3.json
REBUILT_RUNTIME_QUALIFICATION.md
REPAIRED_HIT_PATH_LATENCY_MATRIX_V3.tsv
TARGET_DELTA_METRICS.tsv
COVERAGE_INVARIANTS.tsv
MODEL_VALIDITY_ENVELOPE.md
NON_ATTENTION_SCREEN_STATUS.md
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

Reference V1 source/provenance files by exact recovered ref/commit/hash.

Final hour:
no new scientific target.

Then:
node164 closure -> report -> review pack -> hashes -> commit -> push -> remote verify -> clean -> STOP.

Success marker:

`AWMA_REPAIRED_HIT_PATH_MODEL_VALIDITY_174NEW_V3_COMPLETE_WITH_SCOPE`

Do not automatically enter mechanism design.
