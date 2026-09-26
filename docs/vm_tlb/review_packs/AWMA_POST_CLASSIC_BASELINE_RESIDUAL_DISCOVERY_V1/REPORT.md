# AWMA_POST_CLASSIC_BASELINE_RESIDUAL_DISCOVERY_V1

Final status: **NO_NOVEL_RESIDUAL_MECHANISM_IDENTIFIED_V1**

Lane B's `WARP_VPN_DEDUP_REFERENCE` is the scientific baseline. It covers the
entire historical PREL1 request set on all seven targets; PREL1 is retired.

## Main result

Classic intrawarp dedup does not eliminate all modeled translation sensitivity.
The preregistered L1 0/80 diagnostic changes cycles by +7.037% (T0), -1.983%
(T1), +12.822% (T2), and +1.269% (A2) relative to the 10/80 strong reference.
The response is material but non-monotonic and localized to the hit-dominated
L1 lookup service path.

This does not yield a novel mechanism. Pichai et al. already overlap TLB/cache
lookup, and Yoon et al. filter translation through virtual caches. H1 is highly
overlapped by the ISCA 2018 SIMT-aware page-walk scheduler; H2's collision is
zero by accepted source order. No problem passes all Phase-E gates.

## Experiment discipline

- reused seven accepted WARP reference results;
- ran four preregistered L1 0/80 causal diagnostics;
- ran four exact-neutral Level-1 Observatory replays;
- did not run zero-all, Level 2, H1/H2 policy, or a candidate;
- all coverage/correctness/quiescence checks pass.

See `RESIDUAL_LOCALIZATION.md`, `CLOSEST_WORK_AFTER_BASELINE.md`, and
`PROTOTYPE_DECISION.md` for the decision chain.
