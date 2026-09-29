# LR10：强软件基线之后，表示转换与跨算子交接还剩什么问题？

日期：2026-09-29。维护者：ChatGPT。状态：文献与候选问题设计，不授权实验。

本轮读取文献分支基点`38d4df40b615625c15d1843a69a23eb954ac0bef`，回读README、LR06和LR09B后检索原始来源。重点核对5篇论文的相关正文与NVIDIA官方架构说明；不声称逐页完整复现，不把复读、获取失败计作新增全文。

## 0. 项目边界

采用用户报告：Lane7完成CPU-only来源更正`c17c22ba00c3e1be540b165900c57de4090bd50f`，Lane6进入正式独立消费。本轮没有独立重验109实物或Lane6结果。Lane4原长跑不动、不读partial；M1F full timing仍未授权。旧split/cache故事不重开。没有修改实验branch/Core/config/trace/raw，没有运行GPU、模拟或作者artifact。

## 1. 主要判断

第一优先候选：**固定量化语义与强kernel基线以后，同一权重片段的转换结果能否在有限范围内复用，而不被展开后的带宽、容量和同步代价抵消？**

第二候选：**相邻算子保留各自高效计算布局时，不同tile粒度之间的数据交接是否仍有无法低成本兼顾的限制？**

两项都尚未证明在C16存在，更未完成穷尽性新颖性确认。它们是下一项小型决策研究的候选，不是已经成立的机制或新的GPU排队表。

## 2. 本轮原文核对与反例

### S1 Kitsune：空间数据流已有，交接不是免费

arXiv:2502.18403v1，重点§4–6。L2同步队列连接不同算子的CTA，并修改grid scheduler实现异质阶段重叠。队列微基准有实机测量；五个应用的主要效果来自修改后的NVArchSim。小payload同步代价、buffer限制，以及LL-TOK很小的流量收益，不能被总体加速掩盖。不能将队列、空间融合或资源分配本身称为新能力。

### S2 VTC：消除搬运也可能损害计算kernel

arXiv:2604.09558v2，OSDI2026会议入口，重点§2、§6、§7.5/Table3–4。virtual tensor用索引映射替代物理搬运，其实现利用编译期已知映射专门化。对vLLM的H100对照会自动跳过负优化；强制相关映射反而退化，涉及原cuBLAS与替换后Triton计算路径差异。表3的end-to-end为完整decoder layer，不是完整多层模型。该反例提示成本冲突，但不证明硬件缺陷；更好的库集成仍可能解决。

### S3 ComFuse：有限工作量与阶段失衡仍要计入

arXiv:2608.03537v1，重点§III、§VI。Stage-Stream融合复杂MatMul epilogue并扩展B2BGEMM，涉及DSMEM/TMA。评估是子图微基准，CUDA Graphs、50次warmup与500次测量。小规模时流水难以进入稳态，协调成本和阶段失衡会限制收益。不能把它输给强attention路径的例子解释成所有软件都无法解决。未明确核出的GPU SKU不补成H100，也不继承为4080资格。

### S4 StreamDQ：内存侧DQ已有直接近邻

arXiv:2607.08993v1，重点§2–6。DQB位于定制HBM base die的pseudo-channel读路径，权重与scale/zero限定本地。§5.2为实机基线、转换trace模拟与NSYS权重下的系统收益估计；不是已流片HBM的实测收益。§6.3保留小batch时AWQ-v2略优的反例。本文没有读到足以独立重建紧凑/展开表示在每级GPU cache驻留规则的说明，不替作者补出具体cache行为或缺陷。

### S5 Multi-Scale Dequant：改算术合同不是直接替换旧kernel

arXiv:2605.13915v1，重点§5–6。activation分解为多个低精度分量，通过多次低精度GEMM和重建替代权重DQ。精度证据主要是NumPy/PyTorch数值模拟；性能分析依赖吞吐、利用率和融合假设。误差相对FP32更小不等于与旧AWQ逐bit一致，更不是4080实机加速证明。

### S6 Rubin官方说明：tile-ready触发本身不能主张新颖性

NVIDIA技术博客的“Improving kernel execution efficiency”已介绍tile级producer–consumer依赖触发。这是官方能力说明，不是本项目独立ISA、微基准或成本验证。“数据一就绪就启动consumer”不能单独作为新贡献。

## 3. 第一优先候选卡：转换结果复用与展开成本

### 待区分的问题

地址集合复用、转换工作重复、重复工作暴露到关键路径是三层证据。C16跨M实验只提供选题依据，不能自动推出后两层。要核查同一片段的解包、scale/zero、类型转换与operand重排究竟在哪一级重复，哪些能被现有强布局/流水消除。

最近邻边界：MARLIN/QUICK/FLUTE已有软件数据流能力；StreamDQ已有memory侧DQ；FIGNA/MSD/Anda涉及算术或表示路径。当前问题不能退化成给这些能力改名，也不能用重新量化的模型冒充同一解码权重。

### 可证伪假设

在短生命周期、有限consumer范围内，共享一次转换结果所节省的暴露工作，大于发布、读取、同步、分发和展开表示的资源机会成本。

不是预定设计一个“DQ cache”。结果身份必须含权重、scale、zero、格式、舍入和operand布局，不能只按qweight地址匹配。各项成本可能重叠，数量账本不是可相加的时延模型。

### 最小合同草案，未授权执行

先复用Lane5已有数据流表，只补一个实质缺口：语义兼容的强kernel中是否仍存在目标重复转换。不要重新跑up/down×M1/M256初筛。

只有该缺口成立，才设计一个发现样本与一个预先固定的独立验证样本。旧K/M发现点不改称holdout。对照分开：

1. 语义兼容的强融合低比特kernel，作为参考；
2. 相同解码权重预展开后的计算，仅作诊断：footprint、访问量和kernel改变，时差不是纯DQ成本或免费上界；
3. 有界转换复用，计入转换及全部交接成本，检查净价值。

表示转换逐bit一致与GEMM归约输出要求分别冻结，不忽略归约变化，也不人为制造无人需要的数值约束。

停止条件：强软件已消除重复；重复被隐藏；仅免费预展开有收益；真实有界共享被膨胀/同步抵消；收益依赖改变量化函数；或近邻已在同约束下解决该能力缺口。

## 4. 第二候选卡：保持高效计算布局的异构tile交接

要检查producer/consumer各自高效tile形状和线程组织不一致时，省中间物化是否迫使一方变慢，或者用轮询和驻留CTA占去有用资源。

不是再提通用融合、virtual tensor、tile-ready触发；这些已被S1/S2/S3/S6覆盖。潜在增量必须同时说明交换格式、粒度、buffer容量、同步、阶段资源与有效工作量。

只考虑一个确有成本的pair。不能因为QKV→attention易说明就直接选它，也不预设单token decode价值大；VTC/vLLM已优化很多该类搬运，Kitsune也提供小流量收益反例。

合同草案：保留各自快kernel的分离执行；最强合法融合/virtual-tensor；有界队列且尽量不改双方计算布局；另一个预冻结pair/粒度验证。计时覆盖完整pair，payload和控制请求分开，不能把不同kernel时间差直接叫交接成本。

停止条件：更好的库集成即可解决；普通融合/队列已足够；正结果只来自弱producer；实际所需能力仅为Rubin已公开触发；或需要先换整个平台才能验证尚未成立的现象。

排第二的原因：它更容易扩大为编译器与调度大工程。当前4080不能直接验证全部新架构能力，既有模拟器也未因此取得新数据流范围资格。

## 5. 保留主线，关闭旧分叉

不追加split/GROUP_M/K/N/M扫描，不以phase divergence为名立刻开发cache模型，不重开旧OLMoE周期/广播/KV展开trace挖掘，不再堆replacement predictor等待正结果。TileSight已有相近问题；PASCAL全文仍缺，不能凭其摘要公式化或忽略它主张首次。

Lane4继续回答跨token有用旧行的存活和系统机会成本。该主线与本轮表示/交接候选不能互换结果或授权。AWMA数值归约/在线稀疏选择等已有候选只识别交集，不重复登记为C16首次发现，不接管活动任务。

下一步建议只把第一候选压成一个低成本决策入口；第二候选保留。不同时建两套基础设施。没有新的GPU、SASS或模拟任务。

## 6. 原始来源与阅读等级

S1: https://arxiv.org/html/2502.18403v1
S2: https://arxiv.org/html/2604.09558v2
S2会议入口: https://www.usenix.org/conference/osdi26/presentation/hu-muyan
S3: https://arxiv.org/html/2608.03537v1
S4: https://arxiv.org/html/2607.08993v1
S5: https://arxiv.org/html/2605.13915v1
S6: https://developer.nvidia.com/blog/inside-nvidia-rubin-gpu-architecture-powering-the-era-of-agentic-ai/

仍未完成全文核读：
- PASCAL: https://arxiv.org/abs/2609.10515 —— 原始摘要定位，HTML/PDF获取失败。
- ATLAS: https://zenodo.org/records/21782951 —— 作者摘要/metadata，正文获取失败。
- Leeway: https://www.research.ed.ac.uk/en/publications/leeway-addressing-variability-in-dead-block-prediction-for-last-l/ —— 机构摘要/书目，manuscript获取失败。
- FIGNA: https://doi.org/10.1109/HPCA57654.2024.00064 —— IEEE原始摘要及章节定位。
- Anda: https://arxiv.org/abs/2411.15982 —— 原始摘要。

MonoMoE、FlashQuant、Neptune、Tawa、Entwine及tile-level MoE通信工作仅作为邻近线索，没有用第三方AI概述填补未取得的正文，不计全文、不作为已穷尽排除的证明。

完整细化报告作为本轮对话Markdown附件交付；本文件是远端可接续研究记录。文献数量不替代实际收益和新颖性验证。PASCAL/ATLAS/Leeway全文缺口继续保留，不伪装已补齐。
