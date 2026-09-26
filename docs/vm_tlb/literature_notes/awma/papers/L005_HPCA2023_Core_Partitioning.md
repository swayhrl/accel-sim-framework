# L005｜Mitigating GPU Core Partitioning Performance Effects

**Barnes、Shen、Rogers，HPCA 2023。DOI：10.1109/HPCA56546.2023.10070957。** 复核日期：2026-09-26。

## 阅读证据

[作者PDF](https://engineering.purdue.edu/tgrogers/publication/barnes-hpca-2023/barnes-hpca-2023.pdf)。本轮核§III、§IV、§V及结果解释；PDF第4页图5/6、第6页映射与方法文字已视觉复查。未复现实验。

## 原文：问题、增量与实现

SM分区会让每个warp可用的RF bank、operand collector和调度资源变少。作者研究寄存器bank冲突及子核间工作不平衡。[§III]

RBA依据ready指令源操作数所属bank的待处理队列长度评分，分数相同时按年龄选择；另以warp-to-subcore映射减少某些子核过载。它们分别作用于发射选择和更早的工作归属，不能合并称为一种“优先级”。[§IV，图6]

原文结合真实GPU微测试与Accel-Sim多套负载。TPC-H采用缩小的模拟GPU；SRR映射带有特定warp模式的设计依据，另有Shuffle方案。不能把这些条件省去后宣称所有应用通用。[§IV-B、§V]

## 我的比较判断

这是Memento的直接前序之一，也是AWMA非翻译侧瓶颈解释的重要参考，但当前没有证据说AWMA已被RF bank卡住。

研究启发是“先找对决策层级”：若限制来自warp最初分到哪个子核，单靠子核内每周期调度未必能解决；若来自取操作数拥塞，继续增大TLB并不对症。这是可迁移的问题分析方式，不是新的机制贡献。

## 待验证问题／复现入口

Observatory若报告execution structural pressure，需要继续辨认RF读、OCU占用、执行单元忙以及调度域不均。只见整体FU利用率低，不能确定应扩大资源。

若进入RF方向，至少比较RBA而非只比较GTO。不可把“挑空闲bank/短队列对应warp”改称AI-aware新机制。若仅在特定warp编号规律下获益，应留出不同映射/形状的验证，避免针对benchmark布局定制。

## Related work可用句与边界

可用：该工作揭示GPU子核化改变资源可见范围，并分别从寄存器bank感知调度和warp分配缓解影响。

不可用：首次发现现代GPU分区会造成资源不均，或首次提出bank-aware warp选择。
