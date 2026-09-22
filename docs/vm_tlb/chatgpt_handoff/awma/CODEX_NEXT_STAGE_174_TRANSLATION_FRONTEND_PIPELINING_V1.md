# CODEX NEXT STAGE — Translation Frontend Pipelining Recalibration V1

Date: 2026-09-22

Mode:

`GOAL MODE / solve-and-continue / MODEL-SEMANTIC DIAGNOSTIC`

Node:

`174-new`

Stage:

`AWMA_TRANSLATION_FRONTEND_PIPELINING_RECALIBRATION_V1`

Coordination branch:

`hrl/awma-mainline-reset-crossview-v2`

Read first:

1. `CURRENT_STATE.md`
2. `EXECUTION_PRIORITY_POLICY_V3.md`
3. `REVIEW_174_HITPATH_ATTRIBUTION_V1_2026-09-22.md`
4. accepted attribution pack at `f79aaa1d22d2a22912e8b71dc832bdbf31a899f7`
5. accepted V3R1 at `7a4f2a419fe77c017cb9a9a5555b1551a2fc884c`
6. this Goal

Suggested execution branch:

`hrl/awma-174-translation-frontend-pipelining-v1`

## 0. Frozen boundaries

Historical repaired baseline remains unchanged.

Do not overwrite old semantics.

New behavior must be opt-in and labelled:

`DIAGNOSTIC_RECALIBRATION_CANDIDATE`

No hardware-performance claim.

No TLB/PTW/cache architecture mechanism.

## 1. Phase A — telemetry semantic repair

Before changing performance semantics, fix/extend coverage telemetry so it
distinguishes:

```text
admission_attempts
successful_downstream_admissions
unique_logical_access_uids
translated_attempts
translated_unique_uids
```

Requirements:

- retain legacy `AWMA_VM_COVERAGE admissions=` for backward parsing if needed,
  but document it as attempt-count semantics;
- add a true successful-admission counter only after the downstream access is
  actually accepted/consumed according to the existing L1D/ICNT path;
- do not change control flow, queue decisions, cache behavior, timing, or
  translation behavior.

Run telemetry-neutrality checks on T0/T1/T2 10/80 in parallel if resource
audit permits.

Require exact equality of:

- cycles;
- instructions;
- CTA;
- TLB/PTW/PWC/PTE counters;
- unique logical UIDs;
- Segment dormancy.

Create:

`COVERAGE_TELEMETRY_SEMANTIC_REPAIR.md`

and:

`TELEMETRY_NEUTRALITY.tsv`

## 2. Phase B — design a single-axis frontend candidate

Implement an opt-in mode that changes only translation launch overlap within
the coalesced accessq.

Suggested labels:

```text
LEGACY_ACCESSQ_BACK_SERIAL
PIPELINED_ACCESSQ_TRANSLATION_LAUNCH
```

Exact implementation may differ if source constraints require it, but the
candidate contract is mandatory:

1. every VM-eligible coalesced `mem_access_t` still requires its own
   translation before downstream L1D/ICNT admission;
2. multiple accesses belonging to the resident accessq may have translation
   lookups in flight concurrently;
3. lookup launch throughput is limited by the existing L1 TLB port semantics;
4. configured L1 lookup latency remains 10 cycles in natural runs;
5. positive latency is a service/ready interval, not a forced
   `10 cycles * number_of_accesses` launch serialization;
6. downstream admission order remains consistent with the existing accessq
   contract unless source proof requires a different frozen order;
7. MSHR/PWQ/walker/PWC/PTE semantics are unchanged;
8. probe-at-completion semantics remain unchanged in this V1 candidate;
9. no untranslated access may enter the data path;
10. no duplicate store/atomic/data side effect.

Do not release or redesign the whole LD/ST dispatch pipeline in V1 unless
strictly necessary to satisfy the above.  First isolate accessq translation
launch serialization.

Create:

`PIPELINED_FRONTEND_SEMANTIC_CONTRACT.md`

## 3. Phase C — directed machine-checkable tests

Construct directed tests that demonstrate latency/throughput separation.

At minimum:

### C1 — four warm L1-hit accesses

With L1 latency=10 and one launch port, prove candidate launch/ready pattern is
consistent with pipelining, conceptually:

```text
launch: 0,1,2,3
ready: 10,11,12,13
```

or the exact cycle-equivalent dictated by the source clocking convention.

Legacy mode should retain its original serialized behavior.

### C2 — zero-latency compatibility

Candidate 0-cycle behavior must not create duplicate logical accesses or
translation bypass.

### C3 — miss / MSHR path

Multiple lookups may become inflight, but MSHR merge/allocation and PTW
conservation must remain accepted.

### C4 — stores/atomics

Exactly-once data side effects.

Create:

`DIRECTED_PIPELINING_TESTS.tsv`

## 4. Phase D — candidate neutrality boundaries

Before full target runs prove:

- legacy mode reproduces accepted historical values;
- candidate mode with a single-access synthetic instruction matches legacy;
- Segment remains dormant under F0;
- no address/coalescing/cache configuration changes.

## 5. Phase E — T0/T1/T2 candidate matrix

After source and directed gates pass, run:

```text
T0 candidate 10/80
T0 candidate 0/80
T1 candidate 10/80
T1 candidate 0/80
T2 candidate 10/80
T2 candidate 0/80
```

Follow `EXECUTION_PRIORITY_POLICY_V3.md`.

These six runs have no scientific data dependency after candidate build and
input binding.  Perform resource audit and launch the maximum safe parallel
set.

For every run require:

- terminal completion;
- full successful-admission coverage;
- translated unique UIDs == unique logical UIDs;
- untranslated/unobserved = 0;
- Segment functional counters = 0;
- instruction and CTA completion unchanged.

## 6. Compare legacy vs candidate

Report for each target:

- legacy 10/80 cycles;
- candidate 10/80 cycles;
- legacy 0/80 cycles;
- candidate 0/80 cycles;
- legacy L1-zero sensitivity;
- candidate L1-zero sensitivity;
- L1 lookup count;
- translation launch concurrency;
- translation-caused HOL stall cycles;
- successful downstream admissions;
- unique logical UIDs.

Primary question:

> Does allowing lookup launch overlap remove most of the 53-60% legacy
> sensitivity while preserving per-access correctness?

Do not require a preconceived numeric threshold.

## 7. Classification

At closeout classify:

- `SERIAL_ACCESSQ_FRONTEND_AMPLIFICATION_CONFIRMED`
- `SERIAL_ACCESSQ_FRONTEND_AMPLIFICATION_PARTIAL`
- `SERIAL_ACCESSQ_FRONTEND_NOT_PRIMARY`
- `CANDIDATE_SEMANTICS_INVALID`
- `INSUFFICIENT_EVIDENCE`

Candidate remains diagnostic.

## 8. External calibration boundary

Even if candidate removes the large sensitivity, do not declare it
hardware-accurate.

Closeout must list what further evidence would be required to promote it:

- published/reference GPU translation overlap semantics;
- native microbenchmark evidence if feasible;
- regression against established Accel-Sim behavior;
- sensitivity to lookup latency/port count after serialization artifact is
  removed.

STOP for ChatGPT review before replacing the baseline.

## 9. Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/TRANSLATION_FRONTEND_PIPELINING_RECALIBRATION_174NEW_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_TRANSLATION_FRONTEND_PIPELINING_RECALIBRATION_V1/`

Required:

```text
README.md
SOURCE_ANCHORS.md
COVERAGE_TELEMETRY_SEMANTIC_REPAIR.md
TELEMETRY_NEUTRALITY.tsv
PIPELINED_FRONTEND_SEMANTIC_CONTRACT.md
DIRECTED_PIPELINING_TESTS.tsv
LEGACY_REPRODUCTION.tsv
CANDIDATE_CROSS_TARGET_MATRIX.tsv
TRANSLATION_LAUNCH_CONCURRENCY.tsv
HOL_STALL_ACCOUNTING.tsv
RECALIBRATION_DECISION.md
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

## 10. Publication

Apply mandatory 174 remote publication contract.

Then STOP.

No architecture mechanism.
