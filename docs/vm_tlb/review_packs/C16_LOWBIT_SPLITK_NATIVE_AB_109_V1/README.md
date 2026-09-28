# C16 low-bit split-K native A/B on node109

Status: `OPERATOR_SPECIFIC_SPLIT_POLICY_ONLY`. All four accepted A outputs reproduced exactly, split1 passed the frozen correctness tolerance, and the launch contract passed. Split1 improved `up_proj_M256` materially but not `down_proj_M256`, while both M1 points regressed beyond 5%.

This pack is bounded to Layer0 `up_proj`/`down_proj`, M1/M256, native RTX 4080 execution, and split8 versus split1. It makes no full-model, unique-cause, novelty, Lane 4, or L2-mechanism claim.
