# C16 Qwen decode execution-mode deconflation canary, node 109

Final decision: `MODE_DECONFLATION_CORRECTNESS_PASS_FOR_OBSERVER_REVIEW_ONLY`.

The final authorized contract is `c4a61e8f2d4d96587e0006726e21796a360404e7` (tree `d0370fa0fba6566161558c6f7b34b3c5eebb14e5`, contract SHA256 `bc547a652ed04db9c3e1e1e7020be53ac76052bd76bfdad6d89eee0f69678501`). `CONTRACT_AUTHORITY.json` and `ASSET_INPUT_RECHECK.json` contain the entry gates.

Mode A and B both used `VLLM_COMPILE`, the compiled `Qwen2Model` submodule, `inductor`, BF16, `FlashAttentionImpl`, and `UnquantizedLinearMethod`. A used `FULL_AND_PIECEWISE` and the tested decode shapes each registered 31 full CUDA Graph replays. B used `CUDAGraphMode.NONE` with zero capture/replay events. The identity-only CUDA inventory records BF16 GEMM/GEMV, FlashAttention and fused kernels without duration claims.

MP02: 1 row, 512 frozen prompt tokens, 32 exact generated tokens and 32 exact sampled-token logprobs. MP03: one real B4 request, four mapped 512-token rows, each with 32 exact generated tokens and sampled-token logprobs. The frozen tolerance was `0.05 + 0.01 * abs(A)`; maximum observed absolute delta was zero. The CPU-only verifier in `util/vm_tlb/c16/qwen_decode_mode_deconflation_canary/validate.py` passed 32 checks.

Three engineering attempts consumed a conservative total of 97.108089 GPU-active seconds under the 120-second cap. The first two failed on receipt logic and are excluded from science; all raw bytes were preserved. `ATTEMPT_HISTORY.json` and `GPU_ACTIVE_BUDGET.json` give the accounting. No observer, NSYS, NCU, NVBit, SASS, Accel-Sim, Tier0 rerun, or holdout was run.

Start with `FINAL_DECISION.json`, then `MODE_RUNTIME_IDENTITY.tsv`, `FREE_RUNNING_CORRECTNESS_BY_ROW_STEP.tsv`, `BACKEND_KERNEL_IDENTITY.tsv`, and `RAW_INDEX.tsv`. The raw payload is durable at `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/c16_qwen_decode_mode_deconflation_canary_109_v1/20261002T045340Z`. `PUBLISH_RECEIPT.json`, `REMOTE_VERIFY.json`, and `COPYBACK_VERIFY.json` record per-file verification. `SHA256SUMS` covers this review pack. The historical MP02/MP03 `STOP_POINT_CORRECTNESS` remains unchanged. This pass only admits a separate observer qualification review; `automatic_next_goal=false`.
