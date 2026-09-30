# R17问题卡｜成熟图检索之后的低并发在线推进

**日期：2026-09-30。状态：准备候选，不是execution Goal；没有授权GPU、下载、构图或模拟器任务。**

## 1. 要回答的问题

一个query的下一批候选地址要等当前遍历和距离比较后才能确定。在图/向量已经驻留GPU、合理single/multi-CTA以及可用persistent能力之后，这种在线推进是否仍让真实query完成时间受限？还是剩余主要是必要距离计算或host/runtime成本？

不是研究“GPU随机访存总是慢”，也不是用人为降低recall的更少搜索工作制造收益。

## 2. 与AWMA已有边界不同在哪里

R102是权重更新输入authority；VLA是完整网络VJP；CCE是累计器初始化。这些都不是图检索多轮在线候选反馈。P2的selector→consumer经验可复用，但不能代替graph traversal的测量。本次核读的最新结果清单未见这一问题的已完成Native boundary。

这只是对象不同，尚不构成新颖性或性能证据。

## 3. 必须先承认的既有能力

CAGRA论文已包含warp splitting、forgettable hash、single/multi-CTA。当前cuVS文档的persistent仅支持SINGLE_CTA；Jasper已有改进greedy search和量化/索引组织。BOA、GrAND分别覆盖自适应filtered search和动态更新，作为近邻而非首轮功能。

不同mode可能改变搜索工作/visited结构；它们的差异首先属于实现比较，不可直接当一项硬件干预。

## 4. CPU/source准备的交付物

**A. 能力表。** 固定cuVS公开commit/version和源代码位置；确认SM89构建入口、C++执行路径、低并发推荐mode、persistent限制、workspace分配与生命周期。Jasper只做同层能力核对，不先完整移植第二个系统。API存在与109已验证运行分开记录。

**B. 输入表。** 一套公开learned-embedding database/query/ground-truth。候选DEEP1M用于graph/compute-memory行为：其图像向量来源不能称自然RAG文本。原始源、dtype、维度、license、规模和query独立性都需核实。另一个来源只列为后续验证候选。允许实验室按公开规则构建并冻结index；无需作者提供我们将运行的图hash，但不得假称重现作者的exact index。

**C. 最小比较设计。** 将一次性构图/上传与逐query服务分开；保留完整request完成时间。没有真实在线到达trace时，明确并发是受控实验参数，不声称服务SLO或尾延迟。

三项合格后即足以决定是否写一条Native Goal，不另建数据平台、全模型库或全篇复现项目。

## 5. 条件性的Native最小集草案（待另授权）

一个固定静态index；同一批真实query预分发现/验证；两档并发，建议1与32，不扫描全空间。采用原始精度，先不压缩、不过滤、不更新索引。

- 主基线：针对该并发合法选择的成熟CAGRA模式；预分配可重用workspace，不以弱Python loop为基线。
- 既有能力对照：single/multi-CTA仅用于确认正确mode是否已经解决；若单独评估persistent，则保持其支持模式，不混成复合变化。
- 先冻结recall@k要求、调参集合和最多一组被文档支持的参数选择；验证query不参与选择。比较实现时不能只固定beam的数值而忽略实际质量差异。
- 第一轮只做时间、距离评价量、迭代/visited/候选维护账本。必要时才采一个时间线和一个能区分原因的NCU目标；不先抓trace。
- 小型机制/软件原型可以作为后续诊断，但不预先读取query未来访问路径，不把更少距离计算归因于更快访存。

## 6. 决策

已有mode/persistent充分：收口为软件路径选择。

主要是必要距离计算：保留事实，不自动设计cache。

明显成本只在host wrapper/分配：先软件解释，不进174。

仍有明确影响query的在线依赖/状态维护成本：回到直接近邻，提出一个可证伪的有界干预；尚无architecture admission。

证据不足：保持未知，不按失败或positive处理。5%只能作为下一阶段投入门槛；不能靠profiler占比单独通过。

## 7. 排除范围与当前状态

不做index动态更新、filtered predicates、host offload、NVMe、multi-GPU、完整RAG服务、SASS/NVBit或Accel-Sim；不继承R101的simulator sensitivity。所有已有Lane仍STOP。

来源与阅读深度见`../rounds/2026-09-30_ROUND_17_RETRIEVAL_PROBLEM_SCREEN.md`。
