# CODEX 174 CONTINUATION — V2 READY Consumption Correctness Requalification

Date: 2026-09-23

Mode:

`GOAL MODE / bounded correctness repair / solve-and-continue`

Node:

`174-new`

Stage:

`AWMA_TRANSLATION_FRONTEND_READY_APPLICATION_RECALIBRATION_V2R1`

Read first:

1. `REVIEW_174_TRANSLATION_FRONTEND_READY_APPLICATION_V2_2026-09-23.md`
2. pre-repair V2 execution authority:
   `hrl/awma-174-translation-frontend-ready-application-v2 @ 1a5f4dc49273c9640b981fb1b946d146dd15f21b`
3. V1 READY ownership authority:
   `hrl/awma-174-translation-frontend-pipelining-v1 @ ad6f38878bc1e7c268b17e65fdb3793a3899a84d`
4. `EXECUTION_PRIORITY_POLICY_V5.md`

This is not a new scientific stage. It repairs a local V2 READY-consumption bookkeeping defect discovered in independent review.

## 0. Frozen scope

Do not rerun:

- T0;
- T1;
- canonical input recovery;
- V3/V3R1;
- hit-path attribution;
- V1 matrix;
- Native calibration.

109 remains idle.

No TLB/PTW/cache mechanism is authorized.

## 1. Confirm the source-level defect

Before editing, inspect the exact candidate source and confirm:

- V1 `translate(..., consume_ready=false)` returns READY without erasing the corresponding `m_lookups` entry;
- V2 prelaunch currently uses `!ready_application_v2`;
- V2 applies the returned PA/outcome to the resident `mem_access_t`;
- later scans/head path no longer call `translate()` for that applied access;
- therefore a prelaunch-applied READY can remain stranded in `m_lookups`.

Also inspect the pre-repair T2 terminal raw receipts and report, if available:

- total `m_lookups.size()`;
- count by lookup stage, especially `LOOKUP_READY`;
- `quiescent_invariants_hold()`.

If pre-repair raw binary did not print these counters, add a bounded offline/source-supported diagnosis; do not rerun the invalid candidate merely to prove the leak.

## 2. Minimal repair

Preserve the intended V1/V2 distinction:

### V1 pipelined launch

Prelaunch may observe READY but must not consume it.

### V2 ready application

Prelaunch must consume READY exactly once and immediately apply the returned PA/outcome to that exact resident `mem_access_t`.

Use the existing controller API rather than introducing a new side state machine.

The intended call semantics are equivalent to:

```text
V1 -> consume_ready=false
V2 -> consume_ready=true
```

Check exact source context and zero-latency recursion before editing.

A likely minimal expression is:

```cpp
consume_ready = ready_application_v2
```

but implement from the verified source semantics, not by blind text substitution.

## 3. Hard invariants

The repair may not change:

- L1 lookup latency;
- L1 lookup port throughput;
- L2 latency;
- MSHR/PWQ/walker/PWC/PTE semantics;
- probe-at-completion semantics;
- downstream accessq order;
- L1D/ICNT/cache arbitration;
- target/input identity;
- Segment F0 state;
- store/atomic/data exactly-once behavior;
- legacy mode;
- V1 mode.

Every access must still have its own translation applied before downstream admission.

## 4. Directed tests

Before T2 replay, add/execute focused tests that establish:

### R1 — V1 ownership preserved

V1 prelaunch READY observation:
- returns PA/outcome;
- leaves controller READY entry for head consumer;
- head consumes once;
- terminal controller quiescent.

### R2 — V2 consume-and-apply

V2 prelaunch READY:
- consumes controller READY;
- removes exact `m_lookups` entry;
- applies same PA/outcome to exact resident `mem_access_t`;
- later head path does not translate again;
- duplicate application count 0.

### R3 — zero-latency

V2 zero-latency recursive READY path:
- consumes exactly once;
- no double erase;
- no duplicate completion;
- no stranded READY.

### R4 — miss / merge / walk

MSHR-merged/PTW-woken requesters:
- retain existing semantics;
- each exact requester eventually consumes/applies once;
- no stranded lookup after completion.

### R5 — terminal quiescence

Explicitly expose/verify:

```text
m_lookups.size() == 0
LOOKUP_READY count == 0
m_mshrs.size() == 0
m_pwq.size() == 0
active_walks == 0
quiescent_invariants_hold() == true
```

Do not use only MSHR/PWQ/walker drain as a proxy for controller quiescence.

## 5. T2-only requalification

After directed tests PASS, run only:

```text
T2 V2R1 10/80
T2 V2R1 0/80
```

Use the exact same T2 trace/input/config authority as the accepted V1 / pre-repair V2 T2 points.

These two runs may execute in parallel if resource audit permits.

For each require:

- terminal completion;
- gpu_sim_insn = 43,357,696;
- CTA = 1,216;
- unique logical UIDs = 411,008;
- translated_unique = unique;
- untranslated = 0;
- unobserved = 0;
- prelaunch READY applied = 411,008 if behavior remains the same;
- duplicate application = 0;
- head applied counted consistently;
- Segment functional activity = 0;
- no duplicate data side effect;
- `m_lookups.size() == 0`;
- `LOOKUP_READY count == 0`;
- full controller quiescence true.

Do not require cycle equality with the pre-repair result.

## 6. Performance / host-time observation

Because the pre-repair V2 likely accumulated READY entries, record:

- host wall-clock for fixed T2 10/80 and 0/80;
- pre-repair wall-clock if surviving receipt timestamps allow deterministic recovery;
- terminal/peak lookup-entry count if cheaply observable.

This is engineering evidence only.

Do not change simulator semantics for host performance.

If READY cleanup naturally removes the prior host-time explosion, document it.

## 7. Scientific classification

Recompute:

`residual = (cycles_10_80 - cycles_0_80) / cycles_10_80`

Allowed final outcomes remain:

- `READY_APPLICATION_HOL_CONFIRMED`
- `READY_APPLICATION_HOL_PARTIAL`
- `READY_APPLICATION_HOL_NOT_PRIMARY`
- `V2_CANDIDATE_SEMANTICS_INVALID`
- `INSUFFICIENT_EVIDENCE`

If V2R1 reproduces 111607 / 71743 with true quiescence, accept:

`READY_APPLICATION_HOL_NOT_PRIMARY`

If cycles differ, classify from repaired evidence.

Do not tune implementation toward the old values.

## 8. Pre-repair V2 provenance

Preserve pre-repair V2 authority:

`1a5f4dc49273c9640b981fb1b946d146dd15f21b`

Label its T2 results:

`PRE_REPAIR_READY_RETENTION_INVALID_FOR_FINAL_CLASSIFICATION`

Do not delete its report or raw archive.

## 9. Deliverables

Suggested execution branch:

`hrl/awma-174-translation-frontend-ready-application-v2r1`

Report:

`docs/vm_tlb/codex_handoff/awma/TRANSLATION_FRONTEND_READY_APPLICATION_RECALIBRATION_174NEW_V2R1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_TRANSLATION_FRONTEND_READY_APPLICATION_RECALIBRATION_V2R1/`

Required:

```text
README.md
SOURCE_ANCHORS.md
PRE_REPAIR_V2_DIAGNOSIS.md
READY_CONSUMPTION_REPAIR.patch
DIRECTED_READY_CONSUMPTION_TESTS.tsv
T2_REQUALIFICATION.tsv
CONTROLLER_QUIESCENCE.tsv
HOST_TIME_OBSERVATION.tsv
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
RECALIBRATION_DECISION.md
SHA256SUMS
```

## 10. Publication / STOP

Follow mandatory 174 publication contract:

```text
report + review pack
-> SHA256SUMS
-> commit
-> push
-> fetch-back
-> remote HEAD == local HEAD
-> remote tree verification
-> clean worktree
-> STOP
```

Do not start Native↔simulator cross-calibration in this Goal.
