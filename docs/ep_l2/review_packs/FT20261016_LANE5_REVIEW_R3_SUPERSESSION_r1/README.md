# review_r3 scientific supersession enforcement

62 actual runner/registry/schema/consumer tests PASS, not simulator qualification.
Six retained actual R0 runs were additionally checked through the live canonical
authority: runner input with the historical immutable INDEPENDENTLY_QUALIFIED
certificate and formal result intake both reject each run as withdrawn. Old
COMPLETE_VALID states, raw/config/CSV/binary content remain unchanged. Binary
and raw hashes plus six configuration snapshots independently rechecked.

V2 authority preserves ten old identities, including all feature/ideal/epoch/
termination fields and original keys. It explicitly withdraws R0/R1 Core/binary
identities and grants no current launch or result acceptance. CURRENT_ACCEPTED
is mandatory for results; launch qualification is a distinct state. New results
must use separately qualified new identities. A newer withdrawal wins even if
an older accepted row or certificate survives. Missing/stale authority, changed
proof, mismatched identity/metrics/raw or duplicate rows fail closed.

Local runner reads the current shared pointer plus exact manifest/proof hashes.
Off-host/paper consumers use acceptance.fetch_current_authority(repo), which
performs a bounded read-only GitHub branch fetch and binds exact publication
SHA, manifest bytes and supersession proof. Do not call a cached prior snapshot
current, and do not use bind_manifest directly as a freshness bypass.
