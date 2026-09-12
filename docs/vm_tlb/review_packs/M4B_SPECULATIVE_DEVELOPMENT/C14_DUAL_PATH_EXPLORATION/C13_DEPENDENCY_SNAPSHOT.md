# C13 dependency snapshot

Snapshot points: common-source-audit fetch and post-P/N-instrumentation fetch.
Both resolved `origin/hrl/vm-m4b-c13-diagnostics-v0` to
`889704ff6e8e7ed52c8aad8c5f414bc9fd743af3`.

Status at the latter read-only snapshot:
`C13_EFFECTIVE_CONFIG_AUDIT_REPAIRED_REPLAYS_IN_PROGRESS`.

- The nine original C13 mode=1 (`SUBENTRY_16`) results are explicitly
  `SUPERSEDED_WRONG_L2_MODE_SUBENTRY16` and are excluded from every C14
  scientific judgment.
- Three repaired Decode rows have terminal/runtime receipts, but all remain
  `PASS_PENDING_EQ_GATE`: `C13-LAT-D11-REPAIRED-EXACTMODE-A1` (34,539,934
  cycles), `C13-SEL-D10-CTRL-NEWBIN-REPAIRED-EXACTMODE-A1` (34,432,059), and
  `C13-SEL-D10-REPAIRED-EXACTMODE-A1` (34,483,640).
- EQ1 then EQ2 had not completed.  Seven repaired arms remained speculative.

Consequences for C14:

1. C14's source-level P `NO_GO_WITH_EVIDENCE` does not depend on C13 timing
   results and is not delayed by the EQ gates.
2. C14 N stays observational.  It is the appropriate next diagnostic only if
   a repaired exact-mode C13 comparison later shows a large counter change
   with unclear cycle exposure; it must not interpret the superseded results.
3. No C13 worktree, branch, output directory, or raw artifact was modified.
