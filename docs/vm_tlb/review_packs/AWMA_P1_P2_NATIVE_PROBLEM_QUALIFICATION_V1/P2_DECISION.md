# P2 decision

`P2_COST_DOMINATED_BY_SELECTOR_COMPUTE`

Both frozen configurations preserve exact ordered indices and bitwise-identical consumer outputs across ONLINE, paired READY-INDEX, and strong CUDA-Graph ONLINE arms. The graph liveness test mutates Q in place, observes changed indices equal to fresh eager selection, and restores the original indices; status is `PASS_LIVE_ONLINE_SELECTION`.

- Top-256: strong ONLINE 0.095232 ms versus READY 0.064832 ms; residual 0.030400 ms (46.890%). Selector-only median is 0.062688 ms.
- Top-128: strong ONLINE 0.073344 ms versus READY 0.048928 ms; residual 0.024416 ms (49.902%). Selector-only median is 0.061440 ms.

The residual passes the timing materiality gate in both configurations, but is only 48.494% and 39.740% of independently measured selector arithmetic time. CUDA Graph improves the eager full chain by 1.301x and 1.522x. There is no localized cost beyond the live selector work itself, so this does not support an index-readiness hardware residual. Conditional NCU was not authorized.
