# Finite4 repair completion adopter — metadata only

The R14 parent retired while preserving its scientific frontends/models. Its
ordinary repair runs can subsequently record true DONE/execution_receipt but
have no surviving parent finish_evidence caller. The unchanged V2 consumer
correctly waits for the canonical RESULT and does not independently archive an
ordinary point without it. This package repairs that metadata-completion gap
using the already-published original function, without changing V1/V2 sources.

The exact finite allowlist is old-R1 myocyte977e34578994c3d2 CH/DM and
hybridsort09f94fcc7494a03b DM/DH, with immutable four UUID/spec/INTENT/launch/PID
bindings. No new scientific request, cohort or budget is created. The wrapper
never calls run_cell, experiment, prepare, run_native, a signal or an authority
writer. Binding deliberately does not pin mutable future DONE/result state.

For each point it freshly requires the true recorded DONE == registered
execution_receipt == NATIVE_EXIT, matching UUID/output/spec/INTENT and genuine
native wait evidence. Native rc must be0, stop_reason null and model observed.
The model's recorded PID/start generation must be gone, and the strace launcher
PID must be entirely absent because its start_ticks was never captured. No PID
snapshot or p.wait result is synthesized. Missing receipt/live processes wait;
negative/native failure or conflicting source/evidence fails closed for review.

Under the EXACT same per-point METADATA_CONSUMER.lock used by the active V2
consumer, the wrapper invokes ONLY frozen repair_ops_v1.finish_evidence. That
actual function reruns the unchanged original strict_v1 whole-population,
270-option/source/runtime/identity/raw/progress/BA checks, writes its original
proof/qualification, then uses the standard outbox COPY164/native restore and
creates the previously missing canonical RESULT. This is an actual current
metadata completion, not an assertion that retired R14 executed the call.
A separate adoption receipt states the executor explicitly. No existing RESULT,
INTENT, DONE, wait status, raw/source or spent ledger is replaced or refunded.

The shared V2 lock covers the entire finish call, preventing V2 from reading a
partially created RESULT. The outer wrapper must NOT hold CLOSED_COPY.lock:
outbox.archive acquires it itself. Existing completed RESULT/archive evidence
is independently verified without another COPY. An archive with absent RESULT
is usable only when the exact original proof and seven-field qualification
already exist; the frozen finish then verifies them and creates only the absent
RESULT, without appending archived out. Missing/conflicting proof fails closed.

Qualification passed26 fakeRoot/AST cases, including the ACTUAL frozen finish
body with private strict/outbox dependencies, no-model API audit, all identity/
receipt/rc/live-process negatives, full-strict failure propagation, V2 lock
contention, malformed/conflicting RESULT, archive-without-proof rejection and
idempotent exact existing archive handling. Independent review passed22 guard
cases on the final wrapper. The two real myocyte runs independently passed
unchanged registered strict_v1 full replay (93s/154s), while out inventories,
canonical RESULT/qualification/archive and consumed rows stayed exact. Real
hybrid gates were refreshed; any new DONE follows the same gate and must pass
the actual complete strict before archive. Natural exit alone is not PASS.

Execution is separate: root first publishes this exact package and verifies
every GitHub blob/source-copy join, then writes
ops/REPAIR_COMPLETION_ADOPTER_PUBLICATION_READBACK_V1.json with verified, commit,
tool_sha256, qualification_sha256 and binding_sha256. Command:
python3 -B <FIX>/ops/repair_completion_adopter_v1.py --execute
No --execute is read-only; --full-review additionally replays complete strict.
The finite waiter is singleton/sequential (metadata-memory friendly), polls10s,
ends after four verified completions, and never retries an unexpected exception.
The existing V2 consumer remains running and owns its independent23-point
closure/authorized metadata-floor update. No R16 parent or model is restarted.

No actual archive/COPY or consumer execution occurred in this preparation.
The source/CPU/binding/read-only evidence is final; the earlier unpublished
binding draft was retained under its native preimage filename after adapting
the independent review's schema and is not the current execution binding.
This package grants no accepted performance cycles, no original-matrix receipt
fabrication and no paper promotion. Englishv0.23 remains the confirmed master.
