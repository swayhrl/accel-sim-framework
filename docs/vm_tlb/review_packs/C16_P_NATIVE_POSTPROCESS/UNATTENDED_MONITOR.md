# C16-P unattended event monitor

The local monitor runs for a bounded eight-hour window with a 180-second poll
interval. While G's remote head is unchanged, it performs only `git ls-remote`.
After a changed head it fetches that exact commit, then—and only then—reads
`LATEST_RUNTIME_STATUS.md`, changed semantic publish manifests, and changed
P1/P3 manifest/receipt/index candidates.

Its Git-external state and head-audit ledger live under
`artifacts/c16_p_native_postprocess/unattended/`. A quiet interval writes no
Git evidence and causes no commit. A new hash-closed event is recorded with its
exact G commit and manifest SHA; the appropriate P1/P2/P3 handler must prove
its complete contract before running export/postprocess and making a P commit.

`BLOCKED` and `SKIPPED_RESOURCE` declarations are ledgered only when a changed,
structured receipt binds the terminal status to an exact deployment ID. Historical
or instructional wording in the aggregate runtime-status Markdown cannot mark an
unrelated event skipped. A scoped terminal event is skipped without ending the
monitor or suppressing other deployments.
The monitor never runs a GPU workload and never modifies G, A, C, or H worktrees.
