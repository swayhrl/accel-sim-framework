# CODEX NEXT STAGE — 174-new Repaired Hit-Path Model Validity V1

Date: 2026-09-19

Status: ACTIVE AFTER USER LAUNCH

Mode:
`GOAL MODE / solve-and-continue`

Node:
`174-new`

Stage:
`AWMA_REPAIRED_HIT_PATH_MODEL_VALIDITY_174NEW_V1`

Coordination:
`hrl/awma-hitpath-e1-authority-handoff-v1`

Read first:

1. `CURRENT_STATE.md`
2. `DISCUSSION_REFERENCE.md`
3. `POST_PIPELINE_REVIEW_DECISION_2026-09-19.md`
4. `NEXT_STAGE_ACCEPTANCE_CONTRACT_V1.md`
5. this Goal

## 0. Accepted scientific upstream

Correctness repair:

`hrl/awma-vm-per-access-coverage-repair-174new-v1`

`3f7bc0cd3cb3667b38fa0dd803ac034e19b493d6`

Repaired requalification:

`hrl/awma-repaired-vm-requalification-20h-174new-v1`

`a7110f789a2bc6761d8885a2ca5628b4acf50f69`

Scientific baseline decision:

`REPAIRED_VM_PER_ACCESS_BASELINE_ACCEPTED_FOR_MODEL_RELATIVE_CHARACTERIZATION`

Timing provenance:

`10/80 = GENERIC_SIMULATOR_ASSUMPTION_NOT_RTX4080_CALIBRATION`

Suggested execution branch:

`hrl/awma-repaired-hitpath-validity-174new-v1`

Create it from the repaired requalification final branch/HEAD.
Do not rewrite accepted review packs.

## 1. Goal question

Under correct per-access translation coverage:

> How much of repaired Q05 completion sensitivity is caused by the configured per-access lookup-service timing model, and what residual translation-path cost remains when L1/L2 lookup service is driven to zero?

This is a model-validity characterization.

It is NOT:
- a new TLB design;
- an RTX4080 lookup-latency calibration;
- a hardware speedup claim.

## 2. P0 — Provenance closeout, preferably with zero scientific reruns

The previous scientific data are accepted, but Git packaging omitted two expected provenance artifacts.

Close:

1. final report:
   `REPAIRED_VM_REQUALIFICATION_20H_174NEW_V1_REPORT.md`
2. repaired runtime authority:
   `REPAIRED_RUNTIME_AUTHORITY.json`

First recover from:
- the clean/closed prior worktree if still available;
- durable node164 receipts/logs;
- accepted build/source manifests.

Bind at minimum:
- repair source authority `3f7bc0cd...`;
- applied patch SHA;
- core/source tree identity;
- build/compiler identity if recoverable;
- exact simulator binary SHA256 used for accepted M1 runs if recoverable;
- accepted run receipt hashes.

Do NOT rerun science solely to recreate a missing Markdown/JSON file.

If the exact old binary authority cannot be recovered:
- materialize the exact accepted repaired source semantics from the accepted patch/authority;
- rebuild in an isolated runtime;
- record that this is a rebuilt binary, not claimed bit-identical;
- run one P34 10/80 sanity only if needed.

Required sanity if rebuild occurs:

```text
Q05 cycles = 1,619,068
translated admissions = 3,090,304
untranslated = 0
unobserved = 0
```

Any deterministic mismatch is `STOP_SCIENTIFIC`.

Produce:

`PROVENANCE_CLOSEOUT.md`

`REPAIRED_RUNTIME_AUTHORITY.json`

and update SHA256SUMS.

## 3. P1 — Freeze lookup-override semantics before runs

Audit the accepted source implementation for target lookup overrides.

Prove:

- override activates only for Q05 target;
- all P34 predecessor kernels execute repaired natural 10/80;
- L1/L2 capacity, associativity, ports, MSHR/PWQ/walkers/PWC/PTE are unchanged;
- only service latency fields vary;
- per-access repair remains active;
- target-boundary delta reporting remains valid.

Do not assume the undercoverage-era matrix is quantitatively valid.
It is only a design reference.

Produce:

`HIT_PATH_TIMING_SEMANTIC_CONTRACT.md`

## 4. P2 — Repaired P34 lookup-latency envelope

Reuse accepted:

```text
10/80 repaired P34 R0 = 1,619,068 cycles
I0 repaired P34       =   758,082 cycles
```

Run fresh repaired target-only variants:

```text
5/80
2/80
0/80
10/40
10/0
0/0
```

All predecessors:
`repaired natural 10/80`

Only Q05 target receives the specified lookup override.

Do not globally modify configuration for the prefix.

## 5. P2 invariants

For every variant require:

- target completes naturally;
- 3,090,304 downstream admissions under the same target identity, unless source-defined accounting proves a legitimate invariant-preserving difference;
- zero untranslated admissions;
- zero unobserved admissions;
- zero post-ready retranslation;
- same target instructions/CTA completion;
- same trace/context identity.

If changing lookup service alters lookup ordering/hit/miss counts, record it.
Do not repair the data to preserve the natural counts.

## 6. P2 target-scoped metrics

Use adjacent pre/post Q05 target boundary deltas.

Collect:

- Q05 cycles;
- L1 lookup launches/hits/misses;
- L2 lookup launches/hits/misses;
- requester L1 service;
- requester L2 service;
- L2 queue wait;
- MSHR allocation/merge/HWM/full;
- walk start/complete;
- PWC/PTE;
- requester total/mshr-wait;
- L2 data;
- DRAM;
- VM coverage counters.

Do not use whole-prefix cumulative 499 as the target walk count.

## 7. P3 — Derived sensitivity envelope

Create:

`REPAIRED_HIT_PATH_LATENCY_MATRIX.tsv`

and compute:

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

Report normalized values relative to TOTAL_I0_GAP.

Also report:

- monotonicity of 10 -> 5 -> 2 -> 0 L1 latency at L2=80;
- behavior of 80 -> 40 -> 0 L2 latency at L1=10;
- whether hit/miss counts change with timing;
- whether 0/0 is above or below I0.

Do not force an additive latency model.

Do not invent a categorical “hardware bottleneck” decision.

## 8. P4 — Source/model semantic audit

Explain from source:

1. when each translation lookup is launched;
2. whether L1 service can overlap across requesters;
3. what the configured L1 port accepts per cycle;
4. what causes a memory access to remain stalled while its lookup is pending;
5. how a lookup hit is returned/applied;
6. why repaired Q05 generates about 3.09M target lookup launches;
7. how target override changes timing;
8. which behavior is simulator-model semantics rather than established RTX4080 hardware behavior.

Create:

`HIT_PATH_MODEL_SEMANTICS_AUDIT.md`

This is required before proposing any mechanism.

## 9. C1 — Conditional non-Attention hit-path screen

Only after P2-P4 close.

Preferred target:

`PREFILL_GEMM_PRIMARY_OCC0`

Accepted producer authority:

`8f49ba3b9228b5f8a9163e961225ffd415107734`

No recapture.

If no consumer SIM_INPUT exists:
- perform standard consumer admission from the exact immutable accepted producer bundle;
- use accepted validator/consumer semantics;
- do not weaken unsupported-instruction behavior.

If admission qualifies, run at most:

```text
PREFILL_GEMM_REPAIRED_10_80
PREFILL_GEMM_REPAIRED_0_80
```

This asks whether the current hit-path timing sensitivity is unique to Q05 or appears in a non-Attention family.

If no same-source predecessor context exists:

`ISOLATED_SCREEN_ONLY`

Optional I0 is allowed only if:
- 0/80 retains a substantial unexplained residual;
- the pair can close without delaying required deliverables.

Do not run another family in this Goal.

## 10. Solve-and-continue

Engineering issues:
solve, document, continue.

Scientific task-local issue:
freeze that task, preserve evidence, continue independent authorized work where possible.

Whole Goal STOP for:
- repaired runtime authority mismatch;
- Q05/context identity mismatch;
- lookup override changes more than timing semantics;
- per-access invariant failure.

## 11. Forbidden

No:

- TLB capacity change;
- TLB port change;
- PTW/PWC mechanism;
- walker/MSHR capacity sweep;
- page-size/segmentation;
- prefetch/speculation;
- cache mechanism;
- hardware-calibrated latency claim.

## 12. Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/REPAIRED_HIT_PATH_MODEL_VALIDITY_174NEW_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_REPAIRED_HIT_PATH_MODEL_VALIDITY_174NEW_V1/`

At minimum:

```text
README.md
SOURCE_ANCHORS.md
PROVENANCE_CLOSEOUT.md
REPAIRED_RUNTIME_AUTHORITY.json
HIT_PATH_TIMING_SEMANTIC_CONTRACT.md
REPAIRED_HIT_PATH_LATENCY_MATRIX.tsv
HIT_PATH_MODEL_SEMANTICS_AUDIT.md
COVERAGE_INVARIANTS.tsv
TARGET_DELTA_METRICS.tsv
NON_ATTENTION_SCREEN_STATUS.md
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

Success marker:

`AWMA_REPAIRED_HIT_PATH_MODEL_VALIDITY_174NEW_V1_COMPLETE_WITH_SCOPE`

Then:
report -> review pack -> hashes -> commit -> push -> remote verify -> clean -> STOP.

Do not automatically design a mechanism.
