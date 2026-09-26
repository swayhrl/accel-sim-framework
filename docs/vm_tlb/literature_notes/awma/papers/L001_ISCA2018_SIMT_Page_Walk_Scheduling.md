# L001｜Scheduling Page Table Walks for Irregular GPU Applications

**Shin等，ISCA 2018。DOI：10.1109/ISCA.2018.00025。** 复核日期：2026-09-26。

## 阅读证据

作者提供的[原文PDF](https://www.csa.iisc.ac.in/~arkapravab/papers/GPU_page_walk_scheduler_ISCA_18.pdf)。本轮核查§II-B、§III、§IV、§V-A；PDF第6页图7及设计文字已视觉复查。不是本轮逐句重读整篇，未复现实验。

## 原文：问题、增量与实现

同一SIMD访存指令的多个walk可能被其他指令的请求穿插；完成部分walk不等于该指令完成。作者把指令的翻译工作作为整体，提出SIMT-aware page-walk scheduling，而不是只提高单个walk吞吐。[§III-A/B]

有空闲walker时直接服务；发生排队后，优先继续最近服务的同一指令，否则选择预计剩余访存工作最少的指令。请求带instruction ID；PWC状态用于估计工作量，估计并非未来真实延迟。还用小计数器辅助保留待处理walk将需要的PWC条目。[§IV，图7]

评估采用gem5执行驱动的集成GPU环境、规则与不规则负载，而非LLM推理。已有同指令同页合并属于其基础翻译路径。[§II-B、§V-A]

## 我的比较判断

这是AWMA“最后一个未完成页组影响指令进度”的直接近邻。不能把“最后一项最关键”当作新洞察；但也不能据此宣称所有L1端口仲裁规则都被该论文实现了——它的主要决策点在IOMMU/PTW待处理队列。

比较新候选要回答：操作的是尚未进行L1服务的请求，还是已双级miss的walk？观察的是实际当前head阻塞，还是整条指令预计工作量？这一区别若没有独立收益，仅换位置不足以构成贡献。

## 待验证问题／复现入口

先查强基线后是否真的存在多页指令、同指令walk交错及进度暴露。若没有walk排队，不应为复现此调度器而人为缩小walker资源。

若存在：最近邻对照应保留同指令批处理、PWC估计与公平/等待代价；不使用最终完成时间充当运行时分数。本文不提供AWMA可直接运行的移植代码或原始实验receipt。

## Related work可用句与边界

可用：Shin等以SIMT指令为单位组织与调度page walks，使翻译服务顺序更符合指令整体完成需求。

不可用：此前所有工作只关注TLB miss数量；或者此前无人考虑最后一个walk对进度的影响。
