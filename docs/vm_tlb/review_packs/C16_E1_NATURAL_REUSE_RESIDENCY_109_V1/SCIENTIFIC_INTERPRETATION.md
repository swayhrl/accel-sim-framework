# C16 E1 natural-reuse / residency causal-closure interpretation

Immediate post-pressure reuse shows a clear one-call refill for AWQ q_proj, down_proj and up_proj: target DRAM falls from packed-state-scale K1 traffic to tens of KiB by K2, with matching timing recovery. RAW down/up remain comparatively flat at roughly 136 MB DRAM; RAW q_proj remains near its 25.7 MB state footprint. This rejects Case C.

Role-specific capacity knees occur at 32 MiB for q_proj and 16 MiB for down/up, earlier than nominal residual-L2 budgets of 57.63 and 30.36 MiB. The ordering is capacity-consistent but the deltas are not an exact capacity theorem. Timing knees and non-monotonic post-knee traffic further indicate role/kernel/access-policy effects beyond nominal state size.

Across seven fresh-process AWQ full-model runs, tokens `[23578, 11, 323, 3950]` and all 12 occurrence SHA bindings reproduce exactly. Natural layer0 up_proj DRAM is about 49 MB at D0/D1/D3, outside the accepted isolated WARM-to-DENSE bracket on the dense side. Layer0 down_proj DRAM is about 37 MB and likewise slightly beyond its dense reference, while timing lies inside the bracket. Layer14 up_proj reproduces layer0's roughly 49 MB natural DRAM and D3 timing; layer0 D0 alone carries an additional first-step timing cost.

The integrated result is `CASE_B_WITH_CASE_D_ROLE_DEPENDENCE`: immediate reuse refills compressed state, but realistic full-model interference makes subsequent natural occurrences dense-like or beyond the isolated dense bracket. Capacity matters, but role/kernel/access policy also matters. The optional accepted RAW BF16 full-model control runs naturally and remains flat/high-DRAM at layer0 up_proj.

This closes the registered causal-diagnostic stage without proving a cache/TLB mechanism, excluding translation effects, or authorizing selective residency hardware. No NVBit, full address trace, cache/TLB mechanism, or mechanism simulation was started.
