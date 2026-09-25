# Pre-L1 coalescer versus conventional translation MSHR

Source semantics place the conventional translation MSHR after an admitted L1
lookup, an L1 miss and an L2 miss/handoff. A larger MSHR can hold more miss-side
waiters, but it cannot undo the L1 lookup bandwidth already consumed by an
L1-hit duplicate or by a duplicate that reaches L2 before merging.

The frozen pre-L1 coalescer compares the exact identity before the L1 port.
Its follower waits on the leader's complete translation result, whereas an
MSHR waiter is registered only on a miss-side page-walk entry. These waiter
semantics and service locations are different.

`PREL1_VS_MSHR_MATRIX.tsv` shows that existing MSHR merges are a small fraction
of baseline L1 launches while pre-L1 followers are often tens of percent or
more. Candidate leader-source counts are dominated by L1 hits on the high-
redundancy targets. Therefore simply enlarging the existing MSHR does not cover
the measured L1-hit duplicate population. No unmeasured larger-MSHR performance
claim is made.
