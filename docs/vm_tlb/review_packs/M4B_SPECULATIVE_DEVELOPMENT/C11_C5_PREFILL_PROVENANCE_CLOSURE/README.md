# C11 C5 prefill provenance closure

最终状态：`C11_C5_INPUTS_CLOSED_READY_FOR_C5_REVIEW`。本包关闭 C5 的
immutable 输入、driver allocation、V2 registration、共同 PA 与命令契约；它不
包含、也不授权 C5 performance replay。

推荐阅读顺序：`FINAL_REPORT.md` → `INPUT_SOURCE_AUDIT.tsv` →
`MODELED_DRIVER_PA_POLICY.md` → `C5_DRIVER_ALLOCATIONS.tsv` →
`COMMON_PA_FAIRNESS_VALIDATION.tsv` → `C5_ARM_MATRIX.tsv` /
`C5_COMMAND_MANIFEST.tsv` → `C5_ACCEPTANCE_MATRIX.md`。

标签保持不变：`SPECULATIVE_CANDIDATE`；使用 sub-entry 的 F1/F8 仍为
`REFERENCE_APPROX_SUBENTRY_16`。C5 是独立 review gate，不能由本包直接启动。
