# Candidate existing-path clarification

Status: **PASS for source inspection; Candidate2 DOWNGRADED / NOT_QUALIFIED.** This addendum supersedes only the proposal of adding a per-head Victim lookup token in `WV_NEXT_ARCHITECTURE_CANDIDATES.md`. The original report and manifest are retained unchanged as an audit trail. No Source, CPU protocol, NI or application execution was performed for this clarification.

## Existing production implementation

Agent D flagged an existing implementation path; Agent C independently read accepted Source78 `ep-l2-tvd-cache.inc:81-95`.

- A changed `m_tvd_lookup != mf` head stores `mf`, records the lookup cycle, resets `m_tvd_lookup_done=false`, and charges lookup waiting.
- The same head cannot finish in its arrival cycle (`now <= m_tvd_lookup_cycle`).
- Only `!m_tvd_lookup_done` checks the existing per-cycle query-port guard, increments `m_tvd_lookup_queries`, performs `m_tvd->find(address)`, saves `m_tvd_lookup_ticket`, and sets `m_tvd_lookup_done=true`.
- Subsequent callbacks reuse the stored ticket and check `m_tvd->live(ticket)`; they do not unconditionally perform another find or increment the query count.

**PROVEN from source:** a same-head token/ticket and lookup-result reuse already exist. Therefore the earlier generic per-head token proposal is not a new optimization and must not be implemented or described as missing functionality. Repeated callback observations alone cannot establish repeated physical directory queries. No P0/P1 defect follows from the high cumulative Victim-lookup wait or query counters.

The stored ticket still passes current liveness/state checks. This bounded source inspection does not independently certify every concurrent mutation case or replace Agent D's correctness review. It also does not measure a new performance contribution.

## Remaining candidate, with explicit prerequisites

Only work beyond existing token reuse remains hypothetical: a finite conservative negative-query filter for **actual distinct paid queries** that the existing token does not already eliminate. It should remain lower priority unless existing or separately qualified passive evidence establishes that population by request kind, query outcome, distinct head identity and actual physical query issuance. An observer head-cycle count is not that denominator; query minus service-response count is not an exact negative-query count because operations and service populations differ.

Any future filter would require explicit bits, lookup/update ports, pipeline latency, false-positive behavior, no-false-negative proof, invalidation/version rules, mutation/liveness checks and its own mode-specific NI/Source qualification. No free associative search, bypass of same-address ordering or removal of the paid directory port is authorized. No implementation or new collection is prepared here.

## Priority after this check

The conditional optional-V service-aware-reclaim design remains the first architecture candidate because accepted W/WV contrasts establish real V service and a package-level benefit, while Stencil/Scan offer contrasting retention usefulness. It is still HYPOTHESIS / NOT_QUALIFIED, not a known repair or promised speedup. Require the accepted Stencil result and Main's independent design review before deciding whether reclaim is the remaining causal question. Keep all mandatory/readers/pin/generation/WB/bank-color protections and declared finite selection costs.

No additional GPU starts, CPU tests, Source edits, budget/ledger writes, policy merges or controller changes occurred. The original seven-file delivery and its original manifest remain intact; the new additive manifest binds both the old delivery and this correction.
