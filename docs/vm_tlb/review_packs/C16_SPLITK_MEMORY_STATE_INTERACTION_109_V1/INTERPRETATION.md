# Split-K memory-state interaction interpretation

Primary bounded label: `SPLIT_POLICY_BENEFIT_STATE_CONDITIONED_SCOPED`.

- `up_proj`: gain_W=30.001%, gain_E=26.927%, state_interaction=3.075 percentage points; bootstrap interaction q05/q50/q95=[2.889, 3.096, 3.323] pp.
- `down_proj`: gain_W=-1.285%, gain_E=-6.625%, state_interaction=5.340 percentage points; bootstrap interaction q05/q50/q95=[5.064, 5.367, 5.682] pp.

WARM_SAME_ARM directions are compared only qualitatively with the prior ABBA protocol; medians are not spliced across protocols. EVICT_CONDITIONED changes target traffic/timing descriptively as listed in NCU_SUMMARY and TIMING_SUMMARY, but the conditioner may also affect TLB, clocks, scheduling or other execution state. GEMM and reduction rows remain separate. No counter is assigned to a specific tensor, and no unique L2/cache cause is claimed.
