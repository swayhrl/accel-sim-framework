# C12 C5 full-ROI fair performance replay

状态：`IN_PROGRESS_C5_REPLAY`。

本包记录 C12 对冻结 C11 输入的 22 点正式 C5 full-ROI 性能回放。每个 arm 的
原始 log 留在工作区结果根而不提交；`RAW_LOG_INDEX.tsv` 将其与 SHA-256 绑定。
`ARM_STATUS.tsv` 和 `ARM_RESULTS.tsv` 会在每一个 arm terminal 后立即更新。

结果只能同 ROI 内相对 C5 F0 比较。C11 的 common
`MODELED_DRIVER_PA`、Core、binary、trace list、registration 和 config hashes 是
不可变的输入。任何会改变这些语义身份的改动都会使旧结果失效，不能混合。

推荐阅读顺序（完成后）：`FINAL_REPORT.md` → `COMPARISON_ANALYSIS.md` →
`EARLY_EXECUTION_PROMOTION_AUDIT.tsv` → `ARM_STATUS.tsv` →
`SPEEDUP_SUMMARY.tsv` → `TRANSLATION_MECHANISM_SUMMARY.tsv` →
`CROSS_LAYER_SUMMARY.tsv` → `PROVENANCE_MATRIX.tsv` → `RAW_LOG_INDEX.tsv`。

在矩阵完成前，已 terminal PASS 的两个 F0 可单独审阅
`C12_CACHE_BEHAVIOR_FINDINGS.md` 与 `C12_CACHE_BEHAVIOR_CHECKPOINT.tsv`；它们是
只读 full-ROI F0 cache characterization，不替代 22-point fair-arm 结论。

标签保持：`SPECULATIVE_CANDIDATE`；F1/F8 保持
`REFERENCE_APPROX_SUBENTRY_16`。F6、KV segmentation、12K、M5 和 Window A/B
均不在本轮范围内。
