# RO candidate and lifetime semantics

All completed RO-focus rows are `UNCERTIFIED_CANDIDATE_ONLY`.  The producer
excludes writes, atomics, and writebacks with explicit counters; it labels the
remaining ordinary tracked request only `candidate_uncertified`.  No source
predicate currently establishes alias, ordering, or write-policy safety, so
there are zero source-proven `SAFE_RO_ELIGIBLE` observations.

The CSV gives distributions as `(count, sum cycles)`.  First-lower-issue,
first-fill, and all-ready are measured against the epoch-safe allocation.  A
zero first-issue sum means the native lower-issue handoff was observed in the
same cycle as allocation for that population; it does not mean the later
pending state is safely removable.  Final-retirement, last-issue, and tail
milestones are `NOT_EMITTED` because no exact one-shot instance terminal event
is exposed.
