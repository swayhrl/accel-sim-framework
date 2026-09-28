# C16文献支线LR06：低比特kernel数据流与MoE时间结构

日期：2026-09-28。维护者：ChatGPT。

状态：`LITERATURE_AND_EXPLORATION_DESIGN_ONLY`。本轮没有运行GPU、模拟器或论文代码，没有修改Core、trace、配置、Lane 4或冻结的结果。以下Lane 5是建议下发的只读探索任务，不是已执行实验，也不是full-timing授权。

## 0. 阅读起点与当前边界

先核对远端文献分支`hrl/c16-chatgpt-literature-notes-v1`，读取时HEAD为`350e4a0d364d65812f379ebc69412696e2a4d82a`。读取README和LR03相关合同；LR02–LR05已经形成的capacity/admission/survival/utility区分、经典替换基线及其实现不重新发明。

用户最新提供的状态：Lane 1四种baseline与generation observer完成bounded implementation qualification；Lane 3修复binary exact gate；Lane 4仍需数天。这里沿用该状态，不重新验收，也不读取Lane 4 partial结果。

**本轮问题：**除了等待跨token qweight驻留结论，是否存在不依赖该结论、值得以低成本检验的体系结构问题？

判断：有。优先研究低比特kernel内部的高精度operand重复读取、反量化/布局转换及reduction成本；MoE跨token时间结构作为第二候选，不能因为有expert trace就假定已经有连续路由证据。

## 1. 阅读登记

| ID | 工作 | 本轮深度 | 证据类型/边界 |
|---|---|---|---|
| S1 | MARLIN: Mixed-Precision Auto-Regressive Parallel Inference on Large Language Models | 从既有README升级到arXiv:2408.11743v1的§3.3–3.5及§5相关正文；复核作者README | 作者GPU kernel与端到端评价；不是本项目复现 |
| S2 | QUICK: Quantization-aware Interleaving and Conflict-free Kernel for efficient LLM inference | arXiv:2402.10076 PDF正文§2.3–5文本 | AutoAWQ比较、共享内存路径、kernel/端到端/vLLM实验分开；未成功渲染图，不从曲线估读新数值 |
| S3 | Fast Matrix Multiplications for Lookup Table-Quantized LLMs（FLUTE） | arXiv:2407.10960v3正文§3–4及算法描述 | LUT量化，不等同于C16 affine AWQ；kernel随机矩阵与端到端模型评价分开 |
| S4 | SpecMD: A Comprehensive Study On Speculative Expert Prefetching | arXiv:2602.03921v1正文§3–5、附录A/D/E | 软件管理GPU显存中的完整expert，含容量/带宽仿真；不是硬件L2 cache-line策略 |
| S5 | MonoNN: Enabling a New Monolithic Optimization Space for Neural Network Inference Tasks on Modern GPU-Centric Architectures | OSDI 2024会议PDF，重点§4.2–4.4、§7.2相关正文 | 静态网络单kernel编译，资源兼容与算子间优化；不作为C16直接replacement baseline |
| S6 | ATLAS: Accelerator-local Temporal Locality Analysis and Selection for Mixture-of-Experts LLM Inference | 2026-08-04 Zenodo v1作者书目与摘要；PDF获取失败 | 仅登记直接问题近邻，不宣称已核其证明或实验 |

新增正文条目是S2/S3/S4；S1属于README升级正文，S5由既有线索升级相关正文，S6仅摘要。未闭合Leeway全文，不将失败获取计入已读数量。网页与PDF工具可读正文不等于已运行作者artifact。

## 2. 原文内容及其对研究判断的影响

### 2.1 MARLIN：kernel可能更需要保住activation和partial sums

**作者内容。**§3.4把L2供数带宽与片外权重带宽共同纳入设计：输入tile经L2重复供数，量化权重使用`cp.async`配合`evict_first`降低污染；后续striped partitioning尽量减少全局归约。原文明确权重读取仍经过L2，不是绕过L2。[S1]

**我们的判断。**同为W4A16，不同kernel对L2的最有价值用途可能不同。C16当前kernel中qweight具有局部价值，与另一kernel偏向activation/partial-sum复用并不矛盾。后续应区分“同trace策略优劣”和“换实现后机会是否仍存在”，不能互相替代。

### 2.2 QUICK：片外压缩后仍可能在片内放大

**作者内容。**QUICK通过离线交错权重布局，使反量化结果直接满足Tensor Core operand布局，省去相应的dequantized-weight shared-memory回写和再次`ldmatrix`过程。正文将AutoAWQ相关路径的共享内存bank conflict列为动机；评估分别包含矩阵kernel、多个模型decode以及vLLM吞吐。[S2]

**我们的判断。**“权重字节变少”不能代替片内流量分析。但QUICK已经研究这一问题，单纯复现离线重排不是新贡献。需要核当前C16实际kernel是否经过该路径，不能因函数名含AWQ就直接归因。

### 2.3 FLUTE：带宽、解包、工作分配要一起看

**作者内容。**FLUTE在LUT量化下组合离线重排、共享内存查表向量化/复制、Stream-K分工；3-bit数据拆成1-bit和2-bit片段后在寄存器重组。其kernel评价使用Llama-3形状的随机输入，正文报告每种形状3组输入、各100次，并另做端到端评价。[S3]

**我们的判断。**该工作提供的是kernel内部数据流近邻，不是AWQ相同精度基线。LUT读、affine scale/zero运算和低bit解包的开销必须分开；不能用“均为4-bit”抹平量化格式差别。

### 2.4 SpecMD：MoE时间结构值得研究，但cache层级必须说清

**作者内容。**SpecMD分开routing、miss handling、eviction和prefetch，并用Least-Stale结合forward-pass状态与layer位置管理expert。§5.1使用A100-80GB，软件限制显存cache容量；附录A.4说明通过软件约束/延迟模拟硬件条件。文中headline性能包含TTFT，不能改写为L2周期收益或纯decode结论。[S4]

**我们的判断。**专家频率直方图相同，不意味着跨token访问序列相同；但这一思路已有直接近邻。新的C16 MoE问题应先证明连续时间数据足够、复用机会落在哪一层存储，再谈机制。不重做已关闭的E3 natural/balanced单次routing比较。

### 2.5 MonoNN：把复用间隔缩短也是路线，不只有延长驻留

**作者内容。**MonoNN把静态网络合为monolithic kernel，处理算子资源不兼容，以ILP/TLP权衡和片上缓冲组织执行；§4.3区分streaming与temporal访问，对后者使用cache hints。[S5]

**我们的判断。**“更早消费中间结果”可以与“保留旧权重更久”并列，但当前不值得重建完整MonoNN。此线只保留小型producer–consumer pair作为未来候选；融合导致寄存器压力、并发减少和同步变化，不能只数少了多少字节。

### 2.6 ATLAS：当前只登记，不能把摘要当结论

**作者摘要。**该预印本明确把MoE逐层访问与recency cache首次可能命中的容量联系起来，并研究recency/frequency切换与精确显存容量。[S6]

**我们的判断。**这已经足以提醒我们：“跨完整layer sweep后才可能复用”不是未经研究的问题。但全文未取得，不能据摘要宣布其理论等价于C16或排除C16创新。

## 3. 一个可直接用于选问题的分析推导

下面是基于MARLIN §3.4式(1)的**简化模型推导**，不是新增GPU实验，不是完整kernel时间模型。[S1]

考虑CTA tile：activation是FP16，尺寸`m_t × k_t`；weight是W4，尺寸`k_t × n_t`。暂不计scale/zero、输出、重读、冲突和同步：

```text
D_A = 2 m_t k_t bytes
D_W = 0.5 k_t n_t bytes
T_L2 ≈ (D_A + D_W) / B_L2
T_W  ≈ D_W / B_GMEM
```

在该模型下，要使L2供数时间不超过片外权重流入时间，需要：

```text
B_L2 / B_GMEM > 1 + 4 m_t / n_t
```

同样假设下，W16右侧是`1 + m_t/n_t`。这里的`m_t`是参与该tile供数的行数；只有tile跨整个batch时才等于总M。不能把E1总M=256机械代入某个m_t=16的kernel。

固定`n_t=128`的算术例子：

| m_t | W16所需比值右侧 | W4所需比值右侧 |
|---:|---:|---:|
| 1 | 1.0078125 | 1.03125 |
| 16 | 1.125 | 1.5 |
| 32 | 1.25 | 2.0 |
| 64 | 1.5 | 3.0 |

**含义：**压缩weight同时提高了activation相对weight的供数负担；因此即使缓存容量足够，L2/片内供数仍可能接替片外带宽成为限制。实际有效带宽、tile、metadata、SM并发均未代入，本表不能证明C16已经受该限制。

另一个独立估算：若`K`维被切成`p`个partial输出，每个partial用`b_acc`字节存放，单看一写一读的中间结果，其量级是`2 p M N b_acc`。这是条件化的流量尺度，不是额外流量的通用等式；真实实现可能直接写输出、融合归约或有不同读写次数，必须核源码。

## 4. 两类实验必须保持分离

### 4.1 C16机制主比较

同一个accepted SASS trace、地址sidecar、平台及完整reuse window；只切换L2策略。当前Lane 4与已准备strong baselines属于这一类。

### 4.2 实现稳健性探索

保持相同线性运算输入与相同解码权重，比较不同布局/数据流或kernel路径。换kernel意味着指令和访问序列改变，旧SASS trace不能代表新kernel。该比较只能另立native证据链，不能替换Lane 4的R0。

MARLIN原文§3.4采用对称INT4；FLUTE是LUT量化；当前C16 AWQ含scale/zero语义。因此不能把重新量化后的MARLIN/FLUTE模型与原AWQ直接当成“只换kernel”的因果实验。先核解码权重等价和实际后端支持。[S1–S3]

## 5. 建议优先的新探索：Lane 5 / LOWBIT_DATAFLOW_SCREEN

### 科学问题

> 当前低比特实现中的activation重复供数、反量化布局转换、reduction scratch，是否存在与跨token权重驻留无关、且对性能足够重要的成本？

这是待检验问题，不是对E1已冻结结果的新因果解释。E1已证明的是operator×M×implementation interaction，并未证明唯一cache cause。

### 本轮P0：只读existing artifacts，不新增测量

从E1 clean baseline consumer `59ddb8ba2a33ef12b73bfc859f3a994e0b4ef4ca` 与Semantic NCU V2 consumer `cdd3ec7afbb1611cc52a4b74d32b38a3edabd131`定位accepted producer/source。

只选`up_proj`和`down_proj`，消费现有M1/M256数据，不复测这四点。核：

- 实际kernel dispatch、GEMM/reduction/fill依赖关系；
- CTA/warp tile、K split、pipeline stages、寄存器及共享内存用量（现有材料披露多少写多少）；
- qweight/scale/zero/input/output/scratch在global、shared、register间的数据路径；
- 现有NCU是否能区分这些对象的流量；不能区分则明确unknown；
- 是否有对应源码/SASS证据支持QUICK型路径、MARLIN型activation供数或split-K reduction解释。

静态SASS次数不是动态次数，NCU总量不是对象归因；小tensor总字节少也不证明其critical-path成本小。

### P0交付只要三份

`DATAFLOW_EVIDENCE.tsv`、`HYPOTHESIS_SCREEN.md`、`MINIMAL_NATIVE_AB_PLAN.md`。authority/来源定位附在同一表中，复用已有校验，不建立新一套大工程。

最多留下两条真正可区分的假设；仅允许提出一组后续短native A/B设计，不在P0中执行。优先改变单个layout/pipeline/split控制量；数值误差与归约顺序变化必须单独说明。新holdout必须未参与选策略，不把以前已用于决策的E1点重新命名为independent holdout。

### P0停止/否定标准

如果路径已经规避相关成本、只是重复既有kernel优化，或现有证据不能区分假设，分别输出`NO_NEW_OPPORTUNITY` / `COVERED_BY_EXISTING_KERNEL_TECHNIQUE` / `NEEDS_ONE_BOUNDED_NATIVE_DIAGNOSTIC`。不要自动安装全套新后端、重抓trace或实现新cache机制。

不编译模拟器、不读Lane 4 active输出、不读全量D1-D3大trace、不占用109 GPU。只有用户另行下发短native实验，才走GPU lock与accepted input检查。

## 6. 第二候选：MoE时间结构，先做数据充分性判断

### 与E3的不同

E3的natural/balanced结论继续保留。这里另问：相同expert频率/每token激活数，跨token相关性与层间间隔是否改变可利用的复用？

必须先检查现有记录是否含`request_id, decode_step, layer_id, expert_id, order, expert_bytes`的连续对应。243个selected shards不是243个连续token；单layer replay不是完整模型时间线；不同模型的expert编号不可混用。

有连续序列时，可以做CPU-only序列诊断：在保留每层边际频率的条件下打乱时间顺序，只用于辨认时间相关性，不当作合法full-model执行或输出。expert级软件cache模型、cache-line reference proxy、真实L2事务和timing分层报告。无连续序列时停在`TEMPORAL_AUTHORITY_INSUFFICIENT`，不自动扩张为新的NVBit/full-SASS采集。

**当前排序：**这条留为Lane 6候选；不因SpecMD/ATLAS提到MoE就立即做通用expert cache。其论文近邻密集，首先需要一个区别于已有offloading工作的明确硬件问题。

## 7. 当前建议及不可做事项

建议布局：Lane 4不动；Lane 1/3保持冻结；另开Lane 5做低比特数据流P0，只读、小产出。MoE时间结构留作后备，不同时开两个大实现工程。

不做：新full timing、M1F启动、B8/B24/BFULL扩展、重新采E1/E3、更多replacement predictor、重建MonoNN、为追求论文数量泛化“所有MoE/所有低比特kernel”。

当前不是“研究方向已死”，而是把一个被长跑占住的机制问题与不依赖其结论的行为问题分开。最终是否投稿、采用何机制，仍由真实结果和强比较决定。

## 8. 原文入口与定位

[S1] MARLIN，arXiv:2408.11743v1，§3.3–3.5、§5：
https://arxiv.org/html/2408.11743v1
作者实现：
https://github.com/IST-DASLab/marlin
本轮读取README blob `ae24af61fed1ede9f06ca8f3b3b2985a1d93f12a`；未运行。

[S2] QUICK，arXiv:2402.10076，PDF §2.3–5：
https://arxiv.org/pdf/2402.10076
PDF文本已读；web screenshot多次失败，没有据未核图表估值。

[S3] FLUTE，arXiv:2407.10960v3，§3–4：
https://arxiv.org/html/2407.10960v3

[S4] SpecMD，arXiv:2602.03921v1，§3–5、附录A/D/E：
https://arxiv.org/html/2602.03921v1
只将作者描述的精度保持策略与改变routing/precision的策略分开讨论；未复现其cache或结果。

[S5] MonoNN，OSDI 2024，§4.2–4.4、§7.2：
https://www.usenix.org/conference/osdi24/presentation/zhuang
https://www.usenix.org/system/files/osdi24-zhuang.pdf

[S6] ATLAS，Zenodo v1（2026-08-04），仅作者摘要/metadata：
https://zenodo.org/records/21782951
https://doi.org/10.5281/zenodo.21782951
正文获取未成功；不纳入已全文核读论文。

本轮原文事实、项目冻结事实、分析推导、建议实验已分别标注。没有把外部论文的硬件、精度、cache层级、性能指标移植为C16事实。
