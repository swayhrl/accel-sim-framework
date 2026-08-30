# Preliminary RO Classification

M0b never treats `!is_write()` as proof of read-only safety.  The smoke's
`ro_candidate_uncertified` denominator requires non-write, non-atomic,
non-writeback demand traffic and remains explicitly **uncertified**.  Separate
exclusion counters exist for write, atomic, and writeback traffic.  No source
predicate proves that any surviving request may release Line-MSHR state early.

This preliminary output may identify candidate transferable pending-state
lifetime only; it does not establish an RO mechanism benefit.
