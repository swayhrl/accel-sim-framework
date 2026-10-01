# C16文献支线LR02：从容量公平到跨轮复用存活

日期：2026-09-27。维护者：ChatGPT。状态：定向文献核读与研究判断；不是实验准入、机制实现或性能结果。

本轮沿用此前文献笔记的原则：作者陈述、项目事实、我们的推断、待验证假设分开。不改Lane 1B/Lane 4，不新开GPU或timing任务。LR02表示接续此前聊天中的C16文献讨论，不表示此前已经发布过同结构的LR01文件。

## 1. 范围、阅读深度和证据入口

本轮登记9项研究工作（DIP会议论文与其IEEE Micro延伸放在同一条目）、2份NVIDIA官方文档、1份Marlin作者实现说明。其中Vantage、Talus、AutoScratch、PRESERVE取得正文并核读相关机制、评估设置或限制；其余研究条目停留在原始摘要、作者机构说明或作者项目介绍，不能称全文精读。未复现任何论文代码。另有PIPP、RRIP、APCM等列入后续队列，不能算已读完。

项目引用快照：
- Lane 1：`4214398782159022907081dbcc36854cf21fb4b5`，`C16_E1_TRACE_REUSE_SET_PRESSURE_CHARACTERIZATION_174NEW_V1/SCIENTIFIC_INTERPRETATION.md`。
- Lane 3：`a402828860ced26124ddbf3c9d87baa6f6774d55`，`C16_E1_PAPER_EVIDENCE_AND_RESULT_INFRASTRUCTURE_V1/RELATED_WORK_INDEX.md`。
- 既有AWMA文献分支的README用于参考阅读分级和记录方式，不将AWMA的结论、实验或论文数量移植成C16成果。
- 本轮没有读取Lane 4未闭合输出来选择解释。其完成状态以独立执行报告为准。

### 核心结论

**当前最值得追问的不是“怎样让28层平均分缓存”，而是“有限保护容量能否让一部分具体权重行活到下次真正有价值的复用”。** 层间均衡、行级存活、系统周期收益是三个不同问题。

这既提供新研究问题，也收紧新颖性判断：共享缓存分配、抗扫描插入、地址采样、软件标注关键对象都有直接先例。不能把“elastic + class quota + region tag”这一组名称当成已经成立的创新。

## 2. 逐项阅读记录

### P01｜Utility-Based Cache Partitioning（UCP），MICRO 2006

作者：Moinuddin K. Qureshi、Yale N. Patt。深度：原始摘要的高校转载，以及SIGMICRO官方获奖说明；未取得可用全文。

**作者内容：**按照增加缓存能够减少多少miss来分配资源，而不是按请求需求量分配；提供低成本运行时效用监测。[S01]

**与我们的关系：**“最近访问多，所以应多占缓存”不合理，早已有系统研究。LLM各层属于同一请求，层间等份并非最终目标；是否减少完整decode时间才是目标。这是由UCP原则得到的项目推论，不是UCP已经评估了LLM。

**不可声称：**UCP证明平均分层容量最优；或我们首次提出utility-aware cache allocation。

### P02｜Adaptive Insertion Policies for High Performance Caching，ISCA 2007；IEEE Micro 2008延伸

作者：M. K. Qureshi、A. Jaleel、Y. N. Patt、S. C. Steely Jr.、J. Emer。深度：会议论文原始摘要转载、IBM作者机构延伸论文摘要；未逐段核读会议全文。[S02]

**作者内容：**LIP改变新行插入位置；BIP允许少量高优先级插入以适应工作集变化；DIP用set dueling在策略间选择，针对超容量工作集的thrashing。

**与我们的关系：**“大循环工作集下应保住一部分旧数据，而不是每次都优先接纳新数据”不是新发现。若M1的收益仅是抗扫描，最终不能只对比朴素LRU。

**边界：**不能把BIP的按插入事件选择与按地址稳定选择视为同一算法；未来移植前需核完整原文和确切参数。

### P03｜Vantage: Scalable and Efficient Fine-Grain Cache Partitioning，ISCA 2011

作者：Daniel Sanchez、Christos Kozyrakis。深度：作者PDF，重点§2、§3.1–3.3及实现/评估边界。[S03]

**作者内容：**分离容量分配策略与落实分配的机制；通过替换控制实现细粒度分区，以managed/unmanaged逻辑区域及churn控制缓解分区干扰。明确指出，只允许替换同一分区候选会随分区数增加而损失有效相联度。

**与我们的关系：**对应M1的“总quota合法，但当前set没有合适protected victim”。这一类执行约束已有近邻。

**边界：**Vantage依赖良好散列/较高候选相联度，允许围绕目标分配的受控波动；不能把它直接等同于本项目每次resident+pending硬上限与16-way set-local规则。

### P04｜Talus: A Simple Way to Remove Cliffs in Cache Performance，HPCA 2015

作者：Nathan Beckmann、Daniel Sanchez。深度：作者PDF，重点§I–IV、§V-C、§VI；核对评估属于CPU缓存模拟。[S04]

**作者内容：**用shadow partitions和地址散列分流，使分配容量呈现更平滑的miss收益曲线；显式处理循环扫描的容量“悬崖”。论文区分真正bypass与低优先级插入，也指出按地址采样与按事件抽样的不同。

**与我们的关系：**这是本轮最直接的新启发：即使每层拿到等份容量，只要每层内部仍把超容量循环工作集全量admit，依旧可能没有跨轮命中。要区分“给谁多少空间”和“让哪部分地址留下”。

**边界：**Talus不等于简单固定子集pinning；它依赖miss曲线与模型假设，其CPU结论不能当作GPU效果或我们的原创。

### P05｜SHiP: Signature-Based Hit Predictor for High Performance Caching，MICRO 2011

作者：Carole-Jean Wu等。深度：作者机构原始摘要；原文PDF链接本轮超时，未以二手介绍补作全文结论。[S05]

**作者内容：**以memory region、PC或指令历史等signature关联复用行为，学习不同signature的插入预测。

**与我们的关系：**“给不同语义/地址组不同cache待遇”和“用region而非完整PC识别”有明确先例。未来加入分类器不能仅凭换成qweight或layer ID声称创新。

**边界：**AutoScratch附录的SHiP-SW属于该文的扩展对照，不与原始SHiP混为同一实现。

### P06｜AutoScratch: ML-Optimized Cache Management for Inference-Oriented GPUs，MLSys 2023

作者：Yaosheng Fu等。深度：会议正文§2–4及附录A.1–A.2，包含L4实机与模拟对照的区分。[S06]

**作者内容：**用学习/搜索选择推理数据的L2驻留配置。附录还实现SHiP-SW：软件提供性能关键地址区域，硬件针对这些signature学习驻留，并讨论“有命中”不等于“对性能同等重要”。

**与我们的关系：**它比仅看摘要时更接近：软件region、关键性与硬件驻留的组合已经出现。不能把它只写成一个搜索baseline而忽略SHiP-SW。

**边界：**原文关于weights复用有限的叙述限定在一次iteration的不同层之间，不能改写成“作者认为weights永不复用”。附录的实机/模拟校验是DRAM流量，不等于周期误差。

### P07｜PRESERVE: Prefetching Model Weights and KV-Cache in Distributed LLM Serving，arXiv 2025 v1

作者：Ahmet Caner Yüzügüler、Jiawei Zhuang、Lukas Cavigelli。深度：v1正文§3–4，未将该版本冒充最终会议稿。[S07]

**作者内容：**把weights/KV预取到L2，与allreduce等待重叠；图级插入预取时考虑L2容量。实测平台是Ascend 910B NPU。

**与我们的关系：**证明“LLM weights/KV进入L2以改善推理”已有直接工作。其主要时间尺度是使用前预取，不等于跨完整token周期保留同一部分权重。

**边界：**不是NVIDIA GPU eviction/persistence实现的实测，也不能直接套用其性能数值。

### P08｜Security and Performance Implications of GPU Cache Eviction Priority Hints，MICRO 2025

作者：Qizhong Wang、Xiangyue Huang、Yanan Guo、Yuanchao Xu。深度：作者主页、作者实验室研究说明；本轮未取得可核读的论文全文。[S08]

**作者内容：**研究NVIDIA GPU eviction hints的实际行为，报告预期保留的evict_last可能引发thrashing和退化。

**与我们的关系：**“提高优先级可能适得其反”不能宣称首次发现。需要把接口语义、具体硬件实现、我们模拟的规则分开。

**未核实：**具体GPU/driver全矩阵、阈值、缓存内部推断细节和相应图表。不得从自动生成的论文解读补数。

### P09｜Cache-Resident LLM Inference in GB-Scale Last-Level Caches，arXiv 2026 v1

作者：Wanning Zhang、Tongzhou Gu、Marco Canini、Ceyu Xu、Jian Weng。深度：原始摘要与版本元数据。[S09]

**作者内容：**在GB级CPU LLC场景，将weight-centric执行与attention/KV管理分开，并处理驻留后暴露的同步开销。

**与我们的关系：**“cache-resident LLM”已不是空白概念；还提醒缓存更快可能使其它成本成为主导。

**边界：**CPU/GB级缓存和执行组织，不是我们的64MiB GPU L2替换规则。摘要提到部署结果及模型预测，两者不合并；本轮不复述其性能数值。

### D01/D02｜CUDA L2 Cache Control与PTX ISA官方文档

深度：CUDA Programming Guide §4.13.1–4.13.5；PTX §9.7.9.2、§9.7.9.19，2026-09-27访问。[S10][S11]

**接口事实：**普通/streaming数据可以利用尚未被persisting数据占用的set-aside空间；hitRatio规定的是获得属性的比例/概率。PTX已有range/fractional eviction policy。

**必须修正的口径：**“CUDA完全静态割走容量，而我们首次允许借用”不成立。`hitRatio=1/28`不证明每层实际占用严格相等，更不证明固定地址子集跨token不变。文档没有为本项目提供这种保证。

**对照要求：**native BFULL的requested与actual预算、M1的硬quota分别报告；接口启发的模拟对照不能命名为NVIDIA真实内部实现。

### I01｜Marlin作者README

深度：作者仓库的Techniques与适用说明；只读实现文档，未复现kernel。[S12]

**实现说明：**通过cache policy使weight loads容易驱逐，减少L2污染，同时保留activation与输出buffer的局部性。

**与我们的关系：**这是一个有解释力的反向基线：在其执行范围内，weights按streaming处理可能合理。不能据此推导所有低比特后端都这样，更不能把我们的AWQ trace当作Marlin trace。

## 3. 本轮对现有想法的修正

### 3.1 公平是候选手段，不是最终优化目标

UCP关注资源效用；AutoScratch/SHiP-SW也已经考虑不同对象对性能的重要性。对于同一个decode请求，28层不是28个独立租户，不存在天然的“每层应分到相同字节数”的系统目标。[S01][S06]

我们需要区分：
1. 资格：哪些地址允许申请保护；
2. 配额：各对象能占多少；
3. 存活：哪些具体行在目标reuse前仍然保留；
4. 效用：这种保留实际节省了多少完整区间周期，付出了什么其它成本。

当前M1回答第一项及总量约束，尚不是一个已经测量边际周期效用的自适应控制器。因此可以称occupancy-bounded residency prototype，不宜仅凭名称就说已经实现cost-aware optimal allocation。

### 3.2 即使类间完全公平，类内仍可循环抖动

以下是我们的数学反例，不是C16实测，也不是Talus性能复现。

令每类循环访问S条不同cache line，给每类q条独占配额，0<q<S。若每个新行都admit，且类内LRU，则再次访问某行前已经经过S−1条其它行：从冷启动反复扫描时，稳态仍然可以全部miss。

反之，若明确只让固定q条地址进入保护区，其它行不能挤掉这部分，在无额外干扰等理想假设下，预热后可使q/S的访问命中。这个构造只证明“相同份额可以有不同复用实现”，不保证当前GPU能免费实现该策略。

附带的`toy_scan_counterexample.py`使用两个类、每类8行、每类容量2行；class quota + LRU为0/16，固定子集保护为4/16。两者在轮次边界每类都占2行，但命中不同。该例刻意简化掉sector、L1过滤、MSHR与请求时序，不用于定量预测。

抗扫描插入和地址分流已有DIP/Talus等先例。因此“固定一些权重行”首先应作为文献启发的诊断对照，不直接命名为新发明。[S02][S04]

### 3.3 稳定的line选择，不等于每次重新抽签

需要独立定义：按地址散列固定保护资格；按每次访问抽签；按每次miss/插入事件抽签；按class份额控制。它们对长期存活的影响不同。Talus明确区分地址采样和事件式插入；CUDA/PTX概率属性不能由我们自行解释成稳定子集。[S04][S10][S11]

### 3.4 均衡静态映射并不解决容量落实问题

Lane 1的静态结果说明每层覆盖全部sets，没有明显placement skew；它没有证明实际填充后class分布均衡。B16平均只有4条protected line/set的容量尺度，而class有28个。这个平均值不是per-set硬配额，但足以说明不能要求“每个set里同时公平保留全部28类”。

Vantage早已讨论分区数增长与同分区victim约束的冲突。我们的新颖性必须来自具体约束下的增量能力，而不是首次意识到“局部victim可能不存在”。[S03]

### 3.5 protected_hits不自动等于跨token保留收益

同一次up_proj内部的重复访问可以产生命中；先前token留下的行也可以产生命中。仅见protected occupancy高、protected_hits多或local timing改善，不能独立区分两者。

后续解释Lane 4应尽量绑定“前一轮的地址身份/保留世代→下一次同地址访问”，或使用能够隔离历史驻留贡献的对照。当前已有counter不足时标未辨识，不把aggregate活动命名为cross-token survival。

这不推翻native局部收益；它只是收紧收益来源的归因。

## 4. 新颖性碰撞表

| 拟用概念 | 直接近邻 | 当前定位 |
|---|---|---|
| unused protected capacity可借用 | CUDA L2官方机制；Vantage逻辑区域 | 不是独立创新 |
| 每类soft quota / cache fairness | UCP/Vantage；PIPP待全文 | 不是独立创新 |
| region/software语义标记 | SHiP；AutoScratch SHiP-SW | 不是独立创新 |
| 保住一部分超容量循环工作集 | LIP/BIP/DIP；Talus | 不是独立创新 |
| 按地址稳定分流 | Talus | 不是独立创新 |
| 权重/KV放进L2改善LLM | PRESERVE | 不是独立创新 |
| 高优先级造成干扰或thrashing | CUDA指导；MICRO'25作者说明 | 一般现象已有先例 |
| 低比特decode的有限容量、跨轮存活与系统机会成本关系 | 当前C16证据+尚待区分的假设 | 值得研究，未证明新颖性 |

“未在本轮读到完全相同工作”不等于“首次”。本轮不是穷尽性检索，也没有宣称我们已有强会议论文结论。

## 5. 最小研究问题与停止条件

### H1：主要问题是否真是target-target竞争？

看后续已接受的class occupancy与protected→protected replacement，但不能仅以总替换数判因果。如果class份额本来均衡且旧行存活良好，不能继续把class fairness当解释。

### H2：平均份额是否掩盖了类内地址不断更新？

对比class occupancy和同地址跨轮存活。若份额健康而旧地址全部更新，应先检验抗扫描/稳定准入，不必先加复杂class控制器。

### H3：最接近的旧方法是否已经足够？

在完成Lane 4后，从文献中选一个有确切实现合同的抗扫描基线，再选一个明确标为诊断的稳定子集方案。先回答有没有超出这些已知能力的剩余问题，不同时完整复现所有论文。

若已知简单策略在相同约束下已覆盖收益，当前M1保留为参考机制，不继续以改名方式挽救创新。

### H4：保留的收益能否超过代价？

先确认旧行确实存活，再看目标周期、完整reuse window周期及其它流量代价。低miss或高保护率不能替代system metric；本轮窗口也不能宣传成full decode speedup。

## 6. 对当前Lane的影响

Lane 4保持原binary、trace、quota与测量范围；本轮没有准许新增长跑。Lane 1B可以把本笔记作为只读研究背景，fairness仍是假设，不是预设结论。Lane 3下一版需补入近邻，特别是AutoScratch附录SHiP-SW与Talus，并删除“只差一次B16正收益就证明创新”的暗示。

暂不优先添加动态分类器：权重地址语义已经可用，先证明已有信息下的驻留策略具有增量价值。也不把本轮变成CPU缓存论文的全套复现项目。

## 7. 后续阅读队列与本轮检索限制

优先补全：DIP、UCP、SHiP原始全文；MICRO'25 eviction hints全文和具体平台；PIPP、RRIP以及GPU APCM原文。之后再看MLP/关键路径感知缓存管理，核“节省miss不等于节省周期”的最近邻。

检索还遇到`AscQLUT: A decode-fused INT4 GEMM Kernel for Ascend NPUs`出版社摘要页线索，但页面未成功展开，未将搜索摘录升级为机制核读或C16对照结论。

Vantage与AutoScratch相关页面完成PDF截图复核；Talus部分截图请求失败，关于其采样规则依据可解析正文，不做依靠图柱高度的数值推断。所有论文PDF仍归原作者/出版社，本资料包不重新分发原文。

## 8. 可追溯来源

[S01] UCP，MICRO 2006。原始摘要转载：https://sites.cc.gatech.edu/systems/architecture/arch-beer/spring2007/mar30.html ；SIGMICRO官方说明：https://www.sigmicro.org/awards/tot/ 。

[S02] Adaptive Insertion Policies，ISCA 2007。原始摘要转载：https://sites.cc.gatech.edu/systems/architecture/arch-beer/fall2007/nov9.html ；作者机构IEEE Micro 2008延伸：https://research.ibm.com/publications/set-dueling-controlled-adaptive-insertion-for-high-performance-caching 。

[S03] Vantage，作者全文：https://people.csail.mit.edu/sanchez/papers/2011.vantage.isca.pdf 。定位§2、§3.1–3.3。

[S04] Talus，作者全文：https://people.csail.mit.edu/sanchez/papers/2015.talus.hpca.pdf 。定位§I–IV、§V-C、§VI；地址散列实现位于PDF第7页§VI-B。

[S05] SHiP，作者机构原始摘要：https://istc-cc.cmu.edu/publications/papers/2011/SHiP_abs.shtml ；DOI 10.1145/2155620.2155671。

[S06] AutoScratch，MLSys会议全文：https://proceedings.mlsys.org/paper_files/paper/2023/file/9d32b9324a89001520ae456b9e5ec73b-Paper-mlsys2023.pdf 。定位§2–4与附录A.1–A.2；SHiP-SW在PDF第16–17页。

[S07] PRESERVE，明确使用arXiv v1：https://arxiv.org/html/2501.08192v1 。定位§3、§4。

[S08] GPU eviction hints，作者书目：https://qizhong-wang.github.io/ ；作者实验室摘要：https://cuda.fail/ ；DOI 10.1145/3725843.3756116。

[S09] Cache-Resident LLM Inference，arXiv v1原始摘要：https://arxiv.org/abs/2606.25353v1 。

[S10] NVIDIA CUDA Programming Guide，L2 Cache Control：https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/l2-cache-control.html 。

[S11] NVIDIA PTX ISA，Cache Eviction Priority Hints / createpolicy：https://docs.nvidia.com/cuda/parallel-thread-execution/index.html 。

[S12] Marlin作者README：https://github.com/IST-DASLab/marlin/blob/master/README.md 。本轮读取blob SHA：`ae24af61fed1ede9f06ca8f3b3b2985a1d93f12a`；只读文档，不代表核验所有fork或后端。

---

本轮结论：继续研究，但把问题从“如何公平分容量”推进为“如何把有限容量转成真实复用存活与净周期收益”，并明确对比已有抗扫描、细粒度分配和软件辅助驻留能力。是否形成新机制，仍由后续可证伪实验与最近邻增量决定。
