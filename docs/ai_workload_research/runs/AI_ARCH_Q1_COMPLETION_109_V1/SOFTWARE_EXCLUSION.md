# 强软件排除与机制结论

来源为已接受组合包f88e40123f4060328aa50a16d22fa328cee51cfe：
[冻结文献与软件排除](https://github.com/swayhrl/accel-sim-framework/blob/f88e40123f4060328aa50a16d22fa328cee51cfe/docs/ai_workload_research/discovery/AI_ARCH_NEXT_STAGE_PORTFOLIO_REVIEW_V1/RECENT_LITERATURE_AND_SOFTWARE_EXCLUSION.md)。本轮不新增宽泛文献调研，不使用作者加速比充当本机测量。

| 路径 | 已有功能/语义 | 本轮证据 | 决策 |
|---|---|---|---|
| GS-Scale原实现 | deferred CPUAdam、参数forwarding、GPU/CPU pipeline | 实际native，保持数学与质量规则 | 强基线已有重叠；join/sync小，不把隐藏GPU时间再次计入等待 |
| 原T16 vs T8线程cap | 相同CPU集合、相同恢复状态与camera | 两个窗口分别5次formal，约12.14%差异 | 软件供给敏感性已验证；T16本就是基线，不是新硬件收益 |
| CLM | 已覆盖camera/visibility reuse、选择性appearance传输、optimizer overlap与调度 | 本轮SOURCE_ONLY引用旧接受审查，未移植实测 | 泛称复用/隐藏等待存在直接创新碰撞；不宣称其在本语义已测收益 |
| TideGS | 工作集/异步管理，eviction后optimizer cold restart及camera顺序涉及不同语义 | 未替代原source执行 | 不能当无损plug-in，也不能因未复现而声称软件已穷尽 |
| 只规避全局ID扫描 | 本次ON约2.5%窗口 | CPU函数实际Host区间 | 局部理论上界小，不以U/N低强推硬件 |
| GPU-only或不同optimizer | 改变原CPUAdam/deferred状态/容量条件 | 无独立质量合同 | 不引入本轮等价对照 |

CPU Adam+参数转发约75%的ON Host窗口，是具体而非想象的成本；其中CPU算术与主存供给尚未被独立物理变量拆开。观察到的大逻辑H2D/D2H量也不是PCIe饱和证据。需要的软件状态/调度/传输反事实尚有空间，当前不晋升新GPU单元。

科学终态：NATIVE_Q1_LATE_PIPELINE_COMPLETE；物理机制PARTIALLY_ATTRIBUTED；NO_HARDWARE_CANDIDATE_PROMOTED。没有自动启动下一实验。
