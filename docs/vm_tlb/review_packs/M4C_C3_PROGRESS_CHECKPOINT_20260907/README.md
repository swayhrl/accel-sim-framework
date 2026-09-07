# M4C C3 nonterminal progress checkpoint

Status: **C3_FINAL_STATUS = NOT_YET_TERMINAL**

This independent review checkpoint records the immutable evidence available at
checkpoint creation. Seven C3 arms satisfy the three-part terminal gate:
`simulator_exit_status=0`, started-kernel (`Processing kernel`) markers equal
the immutable list count, and telemetry-kernel records equal that same count.
`prefill-paper` is explicitly `RUNNING`; its counters in this package are
liveness evidence, not a performance result.

No simulator was launched, restarted, paused, reprioritized, or rebuilt. No
C4 export was started. Raw logs and traces are excluded; their identities are
bound by hashes and relative paths in `INPUT_PROVENANCE.tsv`.

Read `FINAL_PROGRESS_REPORT.md` first, then `C3_ARM_STATUS_MATRIX.tsv`,
`ACTIVE_ARM_LIVENESS.tsv`, and `INTERIM_OBSERVATIONS.md`.
