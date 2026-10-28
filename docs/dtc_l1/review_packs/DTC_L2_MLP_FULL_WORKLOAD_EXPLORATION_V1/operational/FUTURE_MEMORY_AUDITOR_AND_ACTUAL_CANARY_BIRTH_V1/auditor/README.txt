Future-memory actual canary rollout auditor (read-only)

This is a new tool, not the old exact-two-additional-field IO auditor. It never
installs an owner wrapper, changes admission, restarts or signals a model.

API: audit_canary(cohort, expectations, root=R, _ops=None). The actual cohort is
fixed to E2-DTCL2MLP-2b93f70cd0666c51-DH-Q64-V1. CLI accepts that cohort and an
expectations JSON path. It returns evidence only. Success status is exactly
PASS_FUTURE_MEMORY_CANARY_ROLLOUT_READONLY_REPLAY, backend ACTUAL_READONLY and
production_release_eligible=true. CPU callbacks always produce backend CPU_FIXTURE
and production_release_eligible=false. Missing UUID/identity not born returns
PENDING_NOT_BORN_OR_EXPECTATIONS_UNSEALED. Missing closure, unknown proof fields,
failed source/identity/math/strict/archive checks return HOLD, never a weak PASS.

The read-only audit hook and exact findmnt whitelist are AST-identical to the
previous 4d5 auditor. All write opens, filesystem mutation, process signals and
unapproved subprocesses are blocked inside the audit. The only approved child is
exact source-pinned sweep_native.check_input -> /usr/bin/findmnt -J -T exact trace
entry, with pinned findmnt bytes. Import bytecode writes are disabled. The hook
is thread-local and does not interfere with healthy simulation threads.

Acceptance requires: current source/route pins; exact original performance strict
replay with no differences except the explicitly named new extras; qualified
MEM extra_strict source78abb... replay (which performs versioned joint padding/IO
rather than claiming an old B5 PASS); matching memory, IO and optional padding
bindings across INTENT/LAUNCH/PID; source/config/QA/readback snapshots; exact new
sidecar bodies and SHA links; RESULT cycles equal replayed base cycles; natural
DONE==NATIVE_EXIT==q execution_receipt; exact UUID/INTENT/current canonical/CPU
binding; actual outbox.verify equal RESULT archive with verified 164 archive and
native-2128 restore; final unchanged source/row recheck.

Priority reservation evidence is sealed from Main's actual owner returned map,
not guessed by mtime. Both immutable RESERVED and CPU_RETURNED SHA are fixed in
expectations, with source/QA/readback/operational authority joins. Full recorded
pre-admission memory math is replayed. A live model is not counted as a new
candidate again: the token's original pre-admission snapshots are consumed.
Its pre-refresh canonical SHA traverses every resource-history amendment and
old preimage to final q/spec/INTENT/dispatch identity. Only estimated RAM,
RSS cap and VMS cap may differ; all other scientific/limit fields are exact.
A zero-length bridge is legitimate when no resource refresh occurred.

Qualification is 14 focused CPU checks with explicit mocked performance strict,
joint terminal, authority and archive callbacks; memory arithmetic uses the
actual pinned library with fictional 1TiB headroom. This does not prove a real
simulation or archive. Separately, actual original strict and actual archive
verification on already-complete mergeSortF256 passed while the real write
barrier was enabled. The new scalar canary remains independently unaccepted
until its own natural DONE/RESULT/archive and the entire actual audit pass.

Actual birth evidence/expectations live under actual_expectations/ and have a
separate UUID from CPU fixtures: 12dc9aae-cbec-40fe-90d8-bd23f92306de. Expected
PID/start was2057286/989805493. The sealed expectations file fixes the actual
three memory bindings/snapshot and Main's unique attempt07f12... bytes. Captured
precompletion lease bridge has zero amendments; this is only partial identity
evidence and explicitly not a rollout PASS. QUALIFICATION.json says the same.

All outputs are written only after the audit barrier returns, into this B
artifact directory. Existing model/INTENT/receipt/source files are never edited.
