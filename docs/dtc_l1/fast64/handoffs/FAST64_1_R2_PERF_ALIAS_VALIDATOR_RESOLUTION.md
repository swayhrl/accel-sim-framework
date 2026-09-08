# FAST64 R2 perf alias validator resolution

Status: **FROZEN-CLOSEOUT DEFECT PROVEN; VERSIONED READER PREPARED**

Every currently observed immutable R2 namespace has exactly one timestamped
regular perf stream and a simulator-created symbolic alias:

`perf_counter.csv.gz -> perf_counter_<launch-time>.csv.gz`

The two paths resolve to the same inode. Each observed row has one simulator
initialization marker; the two terminal cohort-1 rows also have one natural
exit marker and immutable exit-0 receipts. Therefore this alias is not a
second execution epoch.

The frozen validator currently counts both glob paths and rejects the alias as
two perf streams. It will deterministically reject the R2 rows if invoked
unchanged. A second frozen-collector defect is also source-proven: the
collector expects `DTC_L1_lower_outstanding_cap` to be parser output, but that
value is a hash-bound config setting, not a terminal summary metric.

No frozen closeout byte was edited. The versioned
`validate_fast64_trace_row_alias_v2.py` verifies the frozen validator SHA,
accepts only one regular timestamped stream plus the exact optional symlink
alias, rejects every other alias/stream topology, and then delegates all other
checks and parsing to the frozen validator/parser. Its F2 NN/IO test passed
receipt, identity, trace-sequence, strict parsing and terminal-accounting
validation after alias normalization.

The active frozen closeout controller remains untouched and authoritative for
its own fail-closed observation. A versioned R2 collector may be used only
after all seven terminal receipts exist and the frozen controller records its
expected collector retry; it must not overwrite the frozen controller marker.
