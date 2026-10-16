# Round A62｜稀疏前向加速不等于训练加速：三方向强软件与结构寿命

**日期：2026-10-16；执行者：ChatGPT／AI-ARCH Discovery。**

**范围：** 本轮仅公开论文、固定作者源码和控制端算术；未访问109/174-new/164，未启动模型、CUDA、Codex、模拟器或新下载任务。A61已经由用户交给109 Lane M，结果待回报；没有检查其运行进程或轮询执行分支。旧协调导航中的“待授权”早于用户实际授权，不作为当前执行状态。

**科研起点：** `hrl/ai-workload-research-coordination@5d0a3f1145aff943899fc6e08737e77ea023ba4f`。发布前比较该SHA与协调分支为identical。A61原Goal、预算、数据、环境、共享锁和全部历史STOP不变。本文件是研究笔记，不是执行Goal。

## 1. 本轮裁决与实际增量

新增一个**有条件的研究候选**：在具有可接受任务质量的真实稀疏权重模型中，分别优化前向、输入梯度、权重梯度后，三种访问方向、表示转换与归约组织是否还存在软件无法消除的性能或容量代价？

它尚不是已成立的硬件问题。新增证据首先揭示强基线资格缺口：SNACK公开的Sputnik适配只替换前向；训练计时也未覆盖结构更新。不能把“采用Sputnik”当成整个训练路径已经充分优化。

对旧Q-S点云方向，本轮将后续审查明确到完整训练的三方向与映射寿命；但WarpConvNet已经具备分方向选优、反向映射缓存和部分转换共享，因此这些能力不是待发明的机制。

不提高GPU执行优先级，不为维持流水线新增任务。A61仍是唯一已派发任务；Q-S仍是原候补，新稀疏训练问题先保留为源/数值资格候选。

## 2. 阅读范围与证据等级

| 来源 | 本轮核对范围 | 尚未完成 |
|---|---|---|
| SNACK，arXiv:2610.04093，2026-10-02 | 作者正文§3—5、Table 4及相关附录；固定仓库的层、两种GPT-2 runner与Sputnik接线 | PDF页面未成功取得；没有将论文表格绑定到确切运行命令、原raw或完整训练 |
| BARTER，arXiv:2610.16147，2026-10-12 | 作者正文§3—4、Appendix C.5/D.1 | PDF页面未成功取得；未固定作者代码及原运行数据 |
| HASTE，arXiv:2606.01117v1 | §3—4的表示、实现与实验；PDF第5—6页相关图表核对 | 未审作者完整代码或复跑 |
| FlashSchNet，arXiv:2602.13140v1 | §4—5的数据流、动态邻居与评估；PDF第2、11页图表核对 | 未固定运行代码、模型和数据许可，未复跑 |
| WarpConvNet固定源码 | 三方向dispatch/autotune、mask与reverse-map缓存、转换共享 | 本机ABI、GPU可运行性、实际路径和性能均未验证 |

SNACK/BARTER基于作者页面返回的正文和表格文本，不声称已核对PDF图形或最终会议版。所有作者结果为文献证据；固定代码为源码证据；比例为对论文表中值的算术重算；下面的小实验设计是提案。

## 3. SNACK：值得追问的是训练路径，不是摘要中的局部倍数

来源：[SNACK原文](https://arxiv.org/abs/2610.04093)，重点§5/Table 4。

作者GPT-2 small实验仅替换MLP的c_fc/c_proj。99%稀疏度时，相比同稀疏度Dense+Mask，SNACK(Sputnik)表中Memory从2260.84降至1366.27 MB，减少约39.57%；但`Latency_token_ms`从41.76增至70.67，为1.6923倍。90%组对应比值为127.16/41.72=3.0479倍。

这些是论文报告列的配对算术，不是109原生结果，也不重新解释成生成token的TPOT。99%组困惑度130.28与同稀疏度对照131.90相近，却明显不同于dense参考29.73；“保持质量”不能跨比较对象。不能为了制造压力而只挑最高稀疏度、忽视任务可用性。

**我们的判断：** 容量节约与训练执行效率必须分开。局部SpMM快、存储少，尚不能解释整个训练为什么慢；首先应核清实际工作、强软件覆盖和计时边界。

### 3.1 一个后端名称没有覆盖三个方向

固定仓库：`JafarBadour/Snack-SNN@bbae741b5bd460ed8c936c49e63f034f06f5a58f`，tree `8ccab29f48c2f99c261cbc39278983592ec8d305`。

在[`DST/layers/Snack.py`](https://github.com/JafarBadour/Snack-SNN/blob/bbae741b5bd460ed8c936c49e63f034f06f5a58f/DST/layers/Snack.py)的`SputnikSnackFunc`中：

| 训练部分 | 实际源码路径 |
|---|---|
| 前向 | 输入转置/contiguous、权重值按缓存次序重排后调用`sputnik_mod.spmm`，再转换输出布局 |
| 输入梯度dX | 构建`SparseTensor`视图，用其转置与grad_output相乘；不是Sputnik调用 |
| 活跃权重梯度dW | `sparse_outer_join`；不是Sputnik调用 |

因此，论文中的SNACK(Sputnik)标签不能替代逐方向实现审计。这里证明的是该固定代码如何接线，不是证明哪部分实际最慢，更不是宣称论文所有结果无效。

### 3.2 batch=1未必是矩阵乘中的一行

[`run_gpt2_dst_snack_benchmark.py`](https://github.com/JafarBadour/Snack-SNN/blob/bbae741b5bd460ed8c936c49e63f034f06f5a58f/experiments/gpt2_dst_lm_benchmark/run_gpt2_dst_snack_benchmark.py)的`SnackConv1D.forward`执行`x.reshape(-1, x.size(-1))`。该runner默认训练batch=1、block-size=128；对形如[B,L,C]的输入，矩阵行数是B×L，而不是B。

这是默认代码路径的形状推导，不是已经核准论文Table 4用了该默认命令。它说明后续不能将单行SpMM优势直接推广到“batch=1的GPT训练”。

### 3.3 公开runner计时不等于完整动态稀疏训练wall

该文件`train_variant`在forward、backward和optimizer.step后立即记录结束CUDA event并同步。mask处理、剪枝/生长以及Sputnik CSR缓存刷新发生在结束event之后。对应的[`from_scratch` runner](https://github.com/JafarBadour/Snack-SNN/blob/bbae741b5bd460ed8c936c49e63f034f06f5a58f/experiments/gpt2_dst_lm_benchmark/run_gpt2_dst_snack_from_scratch_benchmark.py)也采用先结束event、后更新结构的顺序。

所以这些runner的`cuda_time_ms`不能直接用于估算包含结构维护的完整训练周期。这里没有测到漏计成本有多大，也没有证明它足以解释训练变慢。论文表格与具体runner/raw的绑定仍待核。

**处理原则：** 将它们登记为实验资格和性能分母问题；不因此启动第三方修bug工程，也不把包装问题包装成微架构机会。

## 4. 三个强软件/算法反证

### 4.1 BARTER：结构会变化，并不等于维护值得硬件化

[BARTER](https://arxiv.org/abs/2610.16147)用实际紧凑的头/FFN通道与普通dense kernel执行，涉及模型结构和优化器状态调整，不是同一无结构mask的后端替换。Appendix D.1的epoch长度计时段包括结构更新；C.5中ViT/Tiny-ImageNet、density=0.5的更新频次对照，均摊增量估计为0.019—0.117 ms/optimizer step。

这是按更新频次加权的估计，不是每次改结构的时延，也不是完整100 epochs连续计时。它足以反驳“只要动态改形状，就一定有很大维护瓶颈”的立项方式，不能否定所有无结构DST。

### 4.2 HASTE：共享索引和训练方向重组已有直接近邻

[HASTE v1](https://arxiv.org/html/2606.01117v1)面向极大标签空间，让相关标签共享fan-in支持集合、保留各自权重，结合组内gather复用和反向Split-K。它改变允许的稀疏结构，并非对任意既定mask做无损压缩。

因此“相邻输出共享索引”“分组后用Tensor Core”“反向拆归约”不能直接充当新机制。公平比较要么固定支持集合，要么明确作为算法—质量—执行效率前沿另行比较，不能混成单变量硬件消融。

### 4.3 FlashSchNet：正反向聚合与动态索引维护已在软件中联合处理

[FlashSchNet v1](https://arxiv.org/html/2602.13140v1)已经融合边消息生成，并分别按destination/source组织正向与反向聚合；邻居图变化时重建索引，正文明确计入相应开销。

其反向服务于能量对坐标求导得到力，不等于权重训练与optimizer更新。因此它提供数据流近邻和真实动态结构反例，不能直接当作A61 GraphSAGE训练或SNACK稀疏权重训练的同语义基线。本轮不开展新分子动力学部署。

## 5. Q-S的新补强：三方向选优和反向映射缓存已经存在

固定仓库：`NVlabs/WarpConvNet@f9474304bbfe94bf7ffe0f8dbbcc468c1ff0ceb1`，tree `9a62603c27ace7c5565cbc829611056ecfc2bf7c`。

- [`autotune.py`](https://github.com/NVlabs/WarpConvNet/blob/f9474304bbfe94bf7ffe0f8dbbcc468c1ff0ceb1/warpconvnet/nn/functional/sparse_conv/detail/autotune.py)分别维护前向AB、输入梯度ABt、权重梯度AtB结果缓存。
- [`unified.py`](https://github.com/NVlabs/WarpConvNet/blob/f9474304bbfe94bf7ffe0f8dbbcc468c1ff0ceb1/warpconvnet/nn/functional/sparse_conv/detail/unified.py)保存kernel_map供backward使用，并分别为dgrad/wgrad选优；数值/累加精度参与候选限制。
- [`mask_gemm.py`](https://github.com/NVlabs/WarpConvNet/blob/f9474304bbfe94bf7ffe0f8dbbcc468c1ff0ceb1/warpconvnet/nn/functional/sparse_conv/detail/mask_gemm.py)已经在kernel_map对象缓存正向mask与反向mask；具备融合反向映射构造路径及fallback。另有单次backward scratch内的cast/absmax共享。

不能再提出“第一次缓存反向映射”“第一次分别优化dX/dW”“第一次共享cast”作为研究贡献。也不能把源码能力等同于4080上已通过数值和性能资格。

Q-S仍可问：在这些能力真正生效之后，真实训练中多种表示的准备、同时存活与消费是否还有有意义的代价？这比原先只看推理映射寿命更完整，但仍需数据。正反向map字节数不等于L2占用、DRAM流量或stall时间。

## 6. 新候选的精确科学问题

设X为M×I，稀疏W为I×O，G为输出梯度，S为固定活跃权重坐标集合。一次训练涉及：

- 前向：Y=XW。
- 输入梯度：dX=GW^T。
- 权重梯度：只对(i,j)∈S计算dW(i,j)=Σ_m X(m,i)G(m,j)。

这是基本链式法则，不是新算法。关键是同一支持集合被三个方向以不同访问与归约方式消费；适合其中一个方向的存储次序，未必适合另外两个。

**可证伪问题：** 在固定自然输入、支持集合、数值及更新规则，并分别采用合格强实现后，单一/多重稀疏视图与训练三方向之间，是否还存在软件无法消除的容量—执行代价？

目前尚不知道差距来自dX、dW、排序/重排、launch、计算并行度还是供数。不能先命名一个“稀疏训练Cache”再补动机。

空间坐标稀疏、稀疏权重、动态分子邻居图共享这套审查方法，但不是同一种科学输入；不能合并成一个虚假的跨模型实测结论。

## 7. 后续最小验证设计：提案，不是新的执行授权

**第一步只做源/数值资格清单。** 选择一份有明确质量依据的真实稀疏模型状态和一个自然层；先核模型、文本、mask、激活、梯度与optimizer身份。没有质量合格的真实对象就停，不用随机稀疏矩阵补成“真实模型”。不重用A59未合格的ogbn-products。

如果以后获准原生试验，最小对照应为：

| 条件 | 作用 | 不能声称 |
|---|---|---|
| 同支持集合的Dense+Mask | 数值参考与原实现对照 | 唯一强软件基线 |
| 作者实际稀疏路径 | 建立可追溯起点，逐方向记录实现 | 一个后端名即全路径最优 |
| 三方向各自合格强实现 | 纳入必要布局转换与正常结构复用 | 无代价自由切换后端 |
| 同结果表示提前就绪诊断 | 检查表示准备的敏感性 | 可实施机制或严格性能上界 |

正式计时先测未插桩完整训练窗口，覆盖自然更新频次，再另做方向归因。固定mask局部实验可用于数值与局部因果，但不能替代动态训练周期。人工提前就绪可能改变cache入口和请求顺序，要单列这些影响；不把各阶段独立计时简单相加为wall。

不在本轮规定GPU分钟数、下载额度或新seed；这些必须与具体对象共同形成未来有界Goal，不能借用A61预算。

### 停止与晋升

1. 若低质量高稀疏度才出现差异，或没有合法输入/可复现数值，停止该对象。
2. 若升级反向kernel、消除普通重排或复用已有表示后差异被软件吸收，记录软件充分，不进硬件。
3. 若只是指标分母错误、瞬时显存读数或插桩同步制造现象，修正解释，不按硬件问题晋升。
4. 只有目标kernel family在强软件后仍有稳定代价，才定位在线可见信息与有限硬件控制点；同时报告非目标影响、真实coverage与完整训练wall。不同调用/模型状态用于独立验证，不把调试数据称holdout。

## 8. 科研排序与下一交付

| 方向 | 本轮结论 | 下一步 |
|---|---|---|
| A61 IGB-small GraphSAGE | 唯一已派发任务，结果待用户回报 | 原合同独立审查，不干扰 |
| Q-S点云稀疏卷积 | 原候补保留；强软件基线补到三方向与map复用 | A61后按原决策选择是否做真实层组资格 |
| 新稀疏权重训练候选 | 有论文现象，但强基线和测量边界未闭合 | 先一份真实对象/三方向/数值/质量资格表，不直接GPU |
| 动态拓扑更新加速 | 没有可用硬件动机，存在BARTER反例 | 不单独立项 |
| 共享索引、正反向映射缓存、图聚合融合 | 已有直接软件/算法近邻 | 作为反证，不重新命名机制 |

下一份有意义的交付不是再增加论文数量，而是一张“真实对象—前向—dX—dW—表示准备—结构更新—强实现—质量要求”的表；资料足够才设计原生最小实验。当前没有新Codex指令、GPU执行授权、后台监控或自动后续任务。

## 9. 固定源码索引

| 仓库/文件 | Git blob |
|---|---|
| SNACK `DST/layers/Snack.py` | `891dca1ab8c189d9a956cbcd64507f2e67a630b5` |
| SNACK GPT-2 benchmark runner | `1fafda5488b08119d61e57f7a3db21b26281430e` |
| SNACK GPT-2 from-scratch runner | `86fea17afeed2ade85437aa39bd47b3989a7d073` |
| WarpConvNet `detail/autotune.py` | `3211ae6db821025b43b647aaa2ca16ed2e79b87e` |
| WarpConvNet `detail/unified.py` | `9dd2b97819ee36a12c0732018f86872a39445c77` |
| WarpConvNet `detail/mask_gemm.py` | `2e1fa0bbcd5618c29f8db50cfb4d18806df8a2b5` |

所有代码判断仅覆盖已读函数，不代表完整仓库安全/正确性审计，也不宣称论文实验使用了这些exact commits。作者仓库代码许可不自动覆盖模型、数据和第三方依赖。

**终态：A62文献/源码Discovery完成；新增一个有条件候选、补强Q-S基线；没有已证实的新硬件瓶颈。A61保持用户已派发、结果待回报。**
