# Lane 2 TVD — review_r2 continuation

Status: **IN_PROGRESS — actual R0 production wiring and new producer tests**.

Continuation authority: `aec01450d3c527524ee09ee59242f582fafe5354`; original scientific authority remains `6c136e2a56a008695f8c8b815723bf8f1a760db9`. review_r1 continuation is not executed. Existing Lane 2 branches/worktrees are reused, no restart/reset or duplicate process.

Consumed exact Lane 1 R0: Core `126394be46b15f55b9756d43eb9ca9a9baae1c84`, Framework release `02982b65e87f170103b44c6dbd562a8ffb03841e`, production Framework `37dec04d223ae65167c5584e56887c74f6540d27`. Lifecycle APIs are now executable; the earlier ABI-only dependency is resolved. Frozen R0 binary is untouched.

Node huangrulin-174; worktrees `/workspace/worktrees/{accel-sim,gpgpu-sim}-ep-l2-ft20261016-lane2-v1`, branches `hrl/ep-l2-ft20261016-lane2-v1`. Current candidate Core source `c9666ae6ef21bae41f394b9e51aa4be370a40858`. No active Lane 2 task/run existed at continuation. Shared registry was inspected under its permanent lock; no duplicate run/lease was adopted.

Implemented candidate: actual selected clean victim retention in sole allocator; shared combined WAD/TVD address authority; real +1-cycle frontend lookup before generic WAD rejection; shared bank read and actual ICNT response lease commit; same-handle promotion including dirty resident WB; actual lower_accept/set_done; flush/invalidate cleanup. New switches default OFF and require U_WB/WAD128. Statistics now expose served sectors/bytes; old avoided fields are deprecated served-only aliases, not physical savings.

Executing: new actual memory_sub_partition clean producer tests and isolated build. Legacy DRAM READ/WRITE macro collision was fixed with operation enum names; no asserts removed. Seven already-passed directory groups are not rerun. Dirty production tests follow the clean checkpoint. No full TVD or new test PASS asserted yet.

Shared build lease: `a8c1e21e823f43ab90776075aa01424d` (Lane 2, 2 CPU); logs `/workspace/results/ep_l2_ft20261016/lane2/review_r2_clean_production/`. No formal application run; Lane 5's independent R0 qualification and B16/U_WB experiment remain higher priority and independent. Prior clean/dirty module packs remain immutable.

## Clean production checkpoint

Four actual producer scenario groups PASS at Core `8ae60ff11ad847f28013df2873a5b7a8df7085b4`. Pack `docs/ep_l2/review_packs/FT20261016_LANE2_CLEAN_PRODUCTION_r1/`; binary/config/stimulus/raw hashes in manifest. Clean was delivered before dirty tests. Now continuing dirty read-forward/WB waiting and atomic producer validation. Initial producer test exposed a missing admission audit in the new direct-hit route; fixed by recording the real admitted requester before response audit, preserving the assertion.
