# Round08｜两个并行的小型探索，而非继续串行寻找负结果

日期：2026-09-27。维护：ChatGPT。

## 0. 结论与阅读范围

保留两个探索入口：

- **R81：异构grammar合法词表的批处理代价**。不是首次提出少算非法词表行，而是比较已存在的indexed LM-head之后，共享合法集合与逐请求稀疏计算的代价。
- **R82：现代编译器之后的片上layout转换代价**。不是首次提出layout优化或线程—寄存器解耦，而是从真实已优化kernel中检查剩余转换及有限替代实现。

这是文献驱动的低成本探索组合，不是两项已经证明新颖的硬件机制。允许小原型作为诊断，不要求预先证明5% headroom；只有扩大投入和最终claim需要进一步因果、强基线与验证。

核心13篇：7篇阅读HTML正文的关键机制/实验/限制章节，6篇仅取得原始摘要。另查官方源码、示例和产品文档。不是13篇全文精读，不是13篇均为新增，不是代码复现。

没有启动109/174实验。执行授权另见Round08 coordination branch中的START_HERE和两个独立Goal。

## 1. 继承与方法修正

R54最新执行依据是 `d6ef29505de75985181afc74dffc3cf1b652afc2`，后端资格和checkpoint证据保留；不重跑R51—R54。历史结论只能解释已测模型、后端和范围，不排除整个TLB/cache/调度领域。

此前R54的2048-token前缀是4096-token前缀的前半段，因此是预留长度验证，不是独立内容。copy时间小于总增量、host调用较大，只支持尚未定位出GPU本地残差，不等于完整critical-path因果分解。这里收紧解释，不修改原raw或重开R54。

本轮区分：已知能力、能力在具体执行上的代价、待验证的新能力。没有必要完整复现每篇论文，但不能用缺失最接近已有能力的弱baseline。

## 2. 原文登记与实际支持

| ID | 来源与所读版本 | 深度及所读位置 | 已有能力/边界 |
|---|---|---|---|
| R801 | XGrammar-2, 2601.04426v4, 2026-08-05 | 正文§2—4、实验设置 | TagDispatch、跨grammar缓存、Earley/JIT mask；CPU mask工作与模型重叠。近零mask开销不证明LM-head跳过权重行。 |
| R802 | FlashSampling, 2603.15854v2 | 正文Algorithm1、limitations、AppendixD及实验 | tiled LM-head+sampling、不物化完整logits；已描述全非法group零质量可跳过。不能将跳过无效组/融合argmax当新数学。v2端到端最大改善为10%左右，不沿用v1的19%。 |
| R803 | VocabTailor, 2508.15229v1 | 正文§3.3、§4与消融 | 静态task词表+动态输入token选择，按需加载LM-head；经验质量近似，不是grammar给出的精确合法集合。 |
| R804 | Linear Layouts, 2505.23819v5 | 正文转换lowering/优化及§6 | F2表示、no-op消除、线程内置换、warp shuffle、shared swizzle；包含RTX4090实机，不等于4080已测。不能拿旧Triton缺陷当新硬件机会。 |
| R805 | LoRAServe, 2511.22880v1 | 正文rank异构动机、设计与实验 | rank-aware placement/routing；模型/请求/集群设置需与单GPU局部计算分开。 |
| R806 | VecFlow, 2506.00812v1 | 正文架构、filtered search、实验 | label-centric索引、选择性策略、persistent路径；过滤先于距离计算已有。recall和搜索策略变化不能叫纯映射收益。 |
| R807 | Vorion, 2511.16831v1 | 正文架构/数据流/实验 | RISC-V GPU加专用Gaussian rasterization/training单元；不是只调整现有CUDA kernel。 |
| R808 | FIBER / A Thread-Register Decoupled GPU Execution Model, 2608.19628 | 原始摘要 | 共享寄存器视图、动态并行、细粒度数据流与operand supply已有直接硬件近邻。未取得全文，不补写局限。 |
| R809 | Tensor Seeks Layout, 2608.21555 | 原始摘要 | global layout selection形式化与最优求解，区分cost model误差与search质量。未取得正文，不将其加速比归给SM89。 |
| R810 | tLoRA, 2602.07263 | 原始摘要 | rank-aware nano-batching及融合低秩执行，不能直接把异构rank命名为新问题。 |
| R811 | BOA, 2609.16175 | 原始摘要 | GPU向量搜索beam widening与overlap已有；全文未核。 |
| R812 | GSGPU, DOI 10.1109/ISPA67752.2025.00014 | 出版方摘要 | Gaussian SM不均衡与层次atomic合并已有；全文未核。 |
| R813 | 3DGART, 2608.17298 | 原始摘要 | particle-centric backward gather替代contended scatter；全文未核。 |

补充检索出现ZapFormat、VOCABTRIM、Scaling DoRA、FlashRec等，作为额外排雷线索，不加进上述正文阅读计数。没有依据第三方AI摘要补作者实验细节。

## 3. R81：为什么还值得一次小实验

### 3.1 两个不能忽略的现成实现

**FlashSampling**先计算tile logits再施加mask/bias/temperature，并将选择合进matmul；其数学已支持全非法分组的零质量处理。我们不能仅用普通dense logits materialization作为唯一强baseline。

**Kestrel**源码 `kestrel/models/moondream/text.py::lm_head` 已有 `indices` 参数，先选择 `module.lm_head.weight[indices]` / bias，再调用linear。检查版本：`f61d3c7c6a8380e705a984f1e1767693464e27bd`，blob `50ac9a5da9cd22efc8d62a20ab5d47eff1b4b2e4`。这直接排除“首次让LM-head只计算一部分词表”这个宽泛新意。

**FlashRec**公开0.1.0说明已将head限制到SID token范围；它是有限语义ID域，不能等同每请求动态任意grammar，但也必须进入后续近邻检查。

XGrammar官方HF示例恰使用Qwen2.5-0.5B-Instruct，明确 `config.vocab_size` 可能大于tokenizer词表。其示例是LogitsProcessor后处理，不证明所有服务后端都没有前置选择。示例blob：`d32fff97628194a9cd2c878cc5092cc9479e7a89`。

### 3.2 收窄后的假设

令请求i本step合法token集合为A_i。共享一次head计算通常使用 U=union A_i；逐请求计算则使用各A_i。

`B*|U|` 与 `sum_i |A_i|` 的差是逻辑行工作差，不是HBM流量或speedup上界。共享U有权重复用/GEMM好处；分开A_i更少算，但可能多读权重、需要索引准备、造成短tile和多launch。这是待测的tradeoff，不预设谁好。

研究问题：**真实grammar轨迹中的集合异构性是否让共享union与ragged执行都留下稳定成本，强软件的indexed/fused实现之后是否还需要更细的GPU执行支持？**

mask只依赖已提交前缀与grammar，不能使用未来token。所有合法行都保留，非法行跳过；不按概率/词频再删合法token，不改tokenizer/grammar/decoder。

### 3.3 最小尝试

复用已接受Qwen2.5-0.5B revision `7ae557604adf67be50417f59c2c2f167def9a775`；已有151936×896 head及真实replay身份可复用，但新grammar轨迹必须真实生成并单独绑定，不能把旧自然文本强套随机mask。

比较dense优化head、dense融合选择、Kestrel式预分配gather+union线性层、direct-index/按相同mask分组的ragged小原型。后三者是已有能力移植或诊断，不预称创新。最多两组固定grammar cohort，正式GPU顺序加锁；无效、退化和宽合法集合均保留。

正确性首先验证每个合法行点积的数据依赖不变、mask与token-ID映射相同，再检查实际greedy选择。不要加无关的top2/top8一致gate；跨kernel数值差不能自动解释成算法删工作，也不能通过改reference隐藏差异。只有同一固定任务上合法且数值合格的pair计时。

局部算子测量必须包含该路径实际发生的mask转换、索引、gather/scatter和reduction。完整请求实验保持backbone/输入/生成策略一致；需要logprobs的应用不在本轮范围。grammar compile成本单列，不能混成每token开销。

### 3.4 停止条件

已有indexed实现已足够；真实集合并不稀疏或union并不膨胀；收益仅来自跳过单token强制输出且已有实现覆盖；剩余主要是CPU grammar代码；或者强baseline未建立。结果分别记，不从这些情况推导新硬件。

## 4. R82：数据已在片上，是否仍为分布不匹配多走一圈

### 4.1 原文和源码确实指向一个执行层问题

Linear Layouts已系统处理逻辑元素到register/lane/warp/block的映射。当前Triton转换源码先求minimal conversion：无维变化直接复用、线程内register重新编排、warp内shuffle、否则走swizzled shared-memory store/load并按scope同步。

检查文件：`triton-lang/triton/lib/Conversion/TritonGPUToLLVM/ConvertLayoutOpToLLVM.cpp`，读取blob `f5c1b400a8a45b579271696e73b9ebf9fb16e7f2`；本轮main指向 `eb93a9a97e5dfc6a20c29da0096c047dbabd514c`。正式执行前须在精确commit核blob及与已装编译器的差别。

这证明某些转换会产生实际指令，不证明每个convert_layout都有成本。还要排除更好的producer/consumer联合布局能直接避免转换。

### 4.2 对照边界

R82不是全局layout solver，不复制FIBER的完整共享寄存器执行模型，也不简单把shared/寄存器翻倍。先从已接受的FLA GDN chunk路径与P1 Triton attention路径中各筛一个真实kernel，建立IR→PTX/SASS→动态执行的对应。

分类：NOOP、REGISTER_ONLY、INTRA_WARP_SHUFFLE、INTER_WARP_SHARED、OTHER/UNKNOWN。两类直接问题：为consumer布局进行的通信，及通信scratch/barrier引起的资源占用。bank-conflict已经消除不代表shared往返免费；反之shared往返存在也不代表关键路径。

允许一个联合布局变化与一个已有指令替代通信实现；均必须保留所有数据依赖和同步含义。若改变数学归约树/precision，单独列为不同实现，不宣称纯layout变量。微原语使用整数唯一编号验证置换比top-k更直接；完整目标仍检查合法输出。

### 4.3 证据层次

先source audit；最多两个目标；确定配置后记录native完整kernel时间、register/shared占用、shuffle/shared/barrier指令映射，必要才NCU。独立提取的conversion fixture只能说明primitive，不直接代表model性能。不得把barrier stall与shared duration相加成可消除critical path。

如果当前compiler已消掉转换、合法联合布局已解决、残差只在合成fixture出现、或者现有FIBER等直接覆盖且没有更小成本的新能力，则收口。FIBER及Tensor Seeks Layout本轮只有摘要；任何硬件新颖性声明前必须补全文或明确保持未知。

## 5. 其余候选为何不同时开工

多LoRA：heterogeneous rank确有问题，但LoRAServe/tLoRA已给直接software路径；不再仅因rank不同建新campaign。

Filtered ANN：VecFlow/BOA已经深入过滤/beam/overlap；需要匹配recall和索引，不宜同时引入大dataset及新搜索runtime。

3DGS：Vorion、GSGPU、3DGART覆盖专用数据流、atomic聚合和scatter→gather；值得保留资料，但当前没有比前两项更低成本的差异化实验。

R55仍不做4080上的NVFP4性能替代实验。不是这些领域无价值，而是本轮不够具体或平台/工程成本较高。

## 6. 两窗口并行规则

两个问题、两个execution branch/worktree、两个隔离env、独立编译/JIT缓存、独立raw。共享只读权重、接受的输入、数据发布工具；不得并发改一个catalog/manifest。

109上所有会触GPU的canary/JIT/profile/正式测量都使用 `/data/c16/locks/c16_gpu_campaign.lock`。等待GPU时继续CPU工作；释放lock前等待本lane CUDA进程退出，不能把模型常驻GPU阻碍另一lane。不得杀其他人的进程。

CPU source/近邻/fixture/解析可并行。正式GPU测量每次以一个配对bundle为粒度拿锁，避免两个窗口同时benchmark。174可做已存在数据的离线分析，不自动启动Accel-Sim或新校准；164是大数据authority。

不增加通用调度器或第三个只负责管理的窗口。某lane早停不阻塞另一lane；多个有希望结果之后再排序投入。

## 7. 来源

R801 https://arxiv.org/html/2601.04426v4
R802 https://arxiv.org/html/2603.15854v2
R803 https://arxiv.org/html/2508.15229v1
R804 https://arxiv.org/html/2505.23819v5
R805 https://arxiv.org/html/2511.22880v1
R806 https://arxiv.org/html/2506.00812v1
R807 https://arxiv.org/html/2511.16831v1
R808 https://arxiv.org/abs/2608.19628
R809 https://arxiv.org/abs/2608.21555
R810 https://arxiv.org/abs/2602.07263
R811 https://arxiv.org/abs/2609.16175
R812 https://doi.org/10.1109/ISPA67752.2025.00014
R813 https://arxiv.org/abs/2608.17298
C801 https://github.com/m87-labs/kestrel/blob/f61d3c7c6a8380e705a984f1e1767693464e27bd/kestrel/models/moondream/text.py
C802 https://github.com/triton-lang/triton/blob/eb93a9a97e5dfc6a20c29da0096c047dbabd514c/lib/Conversion/TritonGPUToLLVM/ConvertLayoutOpToLLVM.cpp
C803 https://github.com/mlc-ai/xgrammar/blob/main/examples/hf_transformers/transformers_example.py （读取blob见正文；正式runtime另pin）
C804 https://github.com/FlashSampling/FlashSampling （README读取blob 0ce949416cba0bef6bf37a6c4ee78015eacf16f8；正式runtime另pin）
C805 https://pypi.org/project/flashrec/0.1.0/

作者报告、源码事实与本文件候选推理分开；未执行的native结果保持未知。
