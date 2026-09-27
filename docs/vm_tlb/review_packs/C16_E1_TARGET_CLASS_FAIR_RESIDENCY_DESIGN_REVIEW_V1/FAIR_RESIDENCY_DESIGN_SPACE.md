# Fair-residency design space

| ID | Design | Fairness | Complexity | New dimension |
|---|---|---|---|---|
| M1 | GLOBAL_ELASTIC_RECENCY | none; a recent class can occupy the whole pool | current baseline | False |
| M1F | GLOBAL_ELASTIC_FRACTIONAL_ADMISSION | statistical/stable opportunity fairness; limits one class injection but does not guarantee an exact occupancy floor | low: one hash/threshold decision on target admission | fractional target admission versus M1 all-target admission |
| M1Q | ELASTIC_PER_CLASS_SOFT_QUOTA | stronger proportional protection than M1F but still constrained by set-local victim availability | moderate: counters, share comparison, class-aware victim filtering | class-aware occupancy/admission/replacement |
| OPTIONAL_NEXT_REUSE | NEXT_REUSE_AWARE_CLASS_SELECTION | not fairness; utility prioritization may intentionally be unequal | high and potentially oracle/future-aware | future/utility prediction |

Recommendation: implement nothing in this Goal. If Lane4 supports realized class churn after admission is healthy, evaluate M1F first. M1F uses a stable class/address hash and the frozen budget fraction to select the protection-eligible subset; all non-selected/failed fills remain ordinary. M1Q is the escalation path when a hard soft-share floor is required. Future-aware selection is intentionally deferred.
