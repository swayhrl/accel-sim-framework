# M5.0BT T2 — BICG trace replay qualification

Status: **POST_REPAIR PASS**. This pack qualifies one immutable BICG NVBit-v1.8
payload for the frozen 80-SM / cap-10240 / ratio-zero formal platform under
the active lower-create-queue-repair Core. It is a qualification result, not a
Paper performance registry row.

The same immutable trace bundle was consumed under Base, IO and OO. Each mode
naturally terminated, strict-parsed, and showed no fatal, assertion, deadlock,
trace-corruption, missing-address/opcode or output-mismatch signature.

The former pre-repair T2 is preserved as a diagnostic anchor only.  The Core
repair invalidated it for formal qualification.  This pack now binds a fresh
same-bundle Base/IO/OO triplet to Core `15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`,
Framework runtime `dc7836c484544b78d143837bbbb40ecbabb15aee`, and binary SHA
`3e71cb73e7769be43fc4e7c95c59dba6d50540e3827a38a46e4016cb2877dc27`.
No artifact is relabelled across the repair boundary.

See [VALIDATION_SUMMARY.md](VALIDATION_SUMMARY.md) and
[MANIFEST.json](MANIFEST.json).
