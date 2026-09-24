# AWMA cross-context capture readiness audit 109 V1

Status: COMPLETE — read-only readiness audit; STOP.

The catalog supplies a future Lane D meta-suite with an exact, capture-ready selector identity for every observed unique `(scenario, phase, decode step, exact function, grid, block)` key in T256, T8192, B4, and D128. Each record identifies the first global launch index, occurrence count at that selector, token/input authority, model revision, and exact captured-driver SHA-256.

No producer, GPU lock, GPU workload, capture, NCU, NVBit, or NSYS command was run.

## Disposition

- `T256`, `T8192`, `B4`, and `D128`: `CAPTURE_READY`. They have read-only recovered global launch indices plus bound model, input, and driver identities.
- `S2_BASELINE`: `SELECTOR_IDENTITY_BLOCKED`. Its accepted compact structural catalog has exact function/shape strata but not the historical per-launch global-index ledger or driver hash. The audit did not fabricate either identity.
- `REUSABLE_EXISTING`: none. A read-only node164 search under `/data`, `/root/share`, and `/home` found no matching simulator-native traceg file for these scenario identities.
- `INPUT_AUTHORITY_BLOCKED`: none of the four executed controls. The prospective same-length different-content T2048 TEXT control remains blocked: no second legal frozen T2048 TEXT input was found. Existing CODE and STRUCTURED T2048 payloads were not substituted.

## NVBit1771 producer compatibility

The mature NVBit1771 simulator-native producer is selector-compatible in principle only when a target is bound exactly by global launch index together with phase, grid, and block (and its input/driver authority). The four new scenario catalogs meet that prerequisite. S2 does not, so it must remain blocked until its historical per-launch ledger is recovered or a separately authorized exact identity source is accepted.

The catalog is a readiness artifact, not capture authorization. Lane D must choose targets and authorize any future producer run explicitly.
