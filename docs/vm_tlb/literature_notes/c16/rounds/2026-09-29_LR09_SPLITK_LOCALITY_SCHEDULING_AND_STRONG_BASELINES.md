# LR09：Split-K、跨CTA复用、执行顺序与强基线

日期：2026-09-29。维护者：ChatGPT。

本轮只做文献、公开源码和已有项目证据核读。没有GPU执行、模型下载、SASS采集、模拟或作者artifact复现；不读取Lane4 partial，不修改正在执行的跨M地址共享实验。

## 0. 阅读起点与当前决策

本轮先读取文献分支README与LR06，核对读取时HEAD为`139135231fb30b4981eedb031da9c7e182269652`。LR07/LR08中Stream-K仍仅有摘要，本轮补到相关正文；MARLIN属于针对新问题的复读，不算新增论文。

项目已接受的静态关系另读：`c72d28b17247f25d0c3613604ab6cab1737666e0:docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_STATIC_AUDIT_174NEW_V1/ADDRESS_MAPPING.md`，blob `16360a4e671fcccb923545be551796c80d782584`。该文件确认Mtile间共享weight-side地址、mod8 K tile分配，以及384的线性block-ID距离；它明确不证明实际CTA调度顺序。

当前问题已经不是“split1/8哪一个总是更快”，而是：已观察到的工作集容量拐点与跨M复用，是否暴露出已有高质量软件没有解决的限制？

**本轮判断：现有机制定位值得完成，但不能把“split-K影响缓存复用”或“形状感知split选择”本身作为新颖性。最紧缺的强基线，是在同一AWQ数学与tile下，仅改变CTA到输出tile的映射，检查不增加split和归约也能恢复多少复用。**

这是后续研究建议，不是本轮GPU授权。当前Lane6/7/8按原合同继续，实验结果不因本轮文献而改门槛。

## 1. 阅读登记

| ID | 完整标题或来源 | 版本与本轮阅读范围 | 新增程度 |
|---|---|---|---|
| S1 | Stream-K: Work-centric Parallel Decomposition for Dense Matrix-Matrix Multiplication on the GPU | arXiv:2301.03598，作者正文的ar5iv转换；§3–6，重点§5.2 | 从摘要升级到相关正文 |
| S2 | Stream-K++: Adaptive GPU GEMM Kernel Scheduling and Selection using Bloom Filters | arXiv:2408.11417v2，2025-11-25；PDF§3–5，核读第10/11页图文 | 新增相关正文 |
| S3 | MARLIN: Mixed-Precision Auto-Regressive Parallel Inference on Large Language Models | arXiv:2408.11743v1，§3.4、striped partitioning及相关评估 | 复读已有近邻 |
| S4 | SwizzlePerf: Hardware-Aware LLMs for GPU Kernel Performance Optimization | arXiv:2508.20258v1，§2–4与相关附录；按预印本引用 | 新增相关正文 |
| S5 | GPIR: Enabling Practical Private Information Retrieval with GPUs | arXiv:2604.04696v1，§2.5、3、4及相关实验说明；按预印本引用 | 新增相关正文，非AI对照 |
| D1 | Triton Matrix Multiplication tutorial | L2 Cache Optimizations段与对应源码；固定commit见末尾 | 官方工程文档/源码 |
| D2 | NVIDIA CUTLASS Efficient GEMM in CUDA | Threadblock Rasterization、Parallelized Reductions | 官方工程文档 |
| D3 | NVIDIA/cutlass issue #901作者解释 | Duane Merrill对Stream-K cache skew的说明 | 作者工程解释，不是新实验 |
| A1 | A Coordinated Tiling and Batching Framework for Efficient GEMM on GPUs | PPoPP2019官方会议摘要 | 仅摘要，不计入正文阅读 |

合计5篇工作的相关正文：3篇新增、1篇升级、1篇复读；另有2份官方文档、1项作者说明、1篇摘要。不是5篇全新论文，更不是5篇完整artifact复现。

## 2. 按具体实验组核对，而不是只列论文名字

| 记录 | 研究问题与实际对象 | 改变/固定什么 | 证据层次 | 必须保留的限制 |
|---|---|---|---|---|
| E01 / S1 | 不同GEMM几何下的工作量均衡与partial成本 | 对比同tile数据并行、hybrid Stream-K、cuBLAS、理想选择器 | A100；FP64及FP16输入/FP32累加输出；32,824个对数随机采样的形状 | shape corpus，不是完整LLM；非W4；未运行作者代码 |
| E02 / S1 | 基础Stream-K的K进度偏移对复用的影响 | 作者§5.2分析basic与混合调度 | 算法说明及其进入正式实现的设计依据 | 不把示意调度直接当本项目GPU调度记录 |
| E03 / S2 | 多种Stream-K轮数配置的收益范围 | MI250X单chiplet104 CUs；923个FP16形状；每配置50 warmup+50计时均值 | 真实GPU微基准，CK profiler | 不是AWQ；与原Stream-K不同硬件/实现；不能横向拼speedup |
| E04 / S2 | 低成本选择已有候选配置 | 预先profile的winning形状编码进Bloom filters | CPU查询/候选筛选与GPUprofile表相连 | 不等于在完全未见形状上免profile预测最优；容忍慢5–20%不等于实际获胜 |
| E05 / S3 | W4A16的activation供数、weight流入与partial归约 | kernel采用对称INT4与FP16 scale，联合tile/加载/striped分工 | kernel设计与作者评估；本轮重点设计章节 | 不能把原论文对称INT4和C16 affine qzeros语义直接视为同权重 |
| E06 / S4 | PID重映射是否改善分离式GPU的局部L2复用 | MI300X/XCD语境；10类ML/science kernels；三种LLM上下文策略 | 原生kernel优化与profiling | XCD局部L2不等于RTX4080拓扑；不是W4 split策略消融 |
| E07 / S4 | 缓存统计改善能否变成时间收益 | GEMM实例报告L2改善与约1.03倍时间收益 | 同篇kernel级结果 | L2 hit改善百分比原文未在该句严分相对值/百分点，不代作者重定义 |
| E08 / S5 | batching增加占用率的收益与临时工作集越过L2的代价 | ExpandQuery/ColTor的operation-level与stage-level融合；batch与stage变化 | 真实GPU分析，重点RTX5090；多项系统结果另列于原文 | 这里的容量墙属于PIR多项式临时量，不是W4 GEMM权重；RowSel GEMM布局是另一个问题 |
| E09 / D1,D2 | 不拆K，能否改变相邻CTA的数据重叠 | 输出tile的分组/遍历映射 | 官方算法/代码说明及示例 | 不直接继承示例硬件上的收益；需要本项目同语义实现验证 |

上表的“对本项目有什么用”是我们的归纳，不冒充作者对C16的结论。形状集合选型理由未逐项披露的，不自行补成“代表所有LLM”。

## 3. 哪些认识需要收紧

### 3.1 Stream-K已经讨论负载均衡与cache复用的冲突

**原文。**§5.2指出，basic Stream-K让不同CTA处在不同K位置，可能破坏它们共享输入fragment的时间一致性。作者采用hybrid设计，限制这种偏移持续的范围，再接完整、K进度对齐的数据并行波次，同时处理partial归约延迟。[S1]

**对我们的含义。**“并行度和locality要一起考虑”不是空白。我们的固定split8是模8交错K32 tile，也不是Stream-K算法的同义名称，不能把同一个词的不同工作分配直接混为一类。

D3补充说明了一个关键边界：完整矩阵不需要全部进cache，相近时刻重复访问相同fragment也可能得到良好复用。故当前62–75MiB拐点首先属于当前tile、映射、访问时序和平台组合，不是所有GEMM只看KN字节就能预测的通用硬阈值。[D3]

### 3.2 只调整tile映射，是必须面对的已有能力

Triton教程直接把按M行分组、组内沿列遍历用于改善L2复用；CUTLASS也明确将连续CTA映射到紧凑的二维输出区域，提高相近时刻访问相同输入tile的概率。[D1,D2]

我们的accepted映射是Ntile最快变化：同一Ntile的下一个Mtile在线性ID上相隔384。一个经典分组映射可让同一Ntile的若干Mtile在ID上邻近，而不拆K、不增加8-plane输出和独立reduction。[P1]

这只是候选解释：改变logical block映射不保证硬件严格按ID执行；改善B复用也可能牺牲A复用或改变并发。因此正确的问题不是预先宣布swizzle一定优于split8，而是测清它能消除多少当前差距。

### 3.3 Stream-K++使“再做一个形状选择器”不够新

该文在MI250X的FP16 corpus中比较多种hybrid配置，普通数据并行在约87%的测试形状里最佳；Bloom filter保存的是已有profile产生的winning配置集合。[S2]

因此，查询便宜不代表发现过程免费，允许一定退化也不代表胜出。未来若研究选择策略，必须分别报告：候选执行能力、离线profile成本、在线选择成本、未参与调试的形状表现，以及有限候选集合内的理想选择结果。

这也不意味着本项目应该立即实现Bloom filter选择器；眼下尚未证明现有调度能力之后存在新的可利用空间。

### 3.4 MARLIN提醒我们：换数据流后，值得缓存的对象可能不同

MARLIN原论文用L2帮助重复供给activation，量化权重采用低保留倾向的加载提示避免污染，并以striped partitioning减少跨SM全局归约。[S3]

所以“尽量让完整qweight进L2”不是W4通用设计目标。当前AutoAWQ确实可以暴露跨M权重复用机会，但需要检查更强实现是否通过不同tile/加载/partial组织绕开了这个代价。

原论文对称INT4不能无条件充当本项目affine qzeros的同权重基线。真正的实现比较应核对解码权重、输入、输出与累加语义；无法等价时只能单列部署差异，不能称纯kernel优化。

### 3.5 更新的工作也已覆盖“用L2指标指导调度”

SwizzlePerf针对多XCD拓扑，用硬件/调度信息和profiling辅助生成PID重映射。GEMM例子即使命中统计改善，时间收益也只有约1.03倍。[S4]

这提醒我们两点：不能把“LLM帮我们选一个cache-aware调度”作为创新本身；性能目标也不能被命中率替代。其分离式L2拓扑不直接适用于4080。

### 3.6 容量与并行度权衡也不是AI专属现象

GPIR在PIR的ExpandQuery/ColTor中展示了batch放大临时多项式工作集、超过L2后增加DRAM的情况，并按阶段在高并行的分操作实现与减小中间数据的融合实现之间切换。[S5]

它不是我们的split-K方法，也不是W4机制验证；但足以限制“这种容量墙是LLM首次出现的问题”的说法。我们若要主张低比特特有性，必须展示量化布局、metadata或执行组织带来的具体新增限制。

## 4. 最小强基线阶梯：不是重建所有论文

| 优先级 | 对照 | 它回答什么 | 不该做什么 |
|---|---|---|---|
| 现有 | 原split1、原split8 | 保留已接受的现象与机制诊断 | 不把两者包揽为全部强软件能力 |
| 第一补项 | 同一AWQ split1 + 经典分组tile映射 | 不增加partial/reduction，是否也能保住跨M复用？ | 不先换成另一Triton GEMM；不事后无界扫描group大小 |
| 同一小集合内的联合对照 | 相同映射能力下比较split1/8 | split效果是否只是补偿原映射缺少局部性？ | 不用弱映射的split1对强映射的split8宣称独立split收益 |
| 部署相关性需要时 | 数值/格式合法的优化W4实现，优先核MARLIN类能力 | 强数据流/归约已经消除了多少损失？ | 不重数量化后冒充只换kernel；不要求先完整复现论文所有模型 |
| 只有提出新分工算法时 | Stream-K/hybrid或匹配的work-centric调度能力 | 新方案相对已有负载均衡和partial控制还有什么增量？ | 不把FP16库结果直接作为W4逐bit基线 |

经典分组映射属于已有能力的移植。即便它取得很大speedup，也不等于新机制；它的价值是找到我们必须超越的基准。

未来实施前，至少核：映射双射、尾块覆盖、真实输出参考、每tile K累加顺序、dequant数学、CTA总数、寄存器/指令开销、完整module时间。合成数据可能掩盖重复/遗漏输出tile，不能只凭某种重复pattern下输出相同就放行错误映射。

## 5. 对当前跨M replica实验的使用范围

本轮不改变其运行合同。它要回答的是取消weight-side跨M地址共享后，命中/流量/时间如何变化；与“是否存在更好的调度方案”是不同问题。

解释时需继续保留：所有cell分配16份相同内容，并不意味着活跃工作集相同。SHARED与PER_MTILE同时改变被实际访问的地址、活跃页面数量及可能的set/DRAM映射；因此不能把变化称为“只改变L2而其他微架构状态完全不变”。这来自干预定义本身的逻辑分析，不是新增测量，也不要求中断正在进行的实验。

两种state用同一patched binary，有助于隔离代码生成差异；仍不授权将其绝对时间与未patched旧binary的时间合并成同一组样本。当前结果足以支持到哪一层，等独立consumer后再判断。

## 6. 可能继续的问题，与停止条件

最小下一问题：

> 在经典tile映射已改善复用之后，固定split策略是否仍因并行供给、有效复用工作集和partial/reduction成本的冲突而失效？

这是我们的研究建议，不是作者承认的未解问题，也未被当前数据证明。

- 若仅经典映射就消除大部分异常：把结论收为当前实现的访存组织缺陷与诊断方法，不继续“挽救”固定split8的机制新颖性。
- 若映射改善后仍有稳定剩余差距：再问现有split/hybrid分工为什么无法解决，才有理由开发新机制。
- 若只有命中改善而module不快：不能把统计收益包装成系统性能机会。
- 若新选择规则只在已看过的K点有效：这些点仍是discovery，不是独立验证；另留形状/调用状态。

可能影响有效工作集的变量至少包括split分工、tile遍历、quantization group布局与并发K进度。单个“完整weight bytes / L2 bytes”比值不足以替代它们。这是待验证的解释框架，不是已经构建的预测模型。

## 7. 版本与阅读中保留的问题

1. Stream-K原PDF入口因文件大小无法直接解析，正文使用作者论文的ar5iv转换；没有运行artifact，也不冒称最终会议PDF逐页审校。
2. Stream-K++采用v2（2025-11-25），不是2024 v1。arXiv元数据标题中Scheduling/Selection顺序与PDF标题存在差别，按arXiv引用题名登记。
3. Stream-K++正文关于均值/中位数的描述与Fig.3说明方向不一致；本笔记不采用该项判断。约87%的数据并行胜出比例来自§5.2及相应图文，而非把容忍退化后的数量当胜出数。
4. SwizzlePerf按指定v1阅读，不把摘要的通用措辞自动升级为所有GPU/所有形状保证；附录中的映射代码未由本项目执行验证。
5. PPoPP2019协调tiling/batching仅取得官方摘要，保留历史近邻，不臆造其实现参数或对本项目的性能结果。
6. 本轮未完成Leeway、ATLAS、PIPP勘误队列；没有将其列为新增已读。

## 8. 固定来源与代码定位

### S1 Stream-K
- 论文： https://arxiv.org/abs/2301.03598
- 本轮正文： https://ar5iv.labs.arxiv.org/html/2301.03598
- 作者入口： https://mgarland.org/papers/2023/streamk/
- 重点：§3.1/3.3、§4、§5.2、§6。作者比较包含同tile数据并行、CUDA11.6 cuBLAS与有限tile集合的理想选择器；不将这个理想选择器当可实施在线方案。

### S2 Stream-K++
- 版本： https://arxiv.org/abs/2408.11417v2
- PDF读取入口： https://arxiv.org/pdf/2408.11417
- 重点：§4.2、§5.1–5.3；PDF第10/11页图文已核。预先profile的最优配置是Bloom filter内容来源。

### S3 MARLIN
- https://arxiv.org/html/2408.11743v1
- 重点：§3.4及Striped Partitioning；与LR06互相引用，属于复读，不重复计成新论文。

### S4 SwizzlePerf
- https://arxiv.org/html/2508.20258v1
- 重点：§2–4、Appendix A.2/A.4，分离式GPU的PID映射及kernel-level评价。

### S5 GPIR
- https://arxiv.org/html/2604.04696v1
- 重点：§2.5、§3、§4；分清ExpandQuery/ColTor容量墙与RowSel的GEMM布局问题。

### D1 Triton
- 文档： https://triton-lang.org/main/getting-started/tutorials/03-matrix-multiplication.html
- repo：`triton-lang/triton`
- 读取时固定commit：`ef633a550d8565a8c4cd89edce63213c8b173e2b`
- path：`python/tutorials/03-matrix-multiplication.py`
- blob：`526934c1d7c60ccbb8119b1bca0e807f6fc602e8`
- 本轮核读源码第100–152行附近的grouped ordering说明；这是当前公开源码，不冒称某个历史发行版本。

### D2 CUTLASS
- https://docs.nvidia.com/cutlass/latest/media/docs/cpp/efficient_gemm.html
- 访问日期2026-09-29；Threadblock Rasterization与Parallelized Reductions。

### D3 作者工程说明
- https://github.com/NVIDIA/cutlass/issues/901#issuecomment-1494657119
- 作者Duane Merrill解释普通数据并行CTA对K fragment的时间一致性与Stream-K skew。只做补充解释，不替代S1正文或本项目native证据。

### A1 历史摘要
- https://ppopp19.sigplan.org/details/PPoPP-2019-papers/32/A-Coordinated-Tiling-and-Batching-Framework-for-Efficient-GEMM-on-GPUs

### P1 项目已接受地址映射
- repository：`swayhrl/accel-sim-framework`
- commit：`c72d28b17247f25d0c3613604ab6cab1737666e0`
- path：`docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_STATIC_AUDIT_174NEW_V1/ADDRESS_MAPPING.md`
- blob：`16360a4e671fcccb923545be551796c80d782584`

## 9. 本轮执行边界

仅更新ChatGPT文献分支。未发布新Codex Goal，未启动新的native、trace或模拟；未修改跨M实验和已接受结果。后续实验依据当前producer/consumer结果再另行冻结，不能拿本轮文献建议静默替换已经下发的合同。
