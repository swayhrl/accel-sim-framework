# EP-L2 M3A — RO Certification / Pending-State Minimality Acceptance Criteria

## A. Source identity

All source claims must be anchored to the reviewed M0b/integration source family. If M0b final scan causes a semantic producer/source change, runtime descendants are invalid until revalidated.

## B. Safe eligibility

PASS requires either:

```text
SAFE_RO_ELIGIBLE = a source-proven conservative predicate
```

or an explicit:

```text
NO_SOURCE_PROVEN_SAFE_CLASS
```

A predicate based only on read/not-atomic type is insufficient.

## C. State completeness

Every state currently owned by a traditional Line-MSHR must be classified as:

```text
must retain
already represented elsewhere
safe to discard at boundary A
safe to discard at boundary B
unknown / needs proof
```

Requester descriptors remain explicitly costed and semantically preserved.

## D. Candidate boundary correctness

Both Candidate A and Candidate B must define exact source transition events and late-merge/order/fill/response behavior.

Do not recommend Candidate A solely because it offers a longer lifetime window. Prefer Candidate B if it provides meaningful structural relief with substantially simpler correctness.

## E. Lifetime evidence

If a design recommendation depends on an unmeasured tail interval, PASS requires a timing-neutral observation-only measurement or an explicit `UNKNOWN_NEEDS_MEASUREMENT` decision.

No inferred retirement timestamps.

## F. Metadata fairness

Any claimed metadata saving must include all state moved into the pending object plus references to requester descriptors/tag/payload state. Do not compare a complete Line-MSHR against an incomplete pending object.

## G. No functional behavior change

M3A may add default-OFF telemetry only when needed for the design decision. It may not release, bypass, replace, or shorten the functional Line-MSHR lifetime.

Any new telemetry must pass exact OFF/ON timing-neutrality on at least:

```text
convolutionSeparable
spmv
sad
```

or explain why a narrower directed-only measurement is sufficient.

## H. Directed plan completeness

The future functional design must have an explicit test plan for multi-sector fill, late merge, same-line writes, atomics, writebacks, stale fill/generation, response backpressure, address reuse, and terminal drain.

## I. Decision output

Final `DECISION_MATRIX.md` must select one of:

```text
FUNCTIONAL_M3A_CANDIDATE_A_READY_FOR_HANDOFF
FUNCTIONAL_M3B_CANDIDATE_B_READY_FOR_HANDOFF
NEEDS_NARROW_LIFETIME_MEASUREMENT_FIRST
NO_SAFE_M3_DIRECTION_CURRENTLY
```

The label must follow evidence, not mechanism preference.

## J. Completion

Required status:

```text
M3A_RO_CERTIFICATION_REVIEW_READY
```

This is not functional M3 completion.
