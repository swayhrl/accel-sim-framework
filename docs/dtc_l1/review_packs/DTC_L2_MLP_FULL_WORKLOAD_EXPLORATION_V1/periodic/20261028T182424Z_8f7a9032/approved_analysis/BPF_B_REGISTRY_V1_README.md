# Exact-four engineering registration candidate

Frozen implementation: `engineering_registry.py`. This package has not been
applied to production. The 18 CPU checks use the real immutable Main plan,
exclusion contract, corrected CanaryScope, accepted reference RESULT bytes,
reference cycles and science projections. Authority is an isolated deep copy;
the production native `update_authority` was never called. QA/readback documents
inside CPU fixtures are explicitly marked stand-ins, not actual deployment or
publication evidence. No model is started by this class.

## Main-only API

`EngineeringCanaryRegistry(root, engine, scheduler_frame, configuration,
fault_hook=None)` obtains the actual aging owner lock from the given frame.
Production calls require the actual scheduler frame, same engine, actual owner
PID/start from the execution plan, original native source and update_authority
function, main thread, and valid original parent lease. No extra controller,
thread, polling loop, or automatic recovery runs.

Main creates a real source/QA/readback configuration matching
`CONFIGURATION_SCHEMA.json`, then uses:

```
store = EngineeringCanaryRegistry(R, frame.f_locals['engine'], frame, cfg)
authorization = store.expected_authorization()
# Main reviews/records this exact authorization for this transaction.
store.prepare(authorization)    # PREPARED only; no spec or authority grant
store.register(authorization)   # explicit forward registration
store.reconcile()              # witnesses closure; never grants
```

The expected authorization fixes transaction ID, owner generation, exact four
additional technical starts, zero refunds, engineering role, no primary change,
and no validated union. It is not inferred from an exclusion contract. The
registry constructor and imports are inert. Call `register` again only for
Main's deliberate forward recovery; it cannot grant twice.

QA must be an actual Main combined record with status PASS, exact five
qualified source hashes, expected old-source pins, and the three boolean
native-prefix/extra-strict/consumer-archive qualification flags. Readback must
be real `verified=True` with exactly those source/pin sets and QA SHA. There is
no Git, HTTPS, or publication-transport requirement in the implementation;
Main may use honest byte readback from the new native directory and 164.
CPU fixture stand-ins must not be passed as real Main deployment evidence.

The entry delivery SHA `2ffae93a...` fixes the final five-source set and minimum
complete old-source pins. Main may add extra pins. Deployed source paths can
differ from archive paths while their exact bytes and qualified hashes match.

## Transaction and recovery

Records live under `R/control/bpf_engineering_registration_v1/transactions/`.
The deterministic transaction ID binds the complete configuration. PREPARED
contains the four complete initial specs, initial SHA set, authorization,
pre-existing consumed UUID witnesses, and primary matrix/scope SHA.

Each canonical `control/specs/<C>.json` and alias `control/<C>_SPEC.json` is
published atomically with fsync/link/no replacement. One call to the original
native `update_authority` appends all four admitted specs, admitted-input spec
memberships, four `authorized_engineering_observation_canaries` records, one
batch witness, and exactly +4 budget/remaining. A callback allowlist equality
check proves peers, old consumed records, old source/history, old input data,
and all unrelated registry fields are preserved.

No UUID is manufactured at registration. The native launcher later consumes
each independent identity once and chooses a fresh UUID. No old identity is
reused, reset, refunded, replaced, or included in primary statistics.

COMMITTED is immutable. A crash before authority can be explicitly continued
from the same PREPARED and identical partial spec publication. A crash after
the atomic grant is reconciled from all four records without a second grant.
Partial authority, a COMMITTED witness whose authority disappeared, unknown
ownership, conflicting specs, corrupt PREPARED, or changed source/reference
evidence cause HOLD. The class never erases evidence or repairs partial grants.

After a legitimate official RAM/VMS resource refresh, reconciliation verifies
current q-admitted canonical SHA, canonical host_cpu=None, fixed science
projection and full engineering lineage through real `CanaryScope.validate`.
It does not require the refreshed spec to retain the original DRAFT SHA.
CPU remains solely in independent dispatch binding/resolved spec. Initial
grant SHA is preserved as provenance. Future legitimate primary extensions
are not mistaken for writes performed by this transaction; canaries remain
excluded from current MATRIX and SCOPE.

This package does not append CPU2 allowed scope, install the new entry,
construct a dispatch view, bypass aging/resource gates, or enqueue canaries.
Those are separate qualified Main operations. Paired actual activation,
original physics plus CPU2/IO/new strict, natural lifecycle, genuine 164 archive
and native2128 restoration remain required canary acceptance gates.
