# CODEX NEXT STAGE — Translation Frontend READY-Application Recalibration V2

Date: 2026-09-22

Mode:

`GOAL MODE / solve-and-continue / MODEL-SEMANTIC DIAGNOSTIC`

Node:

`174-new`

Stage:

`AWMA_TRANSLATION_FRONTEND_READY_APPLICATION_RECALIBRATION_V2`

Coordination branch:

`hrl/awma-mainline-reset-crossview-v2`

Read first:

1. `EXECUTION_PRIORITY_POLICY_V5.md`
2. `REVIEW_174_TRANSLATION_FRONTEND_PIPELINING_V1_2026-09-22.md`
3. V1 execution branch `hrl/awma-174-translation-frontend-pipelining-v1 @ ad6f38878bc1e7c268b17e65fdb3793a3899a84d`
4. accepted V3R1 `7a4f2a419fe77c017cb9a9a5555b1551a2fc884c`
5. this Goal

Suggested execution branch:

`hrl/awma-174-translation-frontend-ready-application-v2`

## 0. Frozen boundaries

Do not redo:

- canonical T0 recovery;
- repaired per-access coverage qualification;
- V2/V3/V3R1;
- hit-path attribution;
- V1 READY-ownership root cause;
- V1 six-point matrix.

V1 accepted-with-scope classification:

`SERIAL_ACCESSQ_FRONTEND_AMPLIFICATION_PARTIAL`

V1 remains diagnostic, not baseline.

No TLB/PTW/cache architecture mechanism is authorized.

## 1. Scientific question

V1 pipelines translation lookup launch, but a non-head access whose controller lookup is already `LOOKUP_READY` remains `vm_translation_applied=false` until it becomes the accessq head.

Therefore the repaired downstream guard can still serialize READY application / pre-admission progress one access at a time.

Test:

> Is the remaining V1 sensitivity, especially T2's 35.7182%, materially caused by serial READY completion application at the accessq head?

This is a simulator-semantic recalibration question, not a new architecture mechanism.

## 2. Single-axis V2 candidate

Keep V1 lookup-launch overlap.

Add an opt-in V2 mode in which the prelaunch scan may consume a `READY` result for the exact resident `mem_access_t` and apply that translation result to that exact queue member before it reaches `accessq_back()`.

Mandatory semantics:

1. no access may enter L1D/ICNT before its own translation is applied;
2. use the existing `translation_controller` lookup identity `(sid, waiter_uid, key)`;
3. use existing lookup launch-port and latency semantics;
4. when prelaunch receives `READY`, apply returned PA and translation outcome to the exact matching `mem_access_t`;
5. perform the same object/telemetry classification as the existing head completion path;
6. consume each controller READY exactly once;
7. once a non-head entry has `vm_translation_applied=true`, the later head path must not translate it again;
8. downstream accessq order remains unchanged;
9. L1D/ICNT/cache arbitration remains unchanged;
10. MSHR/PWQ/walker/PWC/PTE semantics remain unchanged;
11. store/atomic/data side effects remain downstream-only and exactly once;
12. Segment F0 remains dormant;
13. legacy mode and V1 mode remain separately reproducible.

Do not introduce a new completion-bandwidth parameter in V2. The diagnostic should use the controller's existing completion behavior; this stage asks whether head-only application is the residual serialization source.

Prefer refactoring one shared "apply translation result to mem_access_t" helper over duplicating completion semantics in multiple call sites.

## 3. Minimal diagnostics

Add only the counters needed to distinguish V1 from V2.

At minimum record for the target kernel:

- prelaunch READY observations;
- prelaunch READY applications;
- head-path READY applications;
- duplicate completion/application attempts;
- ready-but-unapplied resident access count or an equivalent bounded measure;
- cycles in which accessq progress is blocked only because the next resident entry is READY in the controller but not yet applied, if cheaply observable.

Do not build a large new telemetry subsystem.

Instrumentation must be optional and timing-neutral when disabled.

## 4. Directed gates

Before full targets, prove:

### D1 — four warm L1 hits

For four resident accesses, L1 latency=10, one launch port:

- launch overlap follows existing port semantics;
- matching entries become translation-applied when their own READY result is available;
- no entry receives another entry's PA/source;
- downstream order is unchanged.

### D2 — multi-bank downstream path

When multiple resident accesses are already translation-applied, the existing L1D path may consume its normal bank-limited amount.

V2 must not add a new artificial one-access-per-cycle guard.

### D3 — zero-latency

No duplicate READY consumption, no duplicate logical UID, no same-cycle recursive ownership bug.

### D4 — miss/MSHR/PWQ/PTW

Merged/walking requesters conserve existing semantics and each exact requester is applied once after completion.

### D5 — store/atomic

Translation may complete early; data side effects remain exactly once and only on normal downstream admission.

### D6 — terminal quiescence

No stranded `m_lookups`, active MSHR, or READY completion remains after target completion.

## 5. Regression gates

Before scientific matrix:

- legacy canonical T0 exact reproduction remains accepted;
- V1 T0 10/80 and 0/80 reproduce the published V1 values within exact deterministic expectation if rerun is required by the build/source relation;
- candidate-private source/binary/toolchain authority is hash-bound;
- Segment remains dormant;
- telemetry-only disabled path is neutral.

Do not rerun old accepted stages merely for documentation.

## 6. V2 candidate matrix

After directed/regression gates PASS, run:

```text
T0 V2 10/80
T0 V2 0/80
T1 V2 10/80
T1 V2 0/80
T2 V2 10/80
T2 V2 0/80
```

Use the corrected V1 candidate-private zero-latency configs, not the invalid inherited T1/T2 pseudo-0/80 configs.

These six points are independent after build/input qualification.

Follow `EXECUTION_PRIORITY_POLICY_V5.md`:

- audit CPU/RAM/I/O/storage;
- launch maximum safe parallel set;
- speculative execution is allowed when only scientific admission ordering remains.

For every valid point require:

- terminal completion;
- instructions unchanged;
- CTA unchanged;
- translated_unique == unique;
- untranslated = 0;
- unobserved = 0;
- Segment functional activity = 0;
- no duplicate data side effect;
- terminal translation-controller quiescence.

## 7. Primary comparison

Compare Legacy vs V1 vs V2.

Published anchors:

```text
Legacy:
T0 10/80 1654548 ; 0/80 711464
T1 10/80 3114834 ; 0/80 1252198
T2 10/80 152777  ; 0/80 71654

V1:
T0 10/80 756812  ; 0/80 693548
T1 10/80 1320195 ; 0/80 1251826
T2 10/80 111607  ; 0/80 71743
```

Independently accepted V1 residual sensitivities:

```text
T0  8.3593%
T1  5.1787%
T2 35.7182%
```

Report for each target:

- V2 10/80 and 0/80 cycles;
- V2 residual sensitivity;
- delta V1 -> V2;
- prelaunch READY applications;
- head-path READY applications;
- ready-but-unapplied HOL metric;
- successful downstream admissions;
- unique logical UIDs;
- controller quiescence.

No preconceived numerical threshold.

## 8. Classification

Allowed closeout classifications:

- `READY_APPLICATION_HOL_CONFIRMED`
- `READY_APPLICATION_HOL_PARTIAL`
- `READY_APPLICATION_HOL_NOT_PRIMARY`
- `V2_CANDIDATE_SEMANTICS_INVALID`
- `INSUFFICIENT_EVIDENCE`

Interpretation:

- If V2 materially reduces the V1 residual, especially T2, while preserving all invariants, READY application HOL is an additional simulator amplification source.
- If T0/T1 stay stable but T2 drops, that is a clean T2-specific residual closure.
- If T2 remains sensitive, do not tune parameters to force a result; next review will examine higher-level LD/ST dispatch or zero-latency retry ordering.
- Even a successful V2 remains diagnostic and is not hardware-calibrated.

## 9. V1 provenance carry-forward

Do not spend a separate round repairing V1 documentation.

In the V2 review pack, add one compact `V1_PROVENANCE_ADDENDUM.md` that records:

- V1 execution authority `ad6f38878bc1e7c268b17e65fdb3793a3899a84d`;
- ChatGPT review classification `SERIAL_ACCESSQ_FRONTEND_AMPLIFICATION_PARTIAL`;
- V1 report's blank Decision section;
- original V1 deliverables that were omitted;
- first invalid T1/T2 inherited-config 0/80 attempts, if their receipts/logs still survive;
- no rerun is required solely to repair these documentation gaps.

This closes the small provenance debt during a real scientific stage.

## 10. Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/TRANSLATION_FRONTEND_READY_APPLICATION_RECALIBRATION_174NEW_V2_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_TRANSLATION_FRONTEND_READY_APPLICATION_RECALIBRATION_V2/`

Required:

```text
README.md
SOURCE_ANCHORS.md
V1_PROVENANCE_ADDENDUM.md
V2_SEMANTIC_CONTRACT.md
V2_SOURCE.patch
DIRECTED_READY_APPLICATION_TESTS.tsv
REGRESSION_GATES.tsv
V2_CROSS_TARGET_MATRIX.tsv
READY_APPLICATION_ACCOUNTING.tsv
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
RECALIBRATION_DECISION.md
SHA256SUMS
```

## 11. Publication / STOP

Follow `174_MANDATORY_REMOTE_PUBLICATION_CONTRACT.md`.

Complete:

```text
report/review pack
-> SHA256SUMS
-> commit
-> push
-> fetch-back
-> remote HEAD == local HEAD
-> remote tree verification
-> clean worktree
-> STOP for ChatGPT review
```

Use existing HTTPS -> HTTP/1.1 -> SSH -> gh/API transport fallback if needed.

Do not:

- promote V1/V2 to accepted baseline;
- change target/input identity;
- change 10/80 values to fit expectations;
- implement a TLB/PTW/cache mechanism;
- resume 109 side lanes;
- start external hardware claims.

External/reference/native calibration comes only after frontend semantic closure.
