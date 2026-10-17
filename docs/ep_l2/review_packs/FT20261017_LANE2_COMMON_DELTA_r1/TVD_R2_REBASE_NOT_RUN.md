# TVD_R2_REBASE_NOT_RUN

TVD r14 source remains exactly **be5dcbe1fa5b9a501e81a77a6c399e6f6530e536**, branch `hrl/ep-l2-ft20261016-lane2-v1`, worktree `/workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane2-repair-r3`. No source file, test, binary or config there was modified by COMMON_DELTA. Its three `--r14-integration-gates` groups remain **NOT_COMPILED_NOT_RUN**. No common-only binary is a TVD binary.

COMMON_DELTA is separate: branch `hrl/ep-l2-ft20261017-lane2-common-delta-r16-v1`, source099aeb5ac002ddc03ab8dc295caa1333d9aa50e1 on official088146f7f85b4073deb5d166a0a4484c7f3b48b2. It contains no TVD/RO/Ideal integration. The old TVD ten-file adapter was relative to c948, not to this new common source. Do not apply it wholesale over an A1/common release and call that a validated rebase.

Next legal entry: Lane1 publishes its exact A1/common integrated source, producing Framework/vendor identity, new binary and actual producer evidence. Rebind to that exact commit in the isolated TVD worktree only after shared admission, preserving all frozen source/build outputs. Lane1 owns public R2; Lane5 independently qualifies the exact feature vector. No polling/waiter is created here.

Required manual merge points:

| File | Preserve from COMMON_DELTA / official parent | Preserve from r14 TVD |
|---|---|---|
| gpu-cache.h | `atomic_fill_masks` declaration; saturated nominal resident headroom; separate observer snapshot API; official public-cache accessor; Lane1 A1 transaction interface | TVD role/state/op labels and combined free/owner conservation, directory/lease storage and explicit Tag binding |
| gpu-cache.cc | actual D512 ready dirty-sector/byte masking and original non-D512 path; Lane1 pending-victim/native Tag semantics | TVD WAD set_done/directory visibility, production includes, TVD promotion preview |
| ep-l2-ft-cache.inc | atomic response symbolic completion label after real grant; observer scope/Tag+landing counts; Lane1's exact pending victim/rollback/grant cancellation fix | same-handle TVD promotion/retention, exact host alias refusal/retirement, physical-cycle WB/TVD ownership and epoch cleanup |
| l2cache.cc | bypass-only lower FIFO credit; successful bypass admission token once; M0 explicit legacy scope and separate instantaneous Tag/landing/physical output | texture eligibility before TVD frontend, serialized lookup, real TVD response enqueue/commit; never add a global lower-full hit gate |
| ep-l2-tvd-directory.h / ep-l2-tvd-cache.inc | no common-source replacement is proposed | clean-retention physical cost, separate dirty/total cost semantics and all r14 fixes |

The r14 bypass token insertion and common C2 insertion are the same logical correction; merge once. Common snapshot physical free must use the final allocator's complete role set, including TVD/RO if enabled, rather than copying a three-role formula. Tag-visible counts exclude retained TVD and non-Tag pending landings; retain the other-unbound bucket for invalidated old identities.

Keep `test_common_delta_r16.cc` as common correctness evidence and `test_tvd_production.cc` as TVD evidence. After the official parent is exact and resources permit, use the previously finite TVD11-process/24-positive/7-rejection plan plus affected common integration gates; it has not run here. Resolve the r14 RO/Ideal epoch/descriptor/Tag-generation/bank-lifetime integration risks before claiming relevant R2 combinations. No RO/Ideal merge, scientific boundary expansion, application run or full TVD completion is claimed.
