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

## Current formal Core/runtime authority

`15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9` remains the mechanism-behavior
source anchor.  `bbcbb5e7565417102087bc80b14c349b4e568c05` and runtime
`6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041` remain
the historical FAST64 telemetry identity; their existing immutable evidence
retains those literal values.

For every **new non-2DConvolution** FAST64 formal row after the zero-access
repair qualification, the required Core/runtime identity is Core
`95ccdb7a056f2d53f740d90869785cac6d4ee0f5` and trace-enabled Release runtime
SHA-256 `462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9`.
The change only excludes an empty access queue from the IO/OO DTC issue-side
path; the nonempty assertion remains.  The common repaired-Core Hotspot1
Base/IO/OO triplet strict-validates, and its Base row is exact against the
historical bbcbb Base on cycles, instructions, PIB/lower lifecycle and final
state.  The authoritative old-to-new classification is
`handoffs/FAST64_ZERO_ACCESS_CORE_REPAIR_IDENTITY_MAP.md`.

The only current exception is the repaired 2DConvolution common triplet and
its cap controls/reacquisition: Core
`6587238c60214d99491f4048e28ce8a3458c1509`, runtime SHA-256
`29a3dd9f57a5accb89822ca3fcf06b11c437bfe864ee43d2ff5f26c8c056f3c1`.  Its
source-backed scope is fixed by
`handoffs/FAST64_2D_TAG_IDENTITY_CORE_AUTHORITY_MAP.md`; it is not a global
replacement for Core95 and cannot be mixed with Core95 in a 2D triplet.

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

The zero-access repair map is that required Core-transition map. A bbcbb row
must retain its bbcbb identity and may be reused only under the map's explicit
source-inert/unreachable classification and any required differential. It must
never be relabelled as `95ccdb7a`.

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
