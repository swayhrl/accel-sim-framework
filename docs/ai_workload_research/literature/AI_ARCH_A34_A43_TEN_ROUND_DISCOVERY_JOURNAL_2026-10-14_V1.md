# AI-ARCH A34—A43｜十轮迭代探索：辅助状态寿命与稀疏执行

**研究者：ChatGPT／AI-ARCH Discovery；日期：2026-10-14。**

**授权与起点：** 用户要求在Lane M长时间执行期间连续进行十轮Discovery。协调起点`c2dc064265dafcb4f5cebfe9d0f75f150d10aeb1`，写入前compare为identical。本日志记录实际完成的A34—A43十个研究单元；每轮根据上一轮证据修订问题，不是十个新机制，也不是十项已授权的GPU任务。

**执行边界：** 仅公开文献、官方文档、固定Git源码及控制端纯算术。未访问109/174/164、GPU锁和执行目录，未运行模型、GPU、模拟器、编译或新Codex。M保持用户最后报告的A26GR1执行中状态；没有新终态，不预测完成时间。A30T/A30N原STOP、C16/AWMA历史authority不变。

## 0. 最终结论

保留两项近期**发现性问题**：

- **Q-S，直接神经网络方向：** 点云稀疏卷积的结构准备、布局转换和真实消费寿命，是否在强软件选优后仍有可定位的资源代价？
- **Q-A，较低增量成本备选：** A33图式ANNS每查询状态与查询并发的权衡，在同图/同质量及现成强路径后是否还有稳定剩余？

TBE训练状态作为第二层储备；过滤/动态图ANNS不继续扩建系统。没有任何一项已证明新硬件headroom、机制新颖性或本机可运行性。

本轮主动撤回/收紧三个直观想法：FROG已做过滤后再查hash；Spira提前全网映射没有作者场景下显著内存膨胀证据；搜索历史、坐标映射、部分和与optimizer状态不能统一使用遗忘策略。

## 1. 证据范围

新定点正文涉及Jasper、IVF-RaBitQ、FROG、GrAND、TorchSparse++、Minuet、Spira、Insum、SegFold；PCEngine、HSMU-SpGEMM只按可得摘要；CAGRA沿用A33锚点。另读WarpConvNet/FBGEMM/cuSPARSE官方文档、FBTriton作者技术文章及Spira四份固定文件。不是逐行审完全部论文，更没有复现作者结果。Spira以MLSys2026正式PDF为准，相关图文页已截图核对。

预印本不因版式里的PVLDB占位信息自动成为正式会议论文。在线文档标签不等于目标节点安装版本；固定源码快照不等于论文实验exact commit已核准。作者native、作者模型、源码能力、我们推导和本机native严格分开。

## A34｜先分开算法质量前沿与硬件资源响应

**承接A33：** 小历史表和更高查询并发是否构成新硬件问题，首先要排除已有软件/算法解释。

[Jasper原文](https://arxiv.org/html/2601.07048v1)已经移除一类历史hash以降低控制和状态负担；[IVF-RaBitQ §3.4/4](https://arxiv.org/html/2602.23999v1)又提供LUT与bitwise的计算—存储折中。两者不构成我们新发明的能力，且索引、量化或遍历改变可能改变实际工作。

**推导与修正：** 必须保留两类比较：固定图/输入/数值/算法配置时的资源响应；允许算法参数重新选优时的同recall性能前沿。前者定位因果，后者评价应用价值，不能用同一个“状态大小”字段把二者混成单一物理资源实验。A33三条single-CTA历史路径仍是软件状态策略诊断，AUTO是合法强参照而非严格单变量。

**最小反证：** 同recall下AUTO已接近最佳显式路径，或者计数变化不改变完整search时间，则停止对应硬件假说。若只有默认配置不佳，归类软件问题。首轮不必完整复现所有替代算法，但一般ANNS主张必须接受它们的反证。

**裁决：** A33保留为发现草案、因果口径收紧。下一轮查过滤条件带来的控制依赖。

## A35｜过滤检索：晚查hash已经被直接覆盖

[FROG v1 §7.3/8.1](https://arxiv.org/html/2608.16491v1)已将便宜过滤和compaction放在前面，昂贵hash检查移到距离计算前；仅把短路条件中的hash排在最后不等于这个实现。作者GPU为RTX5090，属性一部分真实、一部分由打乱ID生成；本轮按预印本，不推官方录用。

**新增问题而非机制：** 相同selectivity不保证相同访问行为，真实属性—向量相关性和候选重复要独立记录。属性随机化是诊断输入，不能伪装真实业务；过滤检索应对条件子集建立ground truth，不能拿无过滤搜索作同工作量基线。

**反证与决策：** “先便宜筛选、后查历史”“压紧活跃lane”已有FROG，不作为新硬件。没有强路径之后额外代价证据，不为此增加索引/质量/业务维度。过滤型ANNS降为储备，不否定整个领域。

**下一轮：** 检查动态图状态失效和维护成本是否提供更明确问题。

## A36｜动态图：删除快不等于维护便宜

[GrAND v1 §4–6](https://arxiv.org/html/2608.21163v1)已研究批量修复、按需反向图和GPU原地更新。关键实验边界：100M组的部分对照因容量关闭合并/清理，只保留tombstone，作者明确说明不是相同维护设置。因此这些吞吐不能直接成为相同代价的硬件比较。

**我们的推论：** 动态研究必须绑定操作流、查询当时的active set和延迟清理债务。只计标记删除而排除后续整理，会把成本挪出分母。内部并行更新、操作流交错和任意查询/更新并发下的快照一致性也不是同一合同。

**可证伪的小实验形式：** 只在各对照均能履行维护的规模，固定操作序列并计足够长的更新/清理区间，同时核实际active-set recall。不给只有一方能运行的容量条件包装成唯一速度优势。

**裁决：** 语义教训保留，但复杂度已高于A33静态search，不开动态图系统工程。下一轮转回神经网络本体的稀疏卷积。

## A37｜稀疏卷积：映射加计算才是完整边界

[TorchSparse++](https://arxiv.org/html/2311.12862v1)已经共同考虑mapping代价与数据流；[Minuet](https://arxiv.org/html/2401.06145v1)提供排序/映射及搬运优化；[PCEngine官方摘要](https://proceedings.mlsys.org/paper_files/paper/2023/hash/8e3e27d07b3f663b7f85c819b9692163-Abstract-mlsys2023.html)也有紧凑mapping和融合计算。PCEngine本轮不补造全文实验。

**问题收窄：** 更规整的GEMM可能需要排序、重排和准备。即便核心更快，完整层也可能没有收益。因此不要从间接地址多直接设计访存单元，而应固定坐标、数值和消费者，测已有强数据流之后准备—转换—消费的真实成本。

这里结构映射、权重驻留与运行库scratch是不同对象。未来只需一个实际层组和两条强路径，不以完整自动驾驶系统为首轮目标，也不要求一个新稀疏格式。

**反证：** 完整边界的差异被普通数据流选择解释，或准备在实际复用区间已充分摊销，则不进入硬件。

**裁决：** 新增直接神经网络发现对象；下一轮必须面对更新的Spira，而不是停在旧hash基线。

## A38｜Spira反证：提前生成映射没有必然内存爆炸

[Spira MLSys2026正式论文](https://proceedings.mlsys.org/paper_files/paper/2026/file/7972f3735e104a54715922aa416fde1b-Paper-Conference.pdf)已利用坐标性质和网络级提前映射。PDF第9页明确：与逐层生成后缓存的方案最终映射占用相近，映射平均约40MB。不能据此编出“eager mapping必然挤爆片上资源”的动机；这里也不是SMEM或L2实测占用。

**本轮独立源码核验：** 固定`SPIN-Research-Group/Spira@aee69c61f3e001f72828a6d5a70f6a1200166f65`。

- [conv.py](https://github.com/SPIN-Research-Group/Spira/blob/aee69c61f3e001f72828a6d5a70f6a1200166f65/source/spira/nn/conv.py)，blob `29159eed4cb5f3fab28b85bfa815dff6c2ec62bc`：cache reset、stride/kernel-size key、批量build；部分force_os/transposed命中路径仍可能做布局转换。
- [end_to_end_experiment.py](https://github.com/SPIN-Research-Group/Spira/blob/aee69c61f3e001f72828a6d5a70f6a1200166f65/scripts/end_to_end_experiment.py)，blob `b724a82a658f94f39d7ff28b58c6c9f8839723d5`：逐输入reset；计时区内包含order、add_all_kernel_maps和model。不能说作者漏算这些准备成本。

**修正：** cache命中不等于所有消费者布局已就绪，但存在转换也不证明它在关键路径。缓存键没有全坐标identity不能单独当bug，因为caller新输入会reset。

**裁决：** 否定无根据的大容量动机，保留强基线和实际生命周期问题。下一轮检查准备寿命，而不是继续静态数buffer。

## A39｜准备寿命与核执行：一个可复算的摊销问题

[Insum v1 §6.7 Table3](https://arxiv.org/html/2510.17505v1)分别列编译、调优、格式转换和核成本。其conferenceRoom FP16/C128例子，RTX3090格式转换0.55ms、核0.47ms，正文TorchSparse核0.66ms。[WarpConvNet官方文档](https://nvlabs.github.io/WarpConvNet/user_guide/sparse_convolutions_internals/)又区分forward、dgrad、wgrad的执行和映射组织；不能假定一套布局三阶段都最优。

**我们推导，不是新实测：** `T_j=P_j+ΣK_j`。若每次消费相同，快核值得选择的条件是`q*(K_ref-K_fast)>P_fast-P_ref`。示意把**额外准备**假设成0.55ms、核差0.19ms，严格获益需整数q至少3。但参考后端完整准备未配对，因此“三次”绝不能称作者/本机实测交叉点。

编译cache可跨多个坐标输入有效，mapping可能每帧失效，两者分账。不能长期摊销掉每帧必做的结构准备；同样不能为了造大成本，让真实可共享的每层都重新build。

**最小设计：** 采用真实层组自然发生的复用次数，记录结构建立、转换、各consumer及末次使用。人工重复同一结构只作模型诊断。强后端独立调优，但必须计各自完整合法生命周期。

**裁决：** “结构准备有效寿命与执行组织”成为Q-S；尚无新硬件残余。下一轮检查数值状态能否使用类似权衡。

## A40｜数值累加器不能照搬遗忘搜索历史

[HSMU-SpGEMM出版者摘要](https://ieeexplore.ieee.org/document/10946796/)已有hash累加与shared-memory组织，本轮只是摘要；[SegFold v1](https://arxiv.org/html/2606.26701v1)已有动态调度和部分和映射，其性能来自cycle模型、硬件资源来自RTL估算，不是本机GPU或流片。SuiteSparse集合也不自动是AI模型证据。

[cuSPARSE 12.6.3归档§6.6.13](https://docs.nvidia.com/cuda/archive/12.6.3/cusparse/index.html)允许输出结构跨数值计算复用，且说明中间产品存储要求。在线13.4出现弃用标签不能覆盖目标版本合同，不能把reuse读成零buffer。

**语义反证：** 搜索visited历史可在算法允许时遗忘并重算距离；数值partial sum丢弃后继续会漏贡献，重算后不区分贡献集合又会重复累加。任何溢出、压缩或重算方案必须说明贡献恰好一次及输出值/结构/舍入规则。它不是把表做小就完事。

**裁决：** 不设计统一稀疏状态Cache。SpGEMM暂作语义/硬件近邻，没有新增AI workload资格。下一轮看带optimizer更新的真实训练算子。

## A41｜TBE训练：成本前移不等于成本消失

[2026-10-06 FBTriton官方技术文章§2–5](https://pytorch.org/blog/modernizing-table-batched-embeddings-with-fbtriton/)已有metadata hoist、长短run分派和融合optimizer。一个B200配置的forward `22.844→33.252ms`，backward `56.693→32.931ms`，总和`79.537→66.183ms`。

**独立复算：** backward少23.762ms，但forward多10.408ms，净少13.354ms、约16.79%。这是作者一个配置的算子前后向总和，不是整个推荐模型训练步。不能只把反向节约称全部成本消除。

**数值边界：** 同一(table,row)应先合并全部上游梯度再做一次exact optimizer更新。标量反例`(1+2)^2=9`而`1^2+2^2=5`，说明每次出现分别更新Adagrad一般不等价；这不是完整rowwise实现验证。

强CUDA/Triton和已有分派之后是否仍有真实代价才是问题。作者部分Blackwell功能不能套成Ada现成能力，307配置也不等于我们已取得全部自然输入。不能再把hoist、split或fused optimizer直接作为新硬件。

**裁决：** TBE留储备，不新增训练平台。下一轮回查点云真实输入，避免候选身份过度提升。

## A42｜源码中的真实输入到底真实到哪一层

固定[Spira loaders.py](https://github.com/SPIN-Research-Group/Spira/blob/aee69c61f3e001f72828a6d5a70f6a1200166f65/scripts/loaders.py)，blob `caa9747c42108b50617212e4798ed5e81df04420`：读取npy坐标并shuffle/平移，特征由`torch.randn`生成。结合所审端到端入口构造网络、未见checkpoint加载，这应称**真实稀疏几何驱动的结构型执行**，不是训练好模型的任务质量验证。

**不是不合法，也不应因此阻止全部发现实验。** 如果问题仅由坐标、通道和dtype决定，可用限定的结构型输入诊断mapping/执行组织；需证明被替换数值不改变相关工作，固定种子和数值并跨后端对齐输出。主张实际分割精度或值驱动pruning时，另需要真实模型。不能把任意随机坐标和真实坐标混为一谈，也不能强制下载完整checkpoint才允许坐标型研究。

同样，新scene不能凭相同stride继承旧map；同一scene的合法复用不能每层强制失效。下采样、坐标/输出排列都属于身份。

[固定README](https://github.com/SPIN-Research-Group/Spira/blob/aee69c61f3e001f72828a6d5a70f6a1200166f65/README.md)，blob `51df5502ff865956129a541f914bf9278b823041`，给整套artifact的64GB主存/256GB盘/16GB GPU建议及baseline patches；这不证明一个小probe必需整套空间，也不证明109预算已够。不得照抄run_all并下载三套完整场景。

**裁决：** Q-S保留为结构型发现问题，本机/任务精度未资格化；最后收敛两个小实验出口。

## A43｜两项最小反证设计与最终排序

### Q-S：点云稀疏卷积的结构准备—布局—消费有效期

这是**直接神经网络相关性优先**的对象。选一个真实坐标对象、一个实际层组与最多两条强可实现路径；先核Spira及适用TorchSparse++/Minuet，Insum/WarpConvNet作为能力反证，不要求一次部署四种后端。

固定坐标、下采样、输入权重/特征、dtype和数值容限；区分新结构建立到最后使用的完整区间、合法map复用、命中后的布局变换和峰值活状态。真实复用次数是输入/网络事实，不能人工repeat冒充自然执行。Spira已含mapping的基线保持强，不能移出其准备后再重组出虚假对照。

先获取完整时间与必要对象身份；出现可区分差异才加有限NCU/资源干预。缺完整oracle不阻止小发现，缺真实性能则不能进入硬件结论。若普通后端选优消除差距，归类软件/无机会，不挽救新Cache。

### Q-A：ANNS历史状态与查询并发

它是**部署规模和增量成本优先**的备选。保留A33同图、真实query与质量要求，3batch×4现成路径只作未授权草案。先看AUTO/显式配置是否有稳定完整时间差，再区分访问工作改变与资源服务。不能把recall或遗忘策略变化叫物理容量干预；也不要求首轮完整复现Jasper/IVF。

### Q-E：embedding训练储备

只有有合格ID/run分布、适用强后端和完整forward/backward/update分母才进入小诊断。不为作者少数小弱点立即做新硬件，不把GB200数字移到4080。

### 统一决定

十轮结束保留两项近期发现设计、一项储备，**不是十个新机制或三个待运行Goal**。当前无新GPU/模拟器/Codex授权。M完成后按原合同独立审查；随后若选中一个候选，将必要环境/输入/功能canary和小矩阵放在一份连续有界合同中，不以更多source-only轮次替代必须实际测的证据。

机制阶段需另证明：强软件之后的具体资源/就绪约束、在线可获得的信息、有限buffer/带宽/端口/同步成本、非目标退化和独立样本。目标family、应用加权和端到端分开；不以统一全应用5%门槛替代机制科学判断。不存在本轮已验证的硬件瓶颈、PPA或加速承诺。

## 附：算术、归档与未完成项

控制端用Decimal重算三项：Insum条件摊销阈值、FBTriton时间分母和梯度合并反例；不是GPU模拟。配套`AI_ARCH_A34_A43_DERIVED_LEDGER_2026-10-14_V1.json`只记录这些计算。

本日志为Git科研记录；本会话另输出完整扩展报告、十份逐轮笔记、来源/阅读范围JSON、可运行算术脚本与校验包，不含论文PDF或服务器raw。当前未知仍包括新后端ABI、实际数据完整SHA、目标平台峰值、自然层组复用、强软件后的完整时间和机制因果。未披露的作者细节不补造。

源审/实验发现/硬件晋升分层：某项准备存在不等于瓶颈；某项软件能提速不等于硬件空白；某项实现不在4080可运行也不等于领域没有价值。保留问题，但不把每个缺口都变成昂贵复现工程。
