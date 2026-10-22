# E2 source-aware observer framing and terminal decoder

Preparation only. The fixed-source reference is Core
`cf7347151f86a17866b91af6d3f2da726ea8d062`, based on d010.
`SOURCE_BOUND_SCHEMA_cf.json` records the172 counter names extracted directly
from that commit's observer header and its SHA256. No real application raw
or binary was read. There is no application evidence or scientific PASS here.

Run the48 standard-library synthetic engineering controls:

    PYTHONDONTWRITEBYTECODE=1 python3 /tmp/e2_detach_runtime_decoder/test_decoder.py

Future caller use, after exact producer schema/source binding and independent
native/build/input/resource qualification:

    python3 decoder.py FINAL_RAW --schema EXACT_BOUND_SCHEMA --out observer.json

Defaults require64 exact physical slices, T/M/RO-runtime=true and closed epoch.
For a bounded fixture only, the Python constructor can explicitly use
`expected_slice_count=2, require_closed=False`. This is not full-app qualification.

The decoder opens raw only once and consumes bounded readline records. It ignores
unrelated legacy lines, decodes `EPL2DETACH_DIAG_V1|` JSON and collects old
`EPL2ROV1|SUMMARY|` during the same pass. JSON duplicate keys, uint64/bool errors,
missing/extra metadata/counter fields, overflow, output-invalid, oversized input,
line or observer output, truncated framing, conflicting duplicates and regressing
snapshot clocks are refused. Latest complete snapshot is used; an incomplete
new tail is not hidden by falling back to an older complete snapshot.

Every actual record's counter keys must equal the caller's exact schema set.
If that set changes from the fixed cf source, the schema must carry an explicit
`reviewed_field_set_revision`: base source commit, new source commit, source-diff
SHA256, exact new counter-fields SHA256 and E_reviewed=true. This is a required
mapping declaration, not proof that E has really reviewed it; the caller must
bind the actual published bytes. A new r2 schema is never guessed or silently
padded from the old172 fields. Extra semantic observability gaps are not solved
by successful arithmetic: mask/merge coverage needs separate E qualification.

The15 source equation families include frontend status/pressure/eligibility/way,
production reach/intermediate, relieve/detach/commit, histograms, first-known
blockers, nonnegative detached population and per-field disjoint phase sum.
Global sum must match each field over exact SLICE0..63; GLOBAL.slice means
owner COUNT64, not a65th slice. PHASE0/1 are unassigned/overlap residual buckets;
PHASE>=2 is one active-kernel interval. These buckets are disjoint observation-time
states, not exact requester/victim attribution or invented physical intervals.
PHASE live_detached and closure/config metadata refer to the parent slice and
must not be summed as phase-local populations.

New detach_success must equal the authoritative old RO SUMMARY detached count
for every slice. Epoch closure, zero live-detached and ordinary source closure
are checked independently of the producer's closure_ok flag. Counts in returned
sectors, waiter responses, transitions, repeated head cycles and unique requests
are not equated. Samples are capped64, immediate_commit_result=-1 means unlinked
UNKNOWN, and sample drops leave counters intact. Samples are not denominators.

Derived checks are explicitly labeled: global sum, sample accounting, new/old
counter reconciliation and metadata population calculation. No independent
full-application acceptance is granted. Caller still runs its original native
exit, full input/instructions, ROC1/FT/resource drain and identity validator.
Returned status is only VALID_OBSERVER_TERMINAL_DECLARATIONS_ONLY (or
SYNTHETIC_OBSERVER_CONTROL_ONLY for the fixture suite), never CURRENT_ACCEPTED.

The controls cover actual-source zero records, two-slice explicit fixture,
64slice membership, exact fields, uint64/bool, invalid markers, duplicate JSON,
identical/conflicting/tail/regressing snapshots, fake terminal closure, phase
metadata/rollups/kernel catalog/scope, raw FAIL and native not-consulted, old/new
counter mismatch, legitimate multiple waiter responses with detach and denied
trigger, sample drops/caps/UNKNOWN result, bounds and explicit r2 field revision.
All data are SYNTHETIC. No native/build/application/controller was executed.
