# C16 G2 NCU capability-limited closeout

The C-fixed Selector-R/B48 NCU plan was consumed unchanged from C commit
`d55075b7752380d6bd22328547db21a5e24eeed2`.  The sole first-row canary was
the P3 AWQ S1/CODE/DECODE source unit, structurally constrained to its exact
demangled name, source same-name invocation 4284, grid `7x1x1`, and block
`128x1x1`.  Kernel-name-only, nearest, and adjacent substitution were never
allowed.

The final canary executed under root with NCU 2024.1.1 and the committed
five-metric compact set, but NCU reported `ERR_NVGPUCTRPERM`.  It produced no
`.ncu-rep` and therefore cannot prove a unique actual structural reproduction.
Its target identity status is consequently
`TARGET_IDENTITY_NOT_REPRODUCIBLE`, caused by counter permission rather than
by a guessed mismatch.  G2 is
`G2_NCU_CAPABILITY_LIMITED_PERF_COUNTER_PERMISSION`.  The actual canary is
retained as attempted/no-report and each remaining one of the 287 C-fixed NCU
rows is `NOT_EXECUTED_CAPABILITY_LIMITED`.  No further NCU target was selected.

The two prior zero-output CLI diagnostics and the final failed canary are all
retained as `NON_SCIENTIFIC_DIAGNOSTIC` ledger evidence.  The final child
native receipt is retained only to show the frozen package/input/runtime path
was reached; it is not a baseline, census, or NCU-counter result.  The 20
small retained receipt/log files were returned and independently matched by
remote/local size and SHA256.  There is no NCU raw profile and no
remote-only required artifact.  See
[G2_NCU_CAPABILITY_LIMITED_RECEIPT.json](G2_NCU_CAPABILITY_LIMITED_RECEIPT.json)
and [G2_NCU_DIAGNOSTIC_ARTIFACT_INDEX.tsv](G2_NCU_DIAGNOSTIC_ARTIFACT_INDEX.tsv).
