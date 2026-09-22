# CODEX NEXT STAGE — Translation Hit-Path Semantic Attribution V1

Date: 2026-09-22

Mode:

`GOAL MODE / solve-and-continue / MODEL-VALIDITY ONLY`

Node:

`174-new`

Stage:

`AWMA_TRANSLATION_HITPATH_SEMANTIC_ATTRIBUTION_V1`

Coordination branch:

`hrl/awma-mainline-reset-crossview-v2`

Read first:

1. `CURRENT_STATE.md`
2. `EXECUTION_PRIORITY_POLICY_V3.md`
3. `CROSSVIEW_DECISION_HITPATH_VALIDITY_2026-09-22.md`
4. accepted V3R1 pack at `7a4f2a419fe77c017cb9a9a5555b1551a2fc884c`
5. repaired coverage authority `3f7bc0cd3cb3667b38fa0dd803ac034e19b493d6`
6. this Goal

Suggested execution branch:

`hrl/awma-174-hitpath-semantic-attribution-v1`

## 0. Frozen scientific result

Do not rerun the cross-target matrix by default.

Accepted:

```text
T0 10/80 -> 0/80: 56.9995%
T1 10/80 -> 0/80: 59.7989%
T2 10/80 -> 0/80: 53.0990%
```

Primary classification:

`HITPATH_SENSITIVITY_SYSTEMATIC_ACROSS_KERNEL_CLASSES`

Mechanism work remains forbidden.

## 1. Phase A — source-only critical-path audit

No simulation first.

Trace the exact source path for one VM-eligible coalesced access from:

```text
warp memory instruction
-> accessq
-> translation request
-> L1 lookup launch
-> lookup ready
-> vm_translation_applied
-> L1D or bypass-ICNT downstream admission
```

Audit and document:

- when translation is first requested for an access;
- whether only `accessq_back()` is translated at a time;
- whether multiple coalesced accesses from the same memory instruction may have
  translation lookups concurrently in flight;
- whether an untranslated back entry causes `COAL_STALL` and prevents another
  access in the same accessq from progressing;
- whether L1 lookup latency is a pipelined service latency or a serialized
  requester wait;
- L1 TLB port throughput semantics;
- translation-controller queue/inflight capacity;
- per-SM vs global scope of each queue/resource;
- exact behavior when L1 latency is zero;
- whether zero latency invokes same-cycle service and changes retry/admission
  ordering.

Create:

`HITPATH_SOURCE_CRITICAL_PATH.md`

and:

`LOOKUP_PIPELINE_SEMANTICS.tsv`

Every claim requires source-location evidence.

## 2. Phase B — explain existing accounting before adding counters

Using existing V3R1 receipts, compute per target:

- total L1 lookup service implied by `10 * L1_accesses`;
- requester total translation latency;
- requester MSHR wait;
- total simulated cycles;
- cycle delta 10/80 -> 0/80;
- delta cycles per L1 lookup;
- L1 lookups per simulated instruction;
- L1 lookups per accepted Native memory-instruction record where available.

Create:

`EXISTING_HITPATH_ACCOUNTING.tsv`

Explicitly test whether requester total latency is approximately:

`10 * L1_accesses + residual`

Do not equate requester-cycle sums with GPU critical-path cycles.

## 3. Phase C — T2 admission-multiplicity forensics

Without rerunning first, explain why:

```text
T2 10/80 admissions = 411,008
T2 0/80  admissions = 476,907
```

while:

- instructions are identical;
- CTA are identical;
- L1 lookup counts differ by only ~0.077%.

Audit:

- definition of AWMA_VM_COVERAGE admission;
- whether the same access UID may be counted more than once;
- retries/re-admissions;
- positive/zero-latency L1D paths;
- bypass-ICNT path;
- coalescing queue behavior;
- whether `vm_cov_note` is attached to attempts or unique logical accesses.

Create:

`T2_ADMISSION_MULTIPLICITY_FORENSICS.md`

and, if existing raw logs suffice:

`T2_ADMISSION_UID_ACCOUNTING.tsv`

Do not silently assume admission count should be invariant.

## 4. Phase D — minimal neutral instrumentation only if required

Only if Phases A-C cannot quantify the critical path from existing evidence.

Instrumentation may add counters only; no functional/timing changes.

Candidate counters:

- translation-caused `COAL_STALL` events;
- cycles with an accessq blocked solely on translation;
- accessq depth when translation wait begins;
- number of other ready accesses blocked behind the untranslated back entry;
- per-instruction number of sequential translation waits;
- concurrent translation lookups per memory instruction / SM;
- L1-hit lookup launch -> ready cycles;
- ready -> downstream-admission cycles;
- duplicate admission count by access UID.

Instrumentation must have a neutrality gate.

Use the smallest representative runs first.

## 5. Parallel execution policy

Follow `EXECUTION_PRIORITY_POLICY_V3.md`.

After dependency analysis and resource audit:

- run all independent instrumentation-neutrality checks in parallel;
- run T0/T1/T2 instrumented 10/80 attribution points in parallel if required
  and resources permit;
- checkpoint/hash each completion immediately;
- generate source/accounting reports concurrently with long simulations.

Scientific admission may remain ordered; execution should not be serialized
without a real dependency.

## 6. Attribution outcome

Classify one or more source-backed mechanisms of the modeled sensitivity:

- `SERIALIZED_PRE_ADMISSION_LOOKUP_WAIT_DOMINANT`
- `ACCESSQ_HEAD_OF_LINE_TRANSLATION_BLOCKING_DOMINANT`
- `LOOKUP_THROUGHPUT_LIMIT_DOMINANT`
- `REQUESTER_WAIT_WITH_HIGH_OVERLAP`
- `ZERO_LATENCY_RETRY_ORDERING_NONLINEARITY`
- `MIXED_MODEL_EFFECT`
- `INSUFFICIENT_ATTRIBUTION`

These describe simulator behavior, not hardware.

## 7. Recalibration proposal boundary

At closeout, propose candidate simulator semantic repairs/calibration options,
but do NOT implement them yet unless they are strictly telemetry-only.

For each candidate state:

- what current semantic it changes;
- hardware/reference evidence needed;
- expected effect on T0/T1/T2;
- regression risk;
- whether old traces remain reusable.

STOP for ChatGPT review before implementing a new hit-path model.

## 8. Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/TRANSLATION_HITPATH_SEMANTIC_ATTRIBUTION_174NEW_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_TRANSLATION_HITPATH_SEMANTIC_ATTRIBUTION_V1/`

Required:

```text
README.md
SOURCE_ANCHORS.md
HITPATH_SOURCE_CRITICAL_PATH.md
LOOKUP_PIPELINE_SEMANTICS.tsv
EXISTING_HITPATH_ACCOUNTING.tsv
T2_ADMISSION_MULTIPLICITY_FORENSICS.md
T2_ADMISSION_UID_ACCOUNTING.tsv
INSTRUMENTATION_NEUTRALITY.tsv
HITPATH_ATTRIBUTION.tsv
RECALIBRATION_CANDIDATES.md
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

If no new simulation is needed, run-dependent files may explicitly state
`NOT_RUN_EXISTING_EVIDENCE_SUFFICIENT`.

## 9. Publication

Apply mandatory 174 remote publication contract.

Then STOP.

No architecture mechanism.
