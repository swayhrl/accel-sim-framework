# ChatGPT Review — Translation Hit-Path Semantic Attribution V1

Date: 2026-09-22

Reviewed execution:

`hrl/awma-174-hitpath-semantic-attribution-v1`

Remote HEAD:

`f79aaa1d22d2a22912e8b71dc832bdbf31a899f7`

Decision:

`AWMA_TRANSLATION_HITPATH_SEMANTIC_ATTRIBUTION_V1_ACCEPTED`

## 1. Accepted attribution

Final classification:

`MIXED_MODEL_EFFECT`

Supported components:

- `SERIALIZED_PRE_ADMISSION_LOOKUP_WAIT_DOMINANT`
- `ACCESSQ_HEAD_OF_LINE_TRANSLATION_BLOCKING_DOMINANT`
- `ZERO_LATENCY_RETRY_ORDERING_NONLINEARITY`

No new simulation or instrumentation was required.

## 2. Strong source-backed mechanism

The repaired shader path operates on `inst.accessq_back()`.

For an untranslated back entry:

1. translation is requested;
2. non-READY returns `COAL_STALL`;
3. downstream L1D/ICNT admission is blocked;
4. the back entry remains in the accessq;
5. later accessq entries do not independently progress through downstream admission.

The translation controller itself can hold inflight lookup operations, but the
shader frontend exposes only the current back entry to this pre-admission path.

Therefore positive lookup latency can be amplified by accessq-level
serialization/head-of-line blocking.

## 3. Accounting consistency

Natural 10/80 requester latency is overwhelmingly the modeled L1 service sum:

```text
T0: 10 * L1 lookups / requester latency = 98.29%
T1: 10 * L1 lookups / requester latency = 98.15%
T2: 10 * L1 lookups / requester latency = 93.15%
```

A useful cross-SM heuristic is:

```text
(delta cycles / L1 lookup) * 35 SM

T0 = 10.68 cycles
T1 =  9.10 cycles
T2 =  6.90 cycles
```

This is not a formal performance decomposition, but T0/T1 are notably close to
the configured 10-cycle service and support the source-backed serialization
hypothesis.

## 4. T2 admission multiplicity is resolved

T2:

```text
10/80:
  coverage admissions = 411,008
  unique UIDs         = 411,008

0/80:
  coverage admissions = 476,907
  unique UIDs         = 411,008
```

Thus the extra 65,899 are repeated admission attempts/re-admissions of existing
logical accesses.

The existing `vm_cov_note` callsite counts an attempt before the access is
necessarily consumed/popped from the accessq.

Therefore the historical field named `admissions` must not be interpreted as
a unique logical downstream transaction count.

Future telemetry must distinguish:

- admission attempts;
- successful downstream admissions;
- unique logical access UIDs.

This does not invalidate the per-access translation coverage claim because
translated attempts and translated unique UIDs remain closed, but the field
semantics need correction.

## 5. Recalibration principle

Do NOT recalibrate by merely changing:

`L1 lookup latency 10 -> 1`

or another convenient constant.

The first diagnostic semantic repair should isolate the identified frontend
coupling:

> allow translation lookups for multiple coalesced accesses to be launched
> ahead, subject to the existing lookup-port throughput, while retaining the
> rule that each individual access may enter L1D/ICNT only after its own
> translation is READY.

This explicitly separates:

- lookup latency;
- lookup throughput;
- downstream admission correctness.

Keep lookup probe-at-completion semantics unchanged in the first candidate so
only one semantic axis changes.

## 6. Baseline status

The legacy repaired model remains the accepted historical baseline.

A candidate pipelined frontend is:

`DIAGNOSTIC_RECALIBRATION_CANDIDATE`

until:

- directed semantics pass;
- telemetry is neutral/correct;
- T0/T1/T2 reruns close;
- ChatGPT reviews the residual sensitivity;
- external/reference/native calibration is considered.

Do not silently replace historical results.

## 7. Next stage

Proceed to:

`AWMA_TRANSLATION_FRONTEND_PIPELINING_RECALIBRATION_V1`

No architecture mechanism.
