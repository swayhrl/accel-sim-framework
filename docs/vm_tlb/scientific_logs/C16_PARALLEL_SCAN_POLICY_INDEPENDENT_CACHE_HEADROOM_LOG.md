# C16 Parallel-Scan Policy-Independent Cache Headroom V1

This CPU-only stage reads PASCAL arXiv:2609.10515v1, `PASCAL: A Phase-Aware Shared-Cache Model for Parallel Scans`, PDF SHA `e66e606470a841eae6495c6d0ddffbbb922d04a7ce6f4140a657850b7914db2e`. The current arXiv v2 has a different title and is not mixed into the v1 formula authority.

PASCAL's author formulas are kept distinct from the C16 mapping. The v1 model defines cyclic gaps, `U(t)=sum min(g_i,t)`, the exact slotted-TTL miss law, the fully associative LRU certificate, the fractional policy-independent residency bound, historical progress divergence `sigma_E`, the `C >= 2*sigma_E-1` LRU sharing condition, and a pipeline recurrence showing that reduced traffic need not repair sustained timing divergence.

The C16 mapping treats 16 M-tile macro-workers as scans over the same combined weight-side 128-byte-line stream. K3072 has `N=612864`, K4096 has `N=817152`, and RTX4080 L2 gives `C=524288` lines. GROUP_FULL_M supports an aligned logical best case; ROW has static distance 384 and 383 intervening CTAs. No accepted artifact contains actual per-CTA phases or historical `sigma_E`, so all observed-phase PASCAL bounds remain UNKNOWN. Split8 is a composite weight-side proxy with reduction traffic separate.

For aligned phases, `T*=524288`, TTL misses are exactly one per round, and the LRU certificate collapses to the same value. PASCAL's long-run policy-independent lower bounds are 0.1445282077 misses/round for K3072 and 0.3583964012 for K4096. Because the kernel is a single finite scan (`H=N`), the allowed `N/H=1` correction makes the long-run fractional bound non-discriminative. The one-fill value is therefore reported only as an aligned TTL/LRU reference, never as a PASCAL policy-independent floor.

Actual ROW split1 traffic is 8.908422 and 9.030064 fill-equivalents per scan-round at K3072/K4096; matched GROUP_FULL_M reaches exactly 1.0. Timing improves by 27.631% and 33.073%. These uncontrolled ROW cells are candidate observations under `CACHE_POLICY_MECHANISM_WORTH_FURTHER_REVIEW`, but the existing classical software mapping already captures the gap. Under the accepted GROUP baseline the residual gate is `REPLACEMENT_POLICY_HEADROOM_SMALL`.

Split8 ROW/GROUP is within roughly 2% of the aligned one-fill reference, and grouping does not reduce miss sectors. Cross-M PER_MTILE controls are `NOT_APPLICABLE` because they intentionally remove shared physical block identity. The residual M sweep shows timing differences while split1/split8 TEX read-side hit fractions remain 1.0, separating scheduling/parallelism from cache traffic.

The overall decision is `REPLACEMENT_POLICY_HEADROOM_SMALL`. Closed Split-K branches remain closed; no GPU, new trace, simulation, observer, or replacement mechanism was launched or implemented.
