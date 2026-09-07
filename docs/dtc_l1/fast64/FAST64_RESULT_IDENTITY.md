# DTC FAST64 Formal Result Identity

Status: **ACTIVE**

Every FAST64 primary or sensitivity row is keyed by:

`{core_sha, framework_sha, runtime_binary_sha, mode, resolved_config_sha256,
observer_overlay_sha256, execution_payload_kind, workload_id,
workload_input_identity, payload_identity, parser_schema}`

For FAST64 trace replays, `payload_identity` must include:

- exact trace root;
- `kernelslist` and/or `kernelslist.g` SHA-256;
- ordered `.traceg` member list;
- per-member SHA-256;
- aggregate ordered traceg-set hash;
- total trace bytes;
- trace format/frontend identity;
- source C2P paper16 provenance reference.

The provenance label for reused C2P traces is:

`C2P_CANONICAL_TRACE_REUSED_FOR_DTC_FAST64`

It must never be relabelled as a dissertation-exact payload.

## Observer rule

Future not-yet-launched FAST64 triplets use A1:

`-gpgpu_runtime_stat 500000`

observer overlay SHA:

`2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e`

A triplet may not mix observer identities.

## Reuse rule

A completed row may be reused only if every identity field relevant to that
row is identical. A later source/config/parser/Core change must produce an
explicit invalidation map.

Instrumentation-only changes may preserve performance cycles only after an
exact differential proves no timing/dynamic-operation change; newly introduced
scientific counters still require runs that actually produce those counters.

## Raw evidence rule

Raw logs/traces may remain outside Git. Committed compact evidence must bind
each external artifact by:

- path/namespace;
- bytes;
- SHA-256 when practical;
- command/config identity;
- terminal classification.

No row becomes formal merely because a directory name implies completion.
