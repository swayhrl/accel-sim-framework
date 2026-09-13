# G3 NVBit capability-limited closeout

`G3_CAPABILITY_LIMITED` is the terminal result for the frozen C B48 NVBit
plan.  It does not alter the standalone baseline/census path, C selector, or
any frozen scenario.

NVBit 1.7.6 was hash-closed, built once for CUDA 12.4 / sm_86, and passed a
tiny vector-add diagnostic: injected instructions, `EXIT`, `ffffffff` active
masks, 4-byte global `LDG.E`/`STG.E`, postprocessing, and the 4 GiB / 20-minute
window were all directly observed.  That fixture is diagnostic-only and is not
a model trace or a timing result.

The first file-order C row was then bound without selection freedom to the P3
AWQ S1/DECODE composite source key.  The source catalog match was unique and
the attempted model trace used the frozen global ordinal plus an
implementation-family guard; post-trace validation would still have required
the exact full kernel name and 7x1x1 / 128x1x1 geometry.  No name-only,
nearest, or adjacent-launch matching was permitted.

The model process aborted with `SIGABRT` before its child runner emitted a
preflight receipt and before NVBit emitted a raw trace.  The wrapper-owned
single budget lease, token-bound parent receipt, active-measurement marker, and
non-scientific diagnostic ledger row all closed correctly.  Therefore the
target cannot be asserted reproducible, and repeating other rows would not
provide a scientific target result.  The attempted row is retained as
`ATTEMPTED_CAPABILITY_LIMITED_NO_MODEL_NVBIT_TRACE`; all other frozen rows are
`NOT_EXECUTED_CAPABILITY_LIMITED`.

The exact external files and dual-endpoint hashes are in
`G3_NVBIT_DIAGNOSTIC_ARTIFACT_INDEX.tsv`; no raw artifact is committed to Git.
There is no real model NVBit canary for Lane H.
