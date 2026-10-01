# Method lessons retained at terminal state

From the prior wave: oracle-first; strong-software-first; traffic is not timing; summed module durations are not a legal wall-time union; correctness precedes performance; cross-runtime capability is not a strict A/B; measured contention need not explain an entire slowdown; unknown stays unknown.

Problem Discovery V2 adds three sharper gates:

1. **Line granularity is not service granularity.** The same 128B line can mean different 32B sectors, the same sector but different bytes, or exact byte overlap. None alone proves a repeated cache miss or DRAM fill. Q30's selected duplicate sectors with zero exact duplicate BF16 bytes and DeepSeek's exact duplicate bytes make the distinction concrete.
2. **Cross-model difference is not lineage causality.** DeepSeek and OLMoE use matching template-6 static instructions but different K/shape and dynamic work assignment. A selected-shard contrast cannot be attributed to a model family before shape and backend controls; OLMoE is not a post-hoc independent holdout.
3. **Logical-work oracle is not timing oracle.** DeepSeek's 50% O1/O2 ceilings quantify redundant address-level work, not L1/L2 misses, DRAM, scoreboard stall, exposed critical path or whole-decode time. A large logical fraction alone does not authorize a native campaign or new mechanism.

Negative and unresolved outcomes are useful precisely when they preserve their denominator, authority and STOP rule. No frozen negative result was reclassified in this synthesis.
