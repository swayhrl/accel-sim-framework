# LateBind-L2 Phase 1/2 directed regression

The regression uses compact traces with deterministic addresses and checks
event digests in addition to end-of-run statistics.

| Case | Required observation |
| --- | --- |
| same-line read burst | one lower read, one MSHR entry, remaining accesses merged |
| all-way reserved set | baseline reservation failure and shadow oracle opportunity count |
| dirty eviction under full WBQ | baseline stall, then precisely one dirty writeback; ideal-WB suppresses only that backpressure |
| fill-victim conflict | delayed-victim record persists until fill and selects one victim at fill |
| partial-sector accesses | sector masks and residency account independently; no false full-line hit |
| read/write ordering to one line | no duplicate transient ownership and correct baseline reply ordering |
| MSHR pressure | finite baseline blocks at configured bound; infinite-MSHR does not, while all other limits remain |
| transient-budget exhaustion | equal-capacity and sector modes block before accepting an uncreditable record |

Every case runs baseline stats off, baseline stats on, and every applicable
oracle.  The first two must have the same event digest.  Oracle runs validate
their explicitly changed behavior and the common safety invariants; they do
not compare timing to baseline as an equivalence criterion.
