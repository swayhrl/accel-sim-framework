# E2 mechanism-analysis preparation

`report.py` consumes E's future independently accepted adapter output. It does
not read native records, guess A2 field names, accept an application, validate
producer arithmetic, or parse a raw log. D's semantic concepts are an explicit
consumer vocabulary; the E-reviewed mapping must bind exact source/native
schema/field scope before use. This is all preparation in `/tmp`.

Run standard-library synthetic controls:

    PYTHONDONTWRITEBYTECODE=1 python3 /tmp/e2_detach_analysis/test_report.py

Create the empty semantic input template (no application counts):

    python3 /tmp/e2_detach_analysis/report.py --template --out semantic_input.json

After an E accepted record and reviewed adapter mapping actually exist:

    python3 /tmp/e2_detach_analysis/report.py accepted_semantics.json --out analysis.json

The template has no measured data and yields INCOMPLETE, not a numerical
scientific conclusion. No real result is supplied or manufactured here.

Every usable counter needs explicit semantic domain, unit, measurement kind,
E-reviewed mapping reference, matching run/scope/half-open physical interval,
full accepted64slice coverage and explicit no-overflow status. These declarations
are premises already checked by E's actual validator: this consumer cannot prove
them by trusting an input file. REAL_ACCEPTED additionally requires E's real
CURRENT_ACCEPTED_DIAGNOSTIC_POINT endpoint receipt, adapter and schema refs. Missing/NA/unknown counters
never become zero; malformed numeric declarations suppress all claims.

Head cycles are not unique requests. Way predicate masks are nonexclusive;
first-reason counts depend on precedence. There are no implicit sums, percentages,
causal shares or wait-to-program-stall conversions. In particular, no adding
pressure snapshots to commit calls or waiter responses to detached transactions.

Not-consulted is separate from evaluated-no-eligible; sticky-reuse history is
separate from required-sector readiness. A victim detach is separate from its
requesters' responses/retirement and from acceptance or later retry of the
triggering request. Merely observing positive detach counters does not grant
an independent NONZERO_CLOSED qualification: E alone accepts lifetime closure.

The historical upstream explanations for old E048 SGEMM and E050 FWT refer only
to the exact records in E's causal scope matrix. A new positive-certificate
SGEMM observer cannot backfill their missing dynamic history or explain a
different application's old positive-RO detach0. No old/new binary performance
ratio or retrofit of old results is allowed.

The25 synthetic adversarial controls cover missing input, missing metrics,
not-consulted, missing pressure, head-cycle/request confusion, missing slice,
bool masquerading as count, overflow, overlapping sticky/ready predicates,
victim-vs-trigger/response, incompatible scope intervals, real acceptance
absence, and NA with an invented number. They are Python engineering controls,
not native tests, application executions, simulator validation or qualifications.

## Root-reviewed endpoint scope fix

The original consumer incorrectly required a generic CURRENT_ACCEPTED label,
accepted a negative physical-clock interval and an above-uint64 counter, and
allowed a pair-shaped receipt. Initial files are preserved under history/initial/.
ROOT_REVIEW_FAILURE_WITNESS.json contains unchanged actual before-fix inputs and
outputs; ROOT_SCOPE_FIX_RECEIPT.json records their corrected results.

Real input must normalize E's actual independently accepted endpoint as:

- acceptance.status: CURRENT_ACCEPTED_DIAGNOSTIC_POINT
- acceptance.endpoint_status: COMPLETE_VALID
- acceptance.scientific_scope: DETACH_OBSERVER_DIAGNOSTIC_POINT_V1
- acceptance.pair: false

This is an observational diagnostic point, never a formal S/F pair. Receipt,
adapter and producer-schema refs each require commit40hex/path/nonempty/SHA256
structure. The consumer checks only structure; E upstream checks their actual
existence, hashes, producer mapping and acceptance. Qualification_id is required
as64hex. Counts and nonnegative half-open physical clock bounds reject bool
and values above uint64.25 synthetic controls pass, including a structurally
valid E diagnostic point, fake pair, wrong scope, negative/bool interval, count
overflow, missing/malformedQ and missing identity/reference hashes.
