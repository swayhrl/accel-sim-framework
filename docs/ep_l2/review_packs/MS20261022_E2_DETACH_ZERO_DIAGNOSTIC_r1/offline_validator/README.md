# E2 independent offline declaration checker

This is a preparation artifact in /tmp, not an adopted production parser, native
qualification, application acceptance, or evidence that a simulator really
observed a count. It changes no repository, central state, binary, or input.

Run with Python standard library only:

    PYTHONDONTWRITEBYTECODE=1 python3 test_validator.py
    PYTHONDONTWRITEBYTECODE=1 python3 validator.py example_synthetic_document.json

`audit(document)` returns INVALID, INCOMPLETE, or VALID_DECLARATIONS_ONLY.
No formal A2/D metric names are assumed. The example aliases are synthetic.

An owner-reviewed adapter must translate actual versioned records into:

- `declarations.domains`, and metric declarations with domain, unit, and
  measurement_kind. Real-transition reconciliation across domains additionally
  requires the same event_identity, SAME_REAL_TRANSITION bridge, and evidence.
  This cannot equate head exposures with access attempts.
- Records keyed by exact ID and scope: domain, level, half-open physical clock
  interval, dimensions including run/config population, overlap/attribution for
  kernel intervals. Counters are {status: OK, value: integer} or {status: NA,
  reason: text}; unavailable counters never become 0. Bool is not an integer.
- Required scopes and metrics. For a full production result the adapter must
  declare all 64 expected slice scopes, global scope and residual scopes; the
  generic checker deliberately does not invent the eventual emission schema.
- Explicit mutually exclusive partition equations; same-population equivalence
  equations; slice/kernel rollups with exact expected membership and explicit
  residual/unattributed handling. Nonexclusive masks cannot be partition terms.
  Kernel intervals marked overlapping or physically overlapping cannot be summed.
- Explicit overflow flags, and bounded sample cap/emitted/dropped/truncated
  metadata. Sample cap cannot exceed 64; emission count and bounded rows agree.

The supplied adversarial controls include omitted and double counted reasons,
raw FAIL rewritten to MISS, native relief not consulted, legal detach followed
by requester denial, multiple waiter responses for one transaction, NA omission,
missing expected slice, overlap, domain/unit mismatch, transition reconciliation,
integer/overflow/sample checks. Runtime counters are not inferred from samples.

For raw pressure, use the current COUNTER_CONTRACT's three-way intermediate
partition (rewritten, remained-failed, relief-not-consulted). The source review's
older two-term shorthand is limited to paths where RO relief was consulted;
using it for native preview would omit a valid category.

The root owner must review and adopt any repository copy and any real adapter.
Later source/native/resource/input/comparison acceptance remains independent.

## Root review scope fix

The original checker incorrectly accepted declared slice labels 0/1 when the
actual children were slice0/slice99. The unchanged before-fix input/output is in
ROOT_REVIEW_FAILURE_WITNESS.json. The rejected after-fix result and changes are in
ROOT_SCOPE_FIX_RECEIPT.json. Historical code/receipt in history/ are evidence only,
not the current validator. Current controls: 51.

Every dimension set requires a nonempty string run ID. Slice totals require an
integer slice ID; kernel intervals require both integer slice and kernel IDs;
unattributed kernel residuals require the literal kernel dimension UNATTRIBUTED.
Rollup labels must equal actual child dimensions. Kernel rollups have one slice
parent and retain its slice ID when checking populations; combine slices only
through a separate slice rollup. NA cannot suppress these identity checks.
