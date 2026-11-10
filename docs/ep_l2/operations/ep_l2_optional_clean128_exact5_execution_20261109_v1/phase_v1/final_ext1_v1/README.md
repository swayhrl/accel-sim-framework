# Stencil EXT1 单点最终回执

新增单点 `EP_PERF_CLEAN128_STENCIL_WV_EXT1_20261110_V1` 以 Source5、同一 Stencil 输入和完整 283 项实际配置完成一次正式消费，Native 状态 `CLOSED_ACCEPTED`，无重试和退款。三点的 Source、ELF、输入、100 个有序 kernel、6400 CTA 和 2,193,446,000 指令一致；283 项实际选项仅 `-gpgpu_ep_l2_victim_extension` 分别为 0/1/2。完整 raw 留在 174-new 执行根。真164 归档 SHA256 `bc643a1b93dd012b592b06d3d086f3a57b7bcbabe74c49a5a74311a301f20500`，并通过两个不同 Native 目标的独立完整恢复；Source KEEP。

| 比较 | 应用 cycles | 净差 |
|---|---:|---:|
| EXT0 | 4768893 | 基线 |
| EXT1 | 4787045 | EXT1−EXT0 = +18152 |
| EXT2 | 4786427 | EXT2−EXT1 = -618 |

EXT2−EXT0 = +17534 cycles。EXT1−EXT0 是扩展硬件迁移包的净效应；EXT2−EXT1 是同一扩展硬件下开启 CLEAN 策略包的净增量，包含查询、spill、占用和服务成本。CLEAN 策略包净改善；若整体仍比 EXT0 慢，下一轮优先审查迁移成本。这三个确定性单点不能把局部机制各自分解为独占关键路径周期，也不证明物理 PPA、能耗、数值 oracle 或跨负载收益；应用数值输出仍为 UNKNOWN。

验收、归档、三点一致性及逐 kernel 阶段分析证据见同目录 JSON/CSV；固定 Host、启动身份和实时准入见相邻 `live_ext1_v1/`。
