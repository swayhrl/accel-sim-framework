# Qwen compiled/no-CUDA-Graph Observer V2 canary on node 109

Final decision: `COMPILED_NO_CUDAGRAPH_OBSERVER_V2_IDENTITY_FAIL`.

The exact Lane6 contract is commit `eaaa2e66befa872ce7c8f47011e9fe7cdf8921d9`, tree `f2d9d3a46ca3774a82eaeb2175b01a6cdbec9d2f`, contract SHA256 `bf5584db66cf66d076e49d5fbbe9053d9a614c88eccaf514518137ee3812ef68`. `CONTRACT_AUTHORITY.json` validates the authorization, bound sources, frozen gates and budgets. The exact Lane6 runner and Observer V2 files were imported without modification; `SOURCE_INTEGRATION.json` records their hashes.

MP02 failed at the first Observer ON warmup: the semantic receipt contained **0** occurrences against the frozen **4,608**. This is the first identity gate failure. The six native OFF/ON samples were never started, so output correctness, the CUDA-event neutrality median, host cross-check and OFF/ON kernel inventory were not evaluated. MP03 and NSYS were not run. `MP02_IDENTITY_FAILURE_DETAIL.json`, `CORRECTNESS_NEUTRALITY_STATUS.json`, `KERNEL_INVENTORY_STATUS.json` and `NSYS_STRUCTURE.json` state each boundary. The source runner reached and passed its effective Mode B configuration check before the semantic error, but it did not emit a final per-arm compiled-path receipt; no fully qualified ON identity is claimed.

Conservative GPU-active time was 8.795375 seconds, all in MP02 and under its 75-second and the total 180-second caps. The lock was released and postflight found no compute process. Raw stdout, stderr and runner JSON are at `/data/c16/qwen_compiled_no_cudagraph_observer_v2_canary_v1/raw/20261002T060732Z` and were published to `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/c16_qwen_compiled_no_cudagraph_observer_v2_canary_109_v1/20261002T060732Z`; per-file SHA and copy-back checks passed. `RAW_INDEX.tsv` and `PUBLISH_RECEIPT.json` provide provenance. `SHA256SUMS` covers this pack.

Historical Mode C MP02/MP03 `STOP_POINT_CORRECTNESS` remains unchanged. No Tier0 rerun, NCU, holdout, MODE_A, MODE_C, mechanism, or automatic next goal was executed.
