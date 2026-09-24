# C16 E1 Oracle Elastic Residency Semantic Addendum Closure

The authorized addendum redefines a target tag as eligibility to request protected admission. It preserves baseline invalid priority and set-local replacement when hard quota prevents protection.

Case C admits into the baseline invalid line as unprotected and records `QUOTA_FULL_BASELINE_INVALID_PRIORITY`. Case D selects the baseline set-local ordinary victim as unprotected and records `QUOTA_FULL_NO_LOCAL_PROTECTED_VICTIM`. Neither creates a pending reservation. Hits never promote these lines and their later eviction cannot decrement protected occupancy.

The repaired Core passes build, all addendum corners, 22 invariants, baseline-OFF neutrality, diagnostic neutrality and existing regressions. This closes implementation/synthetic correctness only. Bounded-trace namespace admission remains required before real C16 replay.
