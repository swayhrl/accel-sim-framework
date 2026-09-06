# M5.0BT — repaired-Core SpMV precomputed trace triplet

Status: **PRECOMPUTED_SAME_BUNDLE_TRIPLET_STRICT_PASS — NOT A STAGE PASS**.

This pack preserves an exact, repaired-Core SpMV Base/IO/OO trace replay that
was acquired under the authorized capture/replay pipeline.  It is deliberately
separate from the BICG T2 qualification pack: this observation neither closes
T3/T4 nor advances M5.0BT/M5.0C, and it is not registered as a formal Paper
performance result.

All three rows use the one immutable NVBit-v1.8 SpMV bundle, Core
`15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`, Framework runtime
`dc7836c484544b78d143837bbbb40ecbabb15aee`, binary SHA-256
`3e71cb73e7769be43fc4e7c95c59dba6d50540e3827a38a46e4016cb2877dc27`, and
the frozen 80-SM/cap-10240/ratio-zero configuration family.  The original
hardware capture/checker and immutable-receipt evidence remains in
`m5/handoffs/M5_0BT_SPMV_CAPTURE_CLOSEOUT.md`.

See [VALIDATION_SUMMARY.md](VALIDATION_SUMMARY.md) and
[MANIFEST.json](MANIFEST.json).  Raw logs, trace bundles, binaries and local
strict summaries remain outside Git; their identities and SHA-256 values are
recorded here so the pack is reviewable without copying large artifacts.
