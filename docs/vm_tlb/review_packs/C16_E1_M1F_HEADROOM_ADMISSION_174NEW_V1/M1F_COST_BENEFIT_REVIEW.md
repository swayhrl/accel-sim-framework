# C16 E1 M1F headroom cost/benefit review

Decision: `M1F_FULL_TIMING_NOT_JUSTIFIED_BY_CURRENT_HEADROOM`.

This is a CPU-only admission review. It did not run Accel-Sim, M1F, PRIORITY_STABLE, GPU work, a new observer, or a seed/threshold search.

## Frozen selector and useful-target coverage

The independently recomputed selector covers 130,571 of 7,426,048 total target lines. For class 1 / layer 0 it covers 4,752 of 265,216 unique lines (1.791747104%). The accepted D2 trace has 152,064 selected references out of 8,486,912 target 128-byte line-reference proxies (1.791747104%). The two fractions are exactly equal, so the frozen hash subset is not unusually hot in this target.

All 4,752 D2-selected lines also occur in the D1 L0 up trace, so they have an exact D1 access producer. Existing M1 counters are not selector/address-resolved; address-specific D1 protected-fill status remains UNKNOWN. The isolated M1F activation canary reports 35,241 selected of 1,969,155 modeled L2 target accesses, supporting only, not as continuous-M1 authority.

## Existing Lane4 counter bound

Across the frozen D2 L0 up boundary, M1 records 1,974,966 target accesses, 914,251 hits, 1,060,715 misses, 911,871 protected hits, and 265,216 protected fills. Class-1 occupancy moves from 0 to 131,072. Which stable-selected accesses are current M1 misses is UNKNOWN. An optimistic cross-level bound is `potential_extra_hits <= 152,064`, capped by selected trace references and current non-hit target accesses.

## Headroom

- E0 hard target-zero ceiling: D2 L0 up is 0.955678934% of the R0 measured window. Even zero target cycles cannot improve that window by more than this localized ceiling.
- E1 perfect selected retention: at most 4,752 unique lines / 608,256 bytes (0.580078125 MiB) of unique-line first-need traffic, and at most 152,064 trace line-reference events. This is not a cycle speedup.
- E2 model-based optimistic estimate: under a fully linear qweight-service model, local time reduction is 1.791747104%, local speedup is 1.824436390%, and the modeled whole-window response is 0.017123350%. This is `MODEL_BASED_OPTIMISTIC_ESTIMATE`, not a cycle upper bound.

## Resource judgment

The direct useful-target coverage is about 1.8%, with no dynamic heat enrichment. The optimistic linear whole-window estimate is about 0.017%, while the prior cost is roughly 78 hours for primary and 88 hours for diagnostic. No new paper materiality threshold is introduced; these exact coverage, ceiling, and cost facts do not justify committing the full timing sequence now.

If project review later overrides this recommendation, run M1F primary only. Run the diagnostic only after a pre-frozen useful local/window signal; run PRIORITY_STABLE only after that qualified signal. An unhelpful primary stops the expansion.
