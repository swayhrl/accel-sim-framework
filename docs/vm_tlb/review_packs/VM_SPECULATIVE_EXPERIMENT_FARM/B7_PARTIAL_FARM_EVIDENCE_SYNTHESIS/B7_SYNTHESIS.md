# B7 partial farm evidence synthesis（`SPECULATIVE_DIAGNOSTIC`）

本目录只由现有 Window-B scratch、partial、manifest 与 telemetry 流式生成；没有启动 simulator、生成 trace 或重建。B1 每次只解开一个已验证 partial，且受压缩大小 guard 限制；没有构造跨 partial 大集合。

## 覆盖结论

- coverage matrix 包含 106 个 workload/config/ROI 行。B1 是 `REAL_PARTIAL`；B2 已完成项均为 `SMOKE_ONLY`；B3/B5 为 `PLANNED_ONLY`；B4 为 `STATIC_ONLY`。
- 现有 B2 smoke 的强可观测信号数为 1。强信号仅说明该单 kernel telemetry 有差异，不构成 full-workload 或性能因果结论。

## A terminal 后的第一小批建议

1. 在 clean no-swap、单 worker 下补 B2 decode1 的 PWC finite-32、finite-512、ideal 三个 smoke，以围绕已观察到的 PWC-off smoke 信号建立最小对照。
2. 接着补 decode1 的 2MB diagnostic 与两个 translation controls。
3. 只在上述项稳定且资源门控通过后，分别做一次 B1 decode1/prefill miner peak-RSS 校准；其后才允许补 B1 partial。

所有结论和 resume 排序都必须在 accepted 环境中的连续 full ROI 重跑后才能升级。
