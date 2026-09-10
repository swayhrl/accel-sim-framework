# C12 C5 full-ROI fair performance replay

状态：`C12_C5_FULL_ROI_COMPLETE_READY_FOR_REVIEW`。

该 review pack 保存冻结 C11 identity 下 22/22 C5 full-ROI arms 的小型、可提交结果；原始 simulator logs 和 traces 留在工作区结果根，`RAW_LOG_INDEX.tsv` 将每项与 SHA-256 绑定。

性能比较仅限同 ROI 的 C5 F0。所有 arms 共用每 ROI 的 `MODELED_DRIVER_PA`、Core、binary、trace list 和 registration；不同 identity 的数值不得混合。

推荐阅读顺序：`FINAL_REPORT.md` → `COMPARISON_ANALYSIS.md` → `EARLY_EXECUTION_PROMOTION_AUDIT.tsv` → `ARM_STATUS.tsv` → `SPEEDUP_SUMMARY.tsv` → `TRANSLATION_MECHANISM_SUMMARY.tsv` → `CROSS_LAYER_SUMMARY.tsv` → `PROVENANCE_MATRIX.tsv` → `RAW_LOG_INDEX.tsv`。

标签保持：`SPECULATIVE_CANDIDATE`；F1/F8 保持 `REFERENCE_APPROX_SUBENTRY_16`。F6、KV segmentation、12K、M5 和 Window A/B 均不在本轮范围内。
