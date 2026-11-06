# EP-L2统一访存特征分类与下一轮科学选点 V1

本轮已完成一次性分类、独立审核与精确申请准备。新完整应用启动 **0**、预算消费 **0**；原台账、Source、Spec、raw和所有接受/失败记录保持不变。科学基点为 `1c63b67beace667ea8a8028d77fbf9e5f2a9afc7`。本包不授予模型启动权限。

## 可以据此做出的决策

| 方向 | 推荐输入 | 已知证据与用途 |
|---|---|---|
| Victim持续保留 | Stencil | 实际保留sector服务显著；已有同Source W→WV条件收益9.0025%。作为长负载主正例，研究有限保留与WB竞争。 |
| Victim独立验证 | GEMM（不是SGEMM） | CLEAN保留服务明显，WB很少；已有W→WV条件收益1.4876%。适合避免只用FWT设计与验证。 |
| 容量/机制替代 | 3MM、Stencil、GEMM、FWT | G64减少部分Victim响应及额外WV收益，同时改善容量背景；不因此删除复用正例。 |
| 压力感知RO | Conv、Scan | Source78已测Line-MSHR128及full事件；新Core812同事件激活仍是待检验假设。推荐下一轮4点。 |
| 无压力RO开销对照 | Vector4M | Core812/1700优化点激活0、RO接纳0，F55925→45425；不能解释成活跃RO加速。 |
| 内存敏感但当前EP增量低 | Vector4M、Conv（限定Source78） | 合法850→1020服务扰动有响应，且该Source背景F稍慢于S；跨Source不能沿用为实测结论。 |
| 高merge≠压力 | SGEMM、Vector6M | SGEMM merge约92.8%但S普通Line峰34/full0；Vector6M峰110/full0，不是压力正例。 |
| WB多但V兑现少 | Scan | F约531万WB、5584 Victim响应；服务敏感性仍UNKNOWN。只为压力泛化申请，不为V重复测量。 |

FWT的cold过滤已测端到端慢0.63%，不继续扩散该负方向。Transpose保留既有零容量收益/负WV对照，无需重复。新Victim结构尚未冻结、CLEAN完整生产资格未闭合，本轮不虚构可启动的新Source或额外模型。

实际Victim响应是保留sector被再次服务的证据，不是避免DRAM请求数；全程序sector时间复用分布和淘汰后重访距离仍UNKNOWN。RO流量、资源压力、最终性能分开分类。最终EP加速比用于验证分类价值，不用于定义“友好”。

## 人口与有效测量覆盖

- 原始103行 = 96输入/内容组 + 7未决槽位；35代表输入与42目标程序/槽位成员分别保留。
- 当前明确范围：Native中16个EP-MAIN/EP_L2结构化完整应用请求，共291端点 = **286接受 + 5不接受**，涉及28个接受输入SHA。不是286个工作负载，也不是EP全历史总量；较早singleton/兼容范围单独列为排除项。
- 103行中：28有接受结果、1仅失败、67在本范围未测、7身份未决。
- 27输入/57个原Source78参考端点有M/W/RO特征；151个接受端点有V计数。
- 15行有正V服务上下文，17行有显式零V上下文，两者跨配置可重叠，不相加。
- 只有3个输入有严格匹配的服务时钟响应：Vector4M、Conv、BlackScholes；BlackScholes为所测扰动零响应。其余UNKNOWN，不能根据“流式”或请求数量补测量标签。
- 原2026-10-29的222接受数保持冻结，不当作当前总体；旧103行的LIVE/HOLD等字段也是冻结历史，当前状态看新增current字段。

## 下一轮一次性审批建议

两个独立范围，各2次，**共申请4次、当前批准0次**：

1. **Conv**：Core812 / ELFa606，G32×8、850MHz、L100、FR-FCFS128；F_BASELINE与F_PRESSURE_EPOCH。
2. **Scan**：同Source、同硬件背景，两种F策略。

每对完整283项只有pressure_epoch 0/1不同。同新Source基线必须新测；旧Source78或Core862结果只作背景。全部4点可独立释放，不设置基线归档或跨族完成门。

已完成这两个输入的生产RO loader四次与283项parser四次CPU检查。剩余的是用户科学批准，以及Main的正式预算/不可变Spec、43字段Host、22 Native+5 Host pin、boot/mount与实时资源绑定，不重复旧124项资格。

历史F成本：Conv约59分钟，Scan约8.9小时。新Source规划Conv每点1–2小时、Scan每点8–12小时；4点资源允许时并行，约8–12小时模型墙钟加归档，非保证。总计4个CPU、估计RAM8GiB/硬RSS承诺12GiB，按实际资源动态准入。完整成本、用途、输入身份及剩余条件见精确申请。此处仅申请，不启动。

## 审阅入口与可复用产物

- [统一分类JSON](UNIFIED_WORKLOAD_MEMORY_TAXONOMY_V1.json) / [CSV](UNIFIED_WORKLOAD_MEMORY_TAXONOMY_V1.csv)：103行、身份分层、指标、标签、置信及缺口。
- [方法论与证据](CLASSIFICATION_METHODOLOGY_AND_EVIDENCE.md)：定义、人口、阈值、Source边界及UNKNOWN。
- [选点与优先级](WORKLOAD_SELECTION_AND_PRIORITY.md)：正负例、容量替代、开发与独立验证输入。
- [精确科学申请](NEXT_EXACT_PERFORMANCE_EXPERIMENT_REQUEST.md) / [JSON](NEXT_EXACT_PERFORMANCE_EXPERIMENT_REQUEST.json)：两个可同时审批的有限范围及四份283图。
- [当前端点索引](agent_a/CURRENT_ENDPOINT_INDEX.json)：291个独立cohort/UUID及全部Source5/ordered commandlist/配置。
- [W/V精确对照](agent_c/WV_REUSE_EVIDENCE_BY_INPUT.json)：19组完整配置差分匹配。
- [新输入有限CPU资格](agent_b/SOURCE812_CONV_SCAN_CPU_QUALIFICATION.json)。
- [Main独立验收](main/MAIN_INDEPENDENT_ACCEPTANCE_AUDIT.json)：5166项核对；不把计数核对称为应用或生产协议测试。
- [真164证据归档回执](main/TRUE164_SMALL_EVIDENCE_ARCHIVE_RECEIPT.json)。

历史Motivation/Streaming仅作身份未闭合的独立资料；本包未把它们并入Source78统一统计。没有扫描巨大Trace/raw，没有新仿真、GPU、NI或论文任务。Source KEEP，释放0。
