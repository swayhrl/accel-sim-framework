# Phase A/B decision

Status: **PREL1_COALESCING_OPPORTUNITY_SUPPORTED**

The exact finite observer records 9,409,101 legal merges out
of 11,741,022 admitted physical L1 lookup
launches (80.139%). Existing accepted MSHR behavior overlaps
22,826; the remaining
9,386,275 opportunities are
incremental pre-L1 request/probe eliminations.

Only 1,187 of 9,960,255 raw duplicate pairs
(0.011917%) have a leader that completes later than the
follower's baseline completion. Opportunity is therefore neither dominated by
post-completion repeats nor by slower leaders.

Capacity **2 entries per SID** is selected by the preregistered rule:
it is the smallest member of 1/2/4/8 with an exactly equal merge-opportunity
count to capacity 8 on every development target. Matching capacities:
`[2, 4, 8]`. No performance data was used.
