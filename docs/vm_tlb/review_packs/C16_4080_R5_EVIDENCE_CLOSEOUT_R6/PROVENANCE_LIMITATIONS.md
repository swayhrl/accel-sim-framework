# Repository provenance limitations

R5 scientific artifacts remain accepted and hash-closed. R6/R6.1 re-hashed the existing artifacts without rerunning any scientific workload.

Two non-blocking repository replay-transcript limitations remain and are intentionally recorded rather than reconstructed:

1. **U7 NCU command transcript** — the committed sources do not contain a byte-for-byte exact R5 U7 argv vector, a standalone metric-manifest file/hash, or a standalone R5 target-contract receipt/hash.
2. **U9 arm receipt** — the committed sources do not contain a separately recoverable R5 arm/target-binding receipt path+SHA.

These are documentation completeness limits only. They do not change the accepted R5 artifact hashes, the frozen model/input identity, the fixed `indexSelectLargeIndex / static 101 / LDG.E.U16` canary identity, or the `READY_FOR_MULTIMODEL_REVIEW` status.

Do not invent or post-hoc reconstruct the missing command/receipt identities. If exact command replay is required in a future stage, freeze those fields prospectively before the next capture.
