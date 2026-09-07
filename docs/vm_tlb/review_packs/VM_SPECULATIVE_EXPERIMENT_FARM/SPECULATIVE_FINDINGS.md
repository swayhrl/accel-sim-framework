# Window B speculative findings（`SPECULATIVE_DIAGNOSTIC`）

## 已测事实（仅 `SPECULATIVE_DIAGNOSTIC`）

- B0 的吞吐膝点冻结为 32；低资源模式当前有效并发为 1。
- B2 bounded smoke 语义完成 37/54，缺失 17/54；所有已完成行仍为 speculative diagnostic。
- B1 原子 partial：prefill 134/692，decode1 96/740。
- B3/B5 仅完成计划几何数值预检；B4 仅完成 trace-list/格式静态检查；均无运行时结果。

## 假设

- 在完整、经资源安全执行的 B2/B3/B5 ROI 完成前，不对 TLB、walker、PWC 或 cache 敏感性作性能归因。

## 供正式复跑的候选

- B2 的已完成 smoke 可作为后续 accepted 环境中重跑的候选清单，但不构成 formal evidence。
