# Pattern contract

All patterns use one managed allocation and constant deterministic data with CPU-reference checksum closure.

- **P1 DENSE_WEIGHT_STREAM:** 3 token-like steps; every step sequentially scans the full allocation.
- **P2 KV_GROWTH:** 8 steps; each step GPU-writes a new 1/8 tail and scans the full monotonically growing prefix. This is KV-shaped, not attention.
- **P3 MOE_EXPERT_ROTATION:** 64 equal expert regions, K=4, 16 steps. Experts `0,1` provide locality; rotating experts are `(7*step)%64` and `(7*step+13)%64`. This route is synthetic and not claimed to match OLMoE.

M0 uses demand migration. M1 performs one full prefetch only for R0/R1; oversubscribed M1 is `NOT_APPLICABLE_OVERSUBSCRIBED`. Cold and immediate repeat are the only measured repetitions.
