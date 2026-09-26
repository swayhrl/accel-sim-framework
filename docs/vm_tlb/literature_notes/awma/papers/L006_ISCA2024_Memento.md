# L006｜Memento: An Adaptive, Compiler-Assisted Register File Cache for GPUs

**Abaie Shoushtary、Arnau、Tubella Murgadas、Gonzalez，ISCA 2024。DOI：10.1109/ISCA59077.2024.00075。** 复核日期：2026-09-26。

## 阅读证据

来源为用户提供的`Mojtaba et al.pdf`，13页；本轮整理已读全文，并复查图5及§V/表I。SHA256：`8b89edd846f14d72a9143e9fa2ad7dcdf342be9129e2e3a240dba3fb09d317c1`。只提交原创笔记，不提交PDF或全文提取。出版入口：https://doi.org/10.1109/ISCA59077.2024.00075 。

## 原文：不是首次RF cache，而是旧方案不适应新结构

作者针对sub-core与Tensor Core条件下传统RF cache的结构/调度代价：将已有OCU改成CCU，少量增加数据槽，并结合缓存管理和单层warp调度。不同warp轮换CCU时清空旧缓存，一warp不同时占多个CCU，RF本体仍接收所有写回，因此可安全丢弃缓存。[§I–IV]

寄存器复用距离由profile辅助近似成near/far位；替换与写入策略利用此提示。动态算法按IPC区间变化调整允许暂缓CCU分配的阈值，以平衡复用与发射延误；并非证明任何情况下等待都无害。[§III-A、§IV-B]

## 实验、数字与限制

Accel-Sim trace-mode，RTX2060-like缩至10 SM，Rodinia与DeepBench，不是完整LLM服务。方法节说明给trace标注复用信息，再提供二值提示；论文不是已交付生产编译工具链的证明。[§V，表I/II]

作者报告平均IPC +6.1%、RF动态能量 -28.3%，不是整GPU能量降低28.3%；最坏b+tree有约0.8% IPC下降。[§VI]

每SM额外2KiB相对256KiB RF为0.78%，首先是**新增数据存储容量比例**，不能直接用来宣称布局面积只增加0.78%。阈值12与10000-cycle区间来自作者实验选择，不是跨负载定律。[§III-A、§IV-B、§VI-D]

## 我的比较判断与启发

可学习其论证顺序：先说明旧设计的哪项假设在新结构下失效，再给出适配，不是把旧技术放进AI benchmark就称新颖。

对AWMA它是方法参考，不是TLB最近邻。静态粗提示是否有价值，要证明它提供了纯运行时状态缺少的信息。不能先决定“compiler-assisted”再寻找可编码内容。

若未来用profile提示，必须区分训练profile与最终评估执行，冻结标注规则并检查换输入/shape后的误差。直接读取评估trace的未来复用距离只能叫oracle对照，不是已实现提示来源；本文提供的资料不足以替我们完成该泛化检验。

## Related work可用句与边界

可用：Memento以复用OCU存储、profile辅助管理与动态分配策略，研究RF缓存收益和调度机会之间的取舍。

不可用：它证明自适应等待永不回退；或者其2KiB成本可直接换算成AWMA结构面积。
