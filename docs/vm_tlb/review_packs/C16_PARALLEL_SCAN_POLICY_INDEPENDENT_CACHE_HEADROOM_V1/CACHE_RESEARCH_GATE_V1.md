# C16 cache research oracle gate V1

## Gate

1. Reject `NOT_APPLICABLE` samples before using PASCAL formulas: workers must share physical blocks, follow the same or a regular scan order, and have an explicit phase case.
2. Always publish both aligned-best-case and observed-phase status. Missing per-worker progress keeps observed `U(t)`, `T*`, LRU and policy-independent bounds UNKNOWN.
3. Compare actual L2 miss bytes with both the PASCAL long-run fractional lower bound and separately labeled finite-run references. Never relabel the fractional relaxation or an aligned one-fill reference as a realizable policy-independent floor.
4. Keep `CACHE_TRAFFIC_HEADROOM` separate from `CACHE_TIMING_HEADROOM`. A replacement candidate is registered only when both are exposed under the same applicable sample.
5. Require matched software scheduling/dataflow controls before mechanism work. A gap removed by GROUP_FULL_M is not residual replacement-policy opportunity.

## Current C16 outcome

- Raw ROW split1 at K3072/K4096 has large traffic oracle gaps and 27.631%/33.073% matched timing exposure, so those uncontrolled cells meet `CACHE_POLICY_MECHANISM_WORTH_FURTHER_REVIEW` as *candidate observations*.
- The existing GROUP_FULL_M control brings split1 to the aligned TTL/LRU one-fill reference at both K values. The PASCAL fractional bound remains looser and non-discriminative for the one-scan horizon; under the accepted strong baseline, observed residual replacement opportunity is classified `REPLACEMENT_POLICY_HEADROOM_SMALL`.
- Split8 ROW/GROUP remains within about 2% of one unique fill and has small/no mapping traffic change: `REPLACEMENT_POLICY_HEADROOM_SMALL`.
- PER_MTILE cross-M controls are `NOT_APPLICABLE` because they deliberately remove shared physical block identity.
- Residual M-sweep timing at identical TEX read-side hit behavior directs remaining work toward scheduling/parallel decomposition, not a replacement predictor.

Overall gate: `REPLACEMENT_POLICY_HEADROOM_SMALL`. The closed Split-K branches remain closed. No replacement mechanism is authorized.
