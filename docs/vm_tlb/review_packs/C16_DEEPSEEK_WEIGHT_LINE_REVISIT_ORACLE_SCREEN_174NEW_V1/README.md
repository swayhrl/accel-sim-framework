# C16 DeepSeek weight-line revisit oracle screen

CPU-only independent consumer of the accepted C16WARP1 per-static-MREF shards. The sole entry point is this README; `TRAFFIC_ORACLE.json` and the five TSVs carry the reproducible counts. Execute `python3 util/vm_tlb/c16/weight_line_revisit_oracle.py` from the repository root. No GPU, new capture, NCU, or simulator was used.

## Result

The old `2.0 warp visits per 128B line` is **two warp-record visits**, not two distinct warps. Every one of DeepSeek's 180,224 revisited weight lines is visited twice by the **same CTA, same warp identity, same static MREF**, at identical 2B/BF16 start addresses. Each line contributes one selected 32B sector in this per-MREF trace. Therefore O1 and O2 both have 50% avoidable *logical visits* (180,224 sector visits, or 5,767,168 logical bytes). They are not complementary first/second 64B halves. No cross-CTA duplicate was observed. This is not evidence that L2/DRAM performed twice the service, nor that runtime can improve by 50%.

The DeepSeek and OLMoE captures have the same cuBLAS `gemvx` template-6 function and all 243 selected static indices match in instruction offset, opcode and SASS. Both have one observed input row, output width 2048, 512 observed CTA IDs and two observed warp identities per CTA. Their input widths differ (1408 versus 1024), and the DeepSeek selected weight MREFs execute twice per warp where OLMoE executes once. This is a shape-associated same-warp work-decomposition difference, not cross-warp sharing or a lineage-specific cache effect. The precise source-level loop condition or K threshold is not recovered from this payload.

Final classification: `GEMVX_SHAPE_WORK_DECOMPOSITION_EFFECT`. No native service-oracle contract is issued. See `FINAL_DECISION.json` and `DEEPSEEK_OLMOE_TEMPLATE6_COMPARISON.md` for limits.

## Files and provenance

`LINE_REVISIT_DETAIL.tsv` contains one row per accepted DeepSeek/OLMoE weight line *within its independent static-shard replay*. Each visit descriptor gives CTA, warp, record ordinal, static MREF, relative 32B sector, exact BF16 starts (contiguous `a..b:2` notation is inclusive), and byte interval. `UNKNOWN` on a single-visit OLMoE line means the revisit classification is inapplicable, not that its address is unknown. Q30 is independently rescanned as a discovery-control cross-check; its 491,520 lines are summarized, not repeated in the large detail table.

The scanner checks the previous accepted run-manifest/catalog/transfer-ack digests, all 729 prior shard trace/context digests and record/lane totals, C16WARP1 header closure, and prior line totals. Source authority is the accepted `STATIC_MREF_MAP.tsv` or OLMoE canonical selector; their digests appear in the JSON and static map. Discovery authority: `734e6a7ca49bd8cbf16eeb0702cf80755afc23f1` (tree `997f71ed191c5d707dfe169ad9dbdda652448010`). The raw root is `/root/share/mnt164/huangrulin/c16_ai_workload`.

The prior `cross_warp_shared_line_fraction` counted **warp records** touching a line, not distinct `(CTA, warp)` identities. This screen corrects that interpretation without changing the old artifact. It does not union addresses across separate replays, infer cache misses from sector counts, or treat OLMoE as an independent holdout.

## Validation

`python3 util/vm_tlb/c16/test_weight_line_revisit_oracle.py` tests complementary halves, exact duplicate, same-sector/different-byte, same/cross CTA conservation, and single visits. `DETERMINISTIC_RERUN_RECEIPT.json` records the exact output comparison. `SHA256SUMS` hashes deliverables other than itself.
