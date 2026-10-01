# LR09补充：Tile级缓存模型、并发进度偏移与更近的研究边界

日期：2026-09-29。维护者：ChatGPT。

本文件与LR09主笔记属于同一轮调研。在补充检索2026年文献时发现两个已取得正文的直接近邻，以及一个仅取得arXiv原始摘要的更近工作。本轮累计核读7篇工作的相关正文：5篇新增、Stream-K从摘要升级、MARLIN复读；PASCAL和PPoPP2019 tiling/batching仍只计摘要。没有运行任何新代码或GPU/模拟实验。

主笔记：`2026-09-29_LR09_SPLITK_LOCALITY_SCHEDULING_AND_STRONG_BASELINES.md`。

## 1. TileSight：我们的“跨M共享B权重”已经是它明确建模的对象

完整标题：**TileSight: A First-Principles Tile-Centric Analytical GPU Performance Model from Cores to Clusters**。

版本：arXiv:2607.22432v1，2026-07-24，预印本。核读§3.5、§5.1–5.3及局限相关正文，不声称复现作者模型。

### 作者做法与证据

作者用tile粒度的复用距离，将数据对象、共享维度、tile遍历和swizzle连起来；B tile在M维输出tile之间复用是明确例子。§5.2以CUTLASS/CK真实测量验证算子成本，§5.3另以4,680个persistent GEMM case验证cache模型，不能将两组范围混成一张实验表。[S6]

尤其相关的是§5.3的失败例：不同SM在较深K循环中失去同步，会同时访问不同K片段，模型可能高估L2命中。作者给出H200上M=N=8192、K=28672时预测82%、实测43%的例子。总体平均准确度不能取消这个针对性的局限。[S6]

### 对C16的判断

1. “跨M的weight tile复用”“tile顺序决定reuse distance”“不用完整SASS的轻量cache模型”都不能直接当作新颖性。
2. TileSight提供一种比完整指令模拟轻的分析层次，但没有因此获得本项目4080/W4/kernel资格；不得用它绕过现有Accel-Sim拒绝准入。
3. 我们若只根据静态block-ID顺序、假设所有CTA在同一K位置，就可能在最需要解释的场景里过于乐观。
4. 若未来提出模型，需明确哪些有效缓存参数来自独立microbenchmark，哪些是待预测工作负载；不能用当前K拐点同时拟合并验证。

### 代码可获取性

本轮查到公开仓库`tile-ai/TileSight`，并核读README，显示CPU侧建模例子和GPU probe分离。论文v1说将开源，当前仓库可读是后续状态，二者不矛盾。这里只核可获取性，未安装、执行或核验作者误差结果，不宣称支持当前4080。

## 2. PASCAL：很近，但当前仅有摘要，不能补造其公式

完整标题：**PASCAL: A Phase-Aware Shared-Cache Model for Parallel Scans**。

作者：Zhongchun Zhou、Chengtao Lai、Songtao Mao。

arXiv:2609.10515，2026-09-09。

本轮从arXiv检索结果取得原始摘要；直接abstract/html/pdf入口多次获取失败，因此没有读到正文。二级摘要站只用于定位，不作为公式、算法或实验合同来源。

### 摘要明确支持到哪里

它研究多个核反复扫描共享数据时，执行进度分歧如何改变cache miss与DRAM，并提出无需目标trace/timing/counter的phase-aware模型；摘要声称具有与替换策略无关的流量界，并在GB10的60配置集合上评估。[A2]

### 必须保留的未知

- “parallel scan”的精确假设、进度模型和上下界推导：未取得正文，未核实。
- 60配置的输入/控制变量、校准与验证分离方式：未核实。
- 是否显式覆盖W4 affine metadata、mod8 split、当前AutoAWQ kernel：未核实。
- 不能把GB10上的摘要误差指标当作4080可继承资格。

### 对C16的意义

这是我们在正式主张“进度/工作集感知的cache模型”之前必须补全文的直接近邻。不能仅因为其研究问题很近，就宣布它已解决本项目；也不能忽略它，声称首次研究跨核共享扫描的进度偏移。

**本PASCAL不是之前workload调研中有关推理请求调度的Pascal（arXiv:2602.11530）。两篇名称近似、问题不同，必须按完整题名和arXiv ID区分。**

## 3. 多chiplet GEMM局部性模拟：快，但同步假设会直接影响我们的问题

完整标题：**A Fast Locality Simulator for GEMM Design-Space Exploration on Multi-Chiplet GPUs**。

作者：Euijun Chung、Hyesoon Kim。

采用arXiv:2606.11716v2（2026-06-12），核读§I–IV。先取得v1后核v2，最终以v2为准，不混用两版headline数字。[S7]

### 原文方法

模型是功能性tile级局部性模拟，研究每chiplet L2以及本地/远端HBM流量，不是精确周期模型。作者用Qwen3-30B和Llama3.1-70B的12个FFN前向/反向GEMM形状，改变布局、CTA遍历与数据放置；同一wave内CTA沿K同步前进是明确假设。作者也把2D block-swizzle称为CUTLASS/Triton已有优化。[S7]

### 对C16的判断

- 借鉴价值在于“可以只建模要回答的那层问题”，不是所有实验都要抓数亿SASS记录。
- 但其多chiplet远端流量目标与4080的共享L2容量问题不同；不能直接移植结论。
- 作者认为同步假设对其评估影响较小，不等于已经证明它适合我们；TileSight明确给出的deep-K偏差尤其需要注意。
- 不建议现在重建一套tile模拟器。先用正在执行的native干预与后续最小经典映射对照判断是否仍有未解决问题。

## 4. 补充实验组登记

| ID | 实验问题 | 实际对象与变化 | 证据层次/限制 |
|---|---|---|---|
| E10 / S6 | tile模型能否预测GEMM时间 | 703个BF16/FP16形状；多个NVIDIA架构，另有MI210 | 真实库测量对比模型；正文说明NVIDIA时间验证过滤Stream-K/SIMT fallback，不等于验证本项目split8 |
| E11 / S6 | tile复用距离能否预测L2命中 | 4,680个persistent GEMM case；有效容量经单独带宽扫校准 | 作者真实NCU对照；deep-K SM进度偏移存在明确反例；未在本项目复现 |
| E12 / S7 | 布局、CTA遍历和data placement怎样影响远端流量 | 12个LLM FFN相关BF16 GEMM形状；MI300X-like抽象拓扑 | 功能模型输出，不是实机速度；wave-lockstep为明确假设 |
| E13 / A2 | parallel scans的进度分歧如何影响cache | 摘要称GB10、60配置，含pipeline depth/occupancy/datapath变化 | 仅摘要；不能登记为已核实验合同或已复现误差 |

E10–E13是本轮整理的记录名，不是作者原文实验名称。E13明确不算正文实验核对完成。

## 5. 更新后的研究判断

LR09主笔记提出的“经典tile映射强基线优先”保持不变。新增近邻进一步说明：

> 有必要同时分析split、tile遍历、活跃工作集和CTA进度；但这个联合视角本身已经有文献基础，最终贡献必须是已有优化/模型仍未解决的具体能力或成本问题。

目前不应把下一步定义成“做一个预测cache miss的模型”或“再做一个自适应split选择器”。更合理的是先区分：

1. 原AutoAWQ的方向翻转是否主要由普通tile映射即可修复；
2. 经过这种强对照，是否仍存在split、partial归约、metadata布局与有效容量无法兼顾的明确限制；
3. 该限制能否在未参与发现过程的shape、数值输入或另一合法后端复现。

无论本轮搜到多少近邻，当前跨M共享实验都继续按原合同完成，不中途改变它来追逐论文表述。

## 6. 原始来源与阅读范围

### S6
https://arxiv.org/html/2607.22432v1

关键定位：§3.5的tile reuse keys/顺序；§5.2的703形状时间实验；§5.3的4,680 persistent案例和82%/43%失败例；§7局限。没有采用二级中文解读作为证据。

公开仓库： https://github.com/tile-ai/TileSight

README读取blob另记于GitHub回读记录；仅核代码公开入口，未执行。

### A2
https://arxiv.org/abs/2609.10515

本轮能取得的是arXiv原始摘要的检索记录，全文获取失败。应请求完整PDF再核假设、方法和评估，不能用第三方生成摘要填补。

### S7
https://arxiv.org/html/2606.11716v2

v1的90倍headline在v2调整为58倍，本文不利用这些headline作任何本项目性能判断。最终采用v2方法与局限；其正文仍有版本遗留数值的可能，不能自行调和。

### S3补充作者说明
https://github.com/IST-DASLab/marlin/blob/master/README.md

读取blob：`ae24af61fed1ede9f06ca8f3b3b2985a1d93f12a`。README明确描述activation经L2、weight低保留加载和striped partitioning；与主笔记MARLIN正文互证，不代表执行了该库。

本补充只增加文献记录，不授权任何新实验、模型安装、SASS或模拟器任务。
