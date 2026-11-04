# Root report-only publication service

This CPU service consumes the independently reviewed closed-result consumer and publishes only the independent exploration branch every30minutes or when scientific result states change. It does not register a science request, dispatch or stop a simulator, change owner/lease, reuse UUIDs/budgets, or mutate any Goal. It runs at lower CPU priority (nice+10). SourceSHA/configuration and its actual PID generation are recorded here.

Frozen source packages are copied byte-for-byte with manifest SHA verification; changing snapshots are stored in immutable timestamped directories. Git stages only the exploration review directory and never force-pushes. A transient push failure retries the same already-committed publication; unknown worktree writes conservatively stop publication until Root reconciliation. Scientific execution continues independently.

Candidate plans, running points, accepted, archived negative, missing and Tag safety-HOLD remain distinct. Available-subset GM is descriptive; direct variant comparison requires a common accepted input set. This service cannot approve a new science scope, modify the manuscript, complete the paused old UI Goal or grant Root's final scientific signoff.
