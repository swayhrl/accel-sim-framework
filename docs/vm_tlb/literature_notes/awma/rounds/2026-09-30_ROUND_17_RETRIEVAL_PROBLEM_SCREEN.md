# Round17｜Round16之后的问题重选：检索执行与已有能力核查

日期：2026-09-30。工作类型：ChatGPT文献、源码和研究设计；不是execution Goal。

## 0. 结论与授权边界

本轮不再恢复R101、R102、VLA/VJP、CCE zero-init，不启动109或174的新实验，不下载模型/数据，不创建执行分支。Lane E/F/G仍为STOP。

**本轮只保留一个优先准备候选：单GPU驻留图向量检索中，成熟执行模式之后的低并发在线遍历成本。** 这是待验证的问题，不是已定位瓶颈或新机制。MaxSim原本是第二候选，但进一步源码核查发现现有实现已提供分散文档直接评分，故不为凑两个问题而启动它。

最近邻具备某种能力，不等于它在所有平台都最优；但我们必须先说清新增问题相对该能力还缺什么，不能只复述已实现功能。

## 1. 继承的最新内部证据

直接重新读取：
- `31d585dc44f90eb70f83603c8b87a2d06efff01a`中的`docs/vm_tlb/chatgpt_handoff/awma/round16_dual_lane_v1/FINAL_ROUND16_CLOSEOUT_2026-09-30.md`。
- 文献分支原HEAD `c6958df456393b46a9268add5898bbd7f12c1ca9`的README、Round06、Round09；结合本对话已提供的Round15/16事实。

| 内部问题 | 已得到什么 | 本轮如何继承 |
|---|---|---|
| R102真实更新 | 真实相邻权重authority未通过，CUDA=0 | 输入未资格化不是GPU negative；休眠，不继续广撒网找hash |
| VLA/RTC-VJP | 修复后完整network VJP真实；目标state/lifetime份额仍未知 | 未知不是已证无空间；此次不因换一套profiler重开 |
| CCE zero-init | 同shape局部软件协议拿回11.85%，取消全dC预清零 | 保留可复用软件结果；关闭该已测试zero-init硬件动机，不外推整个loss领域 |
| 旧扩散、selector、MoE、TT、LoRA候选 | 文献中已有多项强能力；部分问题有accepted narrow negative，部分仅阅读过 | 按具体问题区分，不能把旧设计中的“待做”当最新执行状态 |

另保留既有双轨原则：现象驱动与文献驱动的小原型都可用于发现问题。5%是具体任务的投入筛选阈值，不应追溯变成所有探索必须先完全证明的普遍定律。可测但尚未解释清楚的响应可以继续有界定位；不能把缺乏解释直接称负结果。

## 2. 本轮来源与阅读深度

13项论文/预印本：5项取得HTML正文并检查关键机制、实验范围或限制，8项仅取得作者/出版方原始摘要。另核NVIDIA官方CAGRA文档、Jasper作者README以及Flash-MaxSim函数源码。不是13篇全文精读，也不是新的Native复现。摘要仅用于判断直接能力是否已有，不能补填未取得的实验细节。

| ID | 工作 / 来源 | 本轮深度 | 与筛选有关的能力或边界 |
|---|---|---|---|
| R1701 | CAGRA, arXiv 2308.15136v2 / ICDE2024 | KEY：IV-B/IV-C/IV-D，V | 已有warp splitting、forgettable hash和single-/multi-CTA；不能把一query多CTA当新能力 |
| R1702 | GPU-Accelerated Algorithms for Graph Vector Search, 2602.16719v1 | KEY：3、4.1、4.3、4.4 | 原始实证区分驻留search、含传输流程及CL/DC/DM组成；传输口径包含graph/data搬入，不直接等于常驻服务每次query开销 |
| R1703 | Jasper, 2601.07048 | ABS + 作者README | 已有GPU-native graph、RaBitQ、改进greedy search和可更新接口；性能结果仅按作者摘要，不宣称SM89已运行 |
| R1704 | BOA, 2609.16175 | ABS | 已研究filtered-ANNS按query在线调beam及阶段重叠；不是我们新提出的自适应浅搜 |
| R1705 | GrAND, 2608.21163 | ABS | 已研究GPU图插删、批内合并repair和并行邻接更新；本轮不转动态索引大工程 |
| R1706 | WARP, 2501.17788v2 | KEY：3–5 | 多向量检索中的隐式解压、分阶段归约；主要评估CPU，不能与GPU kernel数字当同硬件比较 |
| R1707 | TileMaxSim, 2606.26439v1 | KEY：方法、6–8 | 已有融合MaxSim、PQ、dimension tiling；固定长度及数据驻留边界明确；真实/合成大规模点需分开 |
| R1708 | Flash-MaxSim, 2605.29517v1 | KEY：4、5 + 作者源码 | 已有融合forward、varlen、inverse-grid backward；源码进一步提供offset/length直接读取分散文档 |
| R1709 | Chimera, 2608.23553 | ABS | 已把压缩GPU索引与CPU高精度评分协同用于消除向量传输；近似/系统合同不能冒充固定FP16同函数干预 |
| R1710 | ARC, ASPLOS2025 | 作者摘要 | 同地址原子更新的warp归约、core/L2分工已有SW/HW方案 |
| R1711 | GSGPU, ISPA2025 | 出版方摘要 | 已有3DGS训练负载平衡与分级原子归约；不凭“3DGS新”重新命名同一方案 |
| R1712 | FlowTT, 2609.03459 | 原始摘要 | prefix共享、融合收缩、persistent/work stealing和L2 checkpoint已有；未读全文的剩余边界保持未知 |
| R1713 | ELORA, HPCA2026 | 出版方摘要 | LoRA/KV依赖管理与统一成本换入换出已有；generic adapter cache不立项 |

原始链接见末尾。公开日期以arXiv/出版方记录为准，不使用HTML模板中残留的会议日期作为发表日期。

## 3. 为什么不直接挑另一个大中间张量

Round16 CCE展示的是：发现完整累计器、测出显式清零、再用很小的软件协议取消清零。下一轮不能把`T×V`换成另一个`N×M`张量就重新开始同一论证。

本轮MaxSim筛查正好说明这一点。最初的两个想法分别是去掉相似度矩阵，以及候选ID就绪后不再复制/打包文档。第一项由TileMaxSim/Flash-MaxSim直接覆盖；第二项也被Flash-MaxSim已发布源码覆盖了相当一部分。

### 3.1 Flash-MaxSim源码实际提供什么

实际读取：
`roipony/flash-maxsim@48ed5f5f7bd388838edacb7060148e7344442e26`
`flash_maxsim/flash_maxsim_rerank.py`，blob `56bd560b098360cd9cab70063f8d950746ec1b69`，文件前250行。

`flash_maxsim_rerank_direct`接收共享二维embedding存储和每个候选的offset/length；kernel据此加载每个文档，不要求候选在存储中连续排列。wrapper对非连续存储或非FP16输入仍会产生转换，且需要小型元数据和输出分配。因此允许结论是：**固定连续FP16底层存储条件下，按文档offset直接评分已有软件接口**，不是“任何输入零拷贝、任何类型零成本”。

kernel按max-length bucket循环并用mask处理短文档，也不意味着所有变长执行浪费已经消失。但单有这个代码观察不足以成为新硬件问题；不能为验证一个可能很小的循环mask开销立刻搭完整检索系统。

### 3.2 不采用跨口径的巨大speedup

WARP主要是CPU完整检索；TileMaxSim大batch评分和CPU WARP的比值不是纯GPU结构增益。TileMaxSim正文中，小候选集的真实集成示例与大候选数评分表的输入/范围不同，也不能据大候选kernel吞吐推导真实query总收益。

因此，本轮MaxSim方向状态是“直观能力已被直接覆盖，暂不进入执行”，不是我们测出了Native negative。更复杂的压缩索引或host/device协同又必须面对Chimera等最近邻，不能自动成为后备机制。

## 4. 唯一优先问题：驻留图检索的在线依赖与可用并发

### 4.1 具体问题

> 在图与向量常驻单GPU、使用合格CAGRA/Jasper级软件、保持检索质量条件下，少量并发query的完成时间，是否仍由“当前候选处理完成后才能发现下一批有用访问”的在线推进限制？还是已有multi-CTA、persistent及普通软件已经足够，剩余主要是距离算术？

这不是预设“随机访存一定慢”，也不把query batch变大后的吞吐提升称为单query加速。

不同于P2 selector→indices→attention的一次交接，此处地址发现、距离评价、候选/visited维护反复反馈。不同于R101，首先在真实GPU/成熟检索实现观察，不先造local oracle。**上述差别是研究对象差别，不是已证明的性能差别或创新性。**

### 4.2 已知能力是最低比较起点

CAGRA已经针对小batch设计multi-CTA，且它与single-CTA的visited表位置、推进方式及访问工作可能不同。NVIDIA当前文档还提供persistent search，但只适用于SINGLE_CTA。Jasper又把greedy traversal、压缩与并行执行共同设计。

因此禁止以朴素Python循环、单CTA固定小batch或每次搬入整个index作为唯一baseline；禁止从不同mode的时间差直接计算“依赖开销”。BOA的beam自适应会改变搜索工作，GrAND的动态更新会引入另一个生命周期，两者本轮只作最近邻，不加入首轮实验。

### 4.3 反例已经足够强

R1702原始实验并未把所有GPU图检索都判为随机访存主导；其分析强调距离计算与传输条件。它在A800与大批query上的结论不是4080小batch的直接答案，但足以否定“看到pointer chasing就设计cache”的推理。

我们可能最终得到：合适multi-CTA消除低并发损失；persistent只去掉host launch；距离计算占主要时间；或者某项visited/queue维护有真实剩余。四种都是合法终点。

## 5. 下一步最小设计：先能力和输入，暂不下发Goal

详细卡片：`../problem_cards/R17_GPU_RESIDENT_GRAPH_SEARCH_PREPARATION.md`。

### 准备阶段要交付的三项东西

1. **可执行能力表**：锁定cuVS/CAGRA实际版本，核清SM89支持、single/multi-CTA、persistent前提、workspace和C++入口；读取Jasper相关接口作为强近邻。API存在不是109 runtime资格已通过。
2. **真实输入候选**：优先可公开取得database/query/ground-truth的一个learned-embedding benchmark。DEEP1M可作明确可行候选，但须实际核原始下载源、字段、dtype与license；它是图像embedding，不冒充自然RAG文本请求。另留一个独立来源候选，只登记，不先下载。
3. **计时边界**：index build、一次性index upload、query-ready到结果ready、host dispatch、GPU search分开；同一query集合在少量并发与较充分并发下比较，不能把总kernel时间直接当服务尾时延。

这些准备可以形成下一条短Goal的输入，而不是再次搭通用catalog。当前未发送执行指令。

### 有条件的首轮Native草案

- 一个静态index；一个query集合预先分发现/验证。
- 两档并发而非完整sweep，例如1和32；最终数值由源代码支持/资源检查一次冻结，而非见结果后调整。
- 性能基线包括合法的既有低并发实现；persistent仅在支持的模式下独立看launch因素，不能与multi-CTA混成单一干预。
- 算法对比按预设recall@k与相同数据/精度约束比较；单一实现内部的诊断保持graph、seed、search parameters和停止规则。近似检索不额外强加毫无应用根据的逐bit同输出要求。
- 先轻量时间与工作量账本：distance evaluations、迭代、重复访问、visited/selection、kernel/dispatch；日志观测与正式计时分开。
- 只有出现具体未解释、影响完整query的剩余，才选择一个诊断或文献驱动有界原型。禁止预载未来遍历路径；此类oracle只能作为明确标注的离线诊断，不能是可实施候选。
- 若已有软件充分、主要是必要算术、或剩余仅来自wrapper，则停止硬件方向；UNKNOWN单列，不当作失败也不自动升级。

不开展动态插删、过滤谓词、CPU offload、NVMe、multi-GPU、完整RAG服务、SASS trace或Accel-Sim。它们是其他问题，不在一个screen里全做。

## 6. 本輪排除与保留总表

| 问题 | AWMA当前证据 | 本轮决策 |
|---|---|---|
| CCE大累计器预清零 | 真实软件反证已解决 | 不续跑cast/第二shape |
| VLA完整VJP状态 | 工作真实，目标残差未知 | 保留UNKNOWN，不重开 |
| R102真实稀疏更新 | 输入缺口 | 保留休眠，不改synthetic |
| MaxSim矩阵物化 | 本轮未跑；直接最近邻已有 | 文献阶段筛掉直观机制 |
| MaxSim分散文档打包 | direct offset/length接口已有；通用输入有边界 | 不自动进入GPU |
| 3DGS warp内原子归约/分级合并 | ARC与GSGPU已有；本轮只读摘要 | 不以generic原子聚合立项，不声称3DGS领域无空间 |
| TT prefix共享中间值 | FlowTT摘要直接覆盖 | 待具体新差异，不重开旧Q93 |
| LoRA/KV依赖缓存 | ELORA已有 | 不做generic adapter cache |
| 驻留图检索低并发在线推进 | 本次核读AWMA记录未见匹配Native boundary | 唯一优先准备候选；尚无硬件动机准入 |

本轮没有第二个同样明确的候选。一个有具体强基线和反例的问题优于两个宽泛的新标签。

## 7. 原始来源

R1701 https://arxiv.org/html/2308.15136v2
R1702 https://arxiv.org/html/2602.16719v1
R1703 https://arxiv.org/abs/2601.07048
R1704 https://arxiv.org/abs/2609.16175
R1705 https://arxiv.org/abs/2608.21163
R1706 https://arxiv.org/html/2501.17788v2
R1707 https://arxiv.org/html/2606.26439v1
R1708 https://arxiv.org/html/2605.29517v1
R1709 https://arxiv.org/abs/2608.23553
R1710 https://pawks.github.io/publication/asplos-2025/
R1711 https://doi.org/10.1109/ISPA67752.2025.00014
R1712 https://arxiv.org/abs/2609.03459
R1713 https://doi.org/10.1109/HPCA68181.2026.11408492

官方能力：
https://docs.nvidia.com/cuvs/user-guide/api-guides/indexing-guide/cagra
https://docs.nvidia.com/cuvs/api-reference/c-api-neighbors-cagra
https://docs.nvidia.com/cuvs/api-reference/python-api-neighbors-cagra

作者源码：
https://github.com/roipony/flash-maxsim/blob/48ed5f5f7bd388838edacb7060148e7344442e26/flash_maxsim/flash_maxsim_rerank.py
https://github.com/saltsystemslab/Jasper/blob/main/README.md （本次读取blob `81ffb42abed0be62b38234ec43f588b2cbc5040e`；不是已固定的实验runtime）

## 8. 当前执行状态

Lane E/174-new、Lane F/109、Lane G/109全部保持STOP。仅文献分支新增本轮记录与准备卡，accepted实验分支不改。下一次GPU或模拟器任务必须有新的明确授权和冻结入口。
