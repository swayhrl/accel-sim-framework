# Lane F / 109 — R101R5 Native post-L1 check

Result: `NATIVE_POST_L1_DOWNSTREAM_SUPPORT_NOT_OBSERVED`.

The accepted L512 NCU report had traffic but no issue/stall counters, so three bounded NCU jobs profiled only second-recurrence XXT, BA, and BMM-add under the GPU lock. Exact function/grid/block/occurrence and accepted L512 input/source were verified; all numerical checks passed. Across those targets, math-pipe throttle dominated (56.87%, 51.21%, 71.26% of active warp-cycles), LG throttle stayed below 1%, and ordinary LDG warp-instruction counts were 0 / 25,344 / 45,056 versus 506,880 / 506,880 / 428,032 LDGSTS. Long-scoreboard samples did not isolate ordinary LDG/ST downstream service. This does not negate the accepted R101R4 simulator response or localize ICNT/L2; it only fails to observe the requested matching native pressure signature.

Review authority: `docs/vm_tlb/review_packs/AWMA_R101R5_NATIVE_POST_L1_DOWNSTREAM_109_V1/`. No follow-on mechanism or 174 run was started.
