# Round18｜2026 AI负载与GPU体系结构全面横向复审

日期：2026-10-01。作者：ChatGPT。类型：文献、源码与已有证据复审；不是execution Goal。

## 0. 结论、范围与交付

**本轮优先准备两个问题，不授权节点执行：**

1. **低比特计算的表示就绪路径**：数值、分组scale、布局和同步共同交付给consumer时，成熟融合软件之后还剩什么限制？
2. **动态工作集的执行组织**：可用工作在线变化时，已有graphs、varlen、persistent和动态megakernel之后，有限调度/状态存储是否仍有成本？旧R53属于可能承载它的设计，不重新命名成“全新未研究方向”。

第三项只保留源码资格：推理期fast-weight更新中，哪些真实算法不能直接化成线性attention/scan，且是否值得做局部执行研究。Agent缓存、消费级GPU混部、通信、视频、稀疏计算、可靠性和能耗均纳入比较，但不同时开工程。

本轮核心登记**41项论文/预印本/作者技术说明**：15项回到正文关键机制、实验设置或限制；26项本轮只核原始摘要/会议作者页。另核3份公开作者仓库文档。**不是41篇全文精读，不是41个全新工作，不是已复现41篇论文。** 新旧版本分开；部分2025来源作为2026工作的基准。不把网页模板会议名当录用证据。

配套：
- `../empirical/ROUND18_SOURCE_REGISTER.tsv`：41项来源、深度、范围、限制。
- `../empirical/ROUND18_EXPERIMENT_EVIDENCE.tsv`：60条实验/分析证据记录。含摘要级aggregate；不称60组均已取得完整复现参数。
- `../empirical/ROUND18_AWMA_BOUNDARY_LEDGER.tsv`：已有/未做/未知边界。
- `../problem_cards/R18_SHORTLIST_AND_MINIMAL_TESTS.md`：两个优先准备问题和一个条件候选。

所有外部事实按P编号追溯；作者源码文档按C编号。各记录中的“未披露”仅指本次指定版本/核查范围；“未核实”表示未完成验证，二者不混用。大模型、数据集未下载；没有CUDA、NCU、NSYS、NVBit、Accel-Sim或新lane任务。

## 1. 首先修正我们自己的证据边界

### 1.1 R17不能从Q1小于整批Q32推出“没有单query空间”

本轮重新读取R17R1 `29ecc6e5e37005046b1a563c830bed9ae58af656` 的FINAL_DECISION。质量、计时与资源复用事实保留：MULTI_CTA512/1达到recall门槛；256次独立Q1约56.11ms；单Q1约0.215ms；整批Q32约0.531ms。原实验确实没有把Q32/32叫作单query时延。

**但反过来，Q1<整批Q32也不能证明低并发不存在可优化的等待。** 两个请求工作量不同，没有相同工作的可实施干预、必要计算下界或实际SLO需求。纯GPU时间未资格化，host/device未分离，且recall也略不同。

因此保留原执行标签和STOP决定，不改raw/review pack；本轮的研究判断收紧为：**已建立质量合格、资源复用后的成熟CAGRA基准；尚未识别可归因的GPU-local残差。** 这不足以证明软件全局充分，也不足以要求立刻重开实验。选择停止投入是合理决策；把未知写成已证不存在则不合理。

### 1.2 Round16的三种终点必须分开

重新读取Round16 `31d585dc44f90eb70f83603c8b87a2d06efff01a`：
- R102：真实相邻权重输入authority未闭合；没有GPU性能实验，不是稀疏更新无价值。
- VLA：修复后的完整network VJP真实且有成本；目标state/lifetime份额未分离，不是证明内存不重要。
- CCE：`ec1ccad7bbcead8853cd97840a2007d96f325aa3` 的first-contributor协议在固定shape中取消全dC预清零，并有11.85%同轮配对收益。这是有明确干预证据的软件可消除结果；不泛化到所有loss或所有归约。

R101的模型内oracle响应与Native主导压力不匹配，足以阻止当前动机直接进入机制；它也不是“GPU memory无价值”或“模拟器全部错误”。

### 1.3 不让筛选规则把探索空间锁死

继承用户已有双轨原则：现象驱动与文献驱动小原型都合法。**不要求先证明统一的5%上界才允许动手。** 5%只在明确任务中用于投入筛选；没有测出某项开销不等于上界为零。候选可以改变结构、策略或接口，冻结的是比较基准与证据解释。

前人提供了相似能力，意味着需要面对该能力，不意味着整个问题已解。反过来，换模型、换数据名、把软件接口改叫硬件也不产生新颖性。

## 2. 全景：研究现在推进到了哪一层

| 问题族 | 已有工作推进到哪里 | 仍需区分的边界 | AWMA现状/判断 |
|---|---|---|---|
| 低精度训练与推理 | FP4存储/通信、FP8计算、直接转换、转置scale、混合QK/PV；P001–P008 | 容量收益、重算减少、真实低比特算力和转换成本分开 | RAW/AWQ不是该完整链；优先准备 |
| Tensor/非GEMM非对称扩展 | FA4的softmax与SMEM优化；P006/P007/P011 | 矩阵更快以后，scale/归约/交付是否成为必要瓶颈 | 旧资源倍增不能替代此问题；需新平台边界 |
| 编译器与动态megakernel | Event Tensor、Nautilus；P009/P010 | 动态ready工作、寄存器/状态开销与静态专门化取舍 | 未做匹配强基线；优先准备 |
| MoE少token/expert | MonoMoE weight-major完整融合；P012 | 自然route、精度、完整dispatch→combine合同 | E3只验证routing proxy；不称MoE已测完 |
| SSM/线性attention | ReplaySSM输出式计算、TreeWY树验证、SketchSSM近似读；P013–P015 | 同输出容差、近似质量、flush均摊和完整服务 | R54不是SSM datapath；直接边界未测 |
| 推理期学习/fast weight | TTT线性attention归约、TTT-NTP；P016/P017 | 固定特征与动态特征/weight normalization不能混 | 与冻结权重的VLA VJP不同；源码资格候选 |
| 扩散语言模型 | Flash-dLLM、HERALD；P018/P019，旧R53基线 | 性能实验固定步数是否覆盖自然动态步数；缓存近似与映射 | 已读R53为设计稿，未取得完成receipt |
| Agent/KV共享 | ForkKV、TokenDance、IntentKV、KVShareArena；P020–P023 | 语义可复用不等于同地址；有损共享不是无损CoW | R102/普通prefix不能替代；当前不抢主线 |
| 工具等待与服务调度 | TokenCake、Libra、BatchGen；P024/P037/P038 | 关键路径、TTFT/TPOT/goodput/批完成时间不同 | 有很多系统能力；不从kernel吞吐推业务收益 |
| 视觉/视频生成和分析 | Xema、CoStream；P025/P026 | 生成vs理解、稀疏近似、请求模板与真实到达分开 | VLA不代表视频；有新负载但前处理近邻强 |
| 抢占/混部/消费级容量 | Hummingbird、Valve、Nixie、SERENO；P027/P028/P035/P036 | preemption、memory reclaim、pin内存与前台QoS协同 | 单模型UVM negative不覆盖；有平台/工程门槛 |
| 无损压缩与层级存储 | IBP、FRUGAL；P029/P030 | CPU预处理、PCIe搬运、resident消费、重算的成本 | AWQ不是lossless；缺完整encode→consume测量 |
| 通信计算协同 | MSCCL++、Event Tensor；P031/P009 | 软件已有细粒度通信；资源竞争和真正重叠空间 | 109单GPU不能实证多GPU网络收益 |
| 稀疏算术与结构 | Uni-STC、moderately sparse GPU；P032/P033 | 任意稀疏与2:4映射、pruning质量、模拟与实机 | 未测；不能直接把padding比例当收益 |
| 地址翻译 | DEPOT P034及旧MPW/LATPC等 | 特定替换问题≠所有LLM翻译；新场景需新输入 | resident已测窄边界，不重开旧coalescer |
| 移动异构/可靠性/能耗 | AHASD、真实故障分布、功率动态模型；P039–P041 | 硬件估算/故障注入/系统功率模型各自范围 | 仅外围原始摘要筛选；不宣称全面深入覆盖 |

## 3. 最有影响的发现一：FP4的“数据更小”和“计算更快”已明显分家

### 3.1 Practical FP4的12.5%不能读成FP4 GEMM快12.5%

P001在Hopper上用MXFP4保存activation及通信，但MoE GEMM仍是FP8；代码路径主动避免FP4↔BF16↔FP8往返。反向侧因转换代价大，部分流程保留FP8。

必须拆开其三组证据：
- 671B、同一完整recompute策略：FP8为1157 TGS，MXFP4为1156 TGS；是近似吞吐持平、显存下降。
- 减少recompute后MXFP4到1302 TGS；吞吐提升包含消除重算，不是同一算术组织只换bit数。
- 236B同recompute比较，FP4并非每点更快；局部dense转换链甚至慢于TE，grouped MoE转换才占优。

**研究启发**：先研究producer输出怎样以consumer需要的数值/scale/layout到达，可能比再比较整模型FP4和BF16更能识别架构限制。但直接转换、融合和转置已有，不能当新机制。

### 3.2 转置一致性是数值合同，不只是transpose带宽

P002通过二维block量化让前向/反向转置视图共享更一致的量化表达；它评估训练收敛，正文明确系统没有原生FP4算力，采用量化模拟。其理想加速/内存模型不能写成实测FP4训练速度。

如果硬件想避免保存两种布局，必须先问两种视图是否可共享同一组scale及舍入结果。只省一次转置但改变训练数值，不是同一合同的结构优化。

### 3.3 Attention越低比特，不一定越快或越稳定

P003 MpFA采用混合QK/PV精度；P007把非因果Direct-P与因果训练分开，原始摘要还报告测试过的MXFP4 P/V分布式训练轨迹发散。P008在Ascend HIF4上研究量化概率与normalizer一致性，但35.4%时延减少是指令调度预测，摘要明确尚待实机验证。

作者公开FP4 FA4源码文档C002/C003又提供具体成本边界：P量化不仅有convert，还有group max、scale与寄存器/共享存储/TMEM交付；部分优化已经落地。调试文档指出细粒度clock插桩会阻碍编译器调度，局部区间可膨胀15–30%。**这些是作者实现诊断，不是我们测得的GPU通用规格。** README前部表头/数值存在版本混杂，不能直接拼成统一benchmark排名。

## 4. 发现二：“GPU不支持动态任务”已经不是合格动机

P009 Event Tensor把tile级依赖、动态shape和数据相关分支作为编译对象，并提供静态/动态调度；P010 Nautilus继续把代数重写和tiling共同优化。P031 MSCCL++已经把通信原语暴露为细粒度可组合操作。

Event Tensor必须按实验组阅读：
- 通信计算融合不是同一张卡的普通GEMM；
- B200 MoE层对不同token数使用动态调度；
- 小batch完整服务又可使用静态调度以去掉runtime成本，输入长度为合成配置；
- warmup时间与离线compile时间分开，不能把后者当免费。

因此可问的不是“能否做persistent kernel”，而是：**当ready集合、任务粒度和资源需求实际变化时，成熟执行模型仍在哪类位置付出有限队列、同步、寄存器占用或重专门化成本？** 这既允许先观察，也允许先移植一个小型已有能力作诊断。没有必要重建整个编译器。

## 5. 发现三：新的状态管理机会常被算法改写先解决

P013 ReplaySSM不每步写完整状态，而是保存输入、直接算输出、按需flush；同时处理推测验证及continuous batching。P014 TreeWY去掉逐草稿节点快照，但更宽树“能放下”不必然“更快”。P015 SketchSSM保留完整状态写、近似读，必须按质量合同比较，不能当exact替代。

P016更重要：部分TTT可化成线性attention，但其充分并行化实验包括仅更新最后一层、移除weight normalization等消融。Appendix I明确动态特征函数和weight normalization破坏所展示的可归约条件。**代数同一性、近似/消融后质量接近、实机更快三件事要分开。**

P017 TTT-NTP既有真实任务评估，也依赖持续预训练和特定prompt内更新语义。不能拿任意旧Qwen权重施加同名更新就称复现。它与我们的RTC VJP不同：后者冻结模型权重，对action latent求导；前者更新推理期参数/状态。

尚可保留的架构问题是：在真实有收益且不能被已有代数路径替代的算法中，有限state的update→read/commit究竟付出什么成本。仅看到autograd或状态矩阵就立项不够。

## 6. 发现四：动态扩散的性能实验，有时没有测自然动态性

旧R53设计已覆盖Fast-dLLM、dInfer、dLLM-Serve、BlockServe等。此轮不是再宣称连续batch或pack是空白。

新P018 Flash-dLLM摘要已提出IO-aware缓存/融合与draft-verify；原始全文本轮未取回，不能补造实现开销分解。P019 HERALD已把CPU选择与GPU去噪重叠，并复用SGLang、FlashInfer与CUDA Graph。

但HERALD的质量实验用confidence驱动步数，性能实验固定每block为20步；模型质量与性能范围也不完全一致。正文还同时出现block32、512token与“8blocks”的算术不一致，本轮按字段保留，**不替作者悄悄改成16或猜另一block设置**。

这留下的是一个**覆盖缺口**：自然可变步数、request结束、cache refresh决定在运行时变化时，既有软件仍有多少真正额外成本？覆盖缺口不是已证明的新硬件瓶颈。优先核R53是否已有未读执行receipt，再决定是否使用它；不能把旧设计换编号当新发现。

## 7. 发现五：Agent缓存的关键不仅是存储，而是“还能不能合法复用”

P020 ForkKV共享base＋adapter residual，ResidualAttention已融合重建和延迟投影；泛泛“压缩后在attention里重建”不是空白。其正文明确第一层之后跨LoRA共享base在数学上有损，因为hidden inputs随adapter分歧。名字中的CoW不代表逐bit同值。

P021 TokenDance利用通信模式和master/mirror缓存，并在传输路径融合稀疏重建；它不等于已经证明无需dense materialization的所有attention消费接口。P022 IntentKV采用语义/压缩策略；P023 KVShareArena把非prefix/cross-checkpoint复用的质量风险作为研究对象。

P024 TokenCake、P037 BatchGen、P038 Libra分别处理工具等待关键路径、batch coroutine、token级微请求重组。性能目标可能是完整任务完成、goodput、SLO或批makespan，而非每kernel的微秒数。

我们未系统测试这类问题，但当前直接系统近邻强。下一步应当从真实workflow证据选择某个明确consumer边界，不应直接搭一个大型Agent服务平台。

## 8. 发现六：异构与共享资源问题没有被我们的单kernel负结果排除

P027 Hummingbird用kernel拆分构造抢占点，但对跨block同步/persistent kernel关闭拆分。P028 Valve协调channel抢占与细粒度KV回收；涉及driver/ioctl与线上请求生命周期，不是普通可移植CUDA开关。

P035 Nixie针对消费级GPU多应用近满显存，引入透明时分复用并控制pinned CPU内存和双向传输；P036 SERENO在手机上用推测执行形成可让出带宽的时机。它们说明，计算调度和数据驻留需要共同处理，单纯“分配更大cache”不是唯一变量。

这些都不等于我们的单模型resident UVM/TLB结果。另一方面，不能为了研究共享而随意修改共享109驱动，或拿桌面独占计时宣称手机前台QoS改善。此轮列为条件性后备，不立即开新工程。

## 9. 发现七：压缩、稀疏、可靠性、能耗必须保持各自评估层级

**IBP P030**针对host→GPU传输，静态数据预处理、CPU压缩、GPU fetch/decompress分开。FP16与BF16的收益不同；代码C001提供预处理、索引子集和output buffer接口，但不表示在线动态KV免费生成压缩格式。正文实验是A100/PCIe4上的多个系统，DLRM embedding lookup不是完整推荐模型。扩展arXiv稿摘要约24% LLM提升，会议/README约25%；本轮不混两个版本。

**FRUGAL P029**接受时间代价换内存；摘要中的大幅省显存伴随geomean约28.31% slowdown，不能称免费容量扩展。**Uni-STC P032**是新稀疏硬件结构，摘要中的相对其它STC收益不等于商品GPU实测。**P033 moderately sparse**还改变pruning/表示合同，不只是任意稀疏矩阵无损变快。

**可靠性P039**从门级故障分布出发，提醒任意随机单bit flip不一定代表真实GPU故障；没有真实故障模型就开展大量训练inject，可能再次变成缺少输入authority的工程。**功率P040**是trace-calibrated系统模型，不是直接验证某个GPU DVFS策略。**移动NPU-PIM P041**提出新增硬件与算法控制，不能把其平台估算替代RTX4080实测。

这些外围方向已纳入原始来源筛选，但本轮没有取得所有全文，不宣称把能源/可靠性/异构体系结构穷尽。

## 10. 我们做过什么、没有做过什么

边界账本与状态源分开维护：

- **确有局部软件反证**：CCE zero-init；P1数值归约和P2 selector交接按旧Round15记录继承，后两项本轮未逐一重读全部raw。
- **有模型响应但现实动机未支持**：R101；不继续该scope机制。
- **有负载现象但目标残差未知**：VLA；R17设备内分解也仍未知。
- **输入未资格化**：R102。
- **只有部分轴验证**：MoE E3只验证natural/uniform代理；RAW/AWQ只验证特定实现×shape；不能代替FP4训练完整链。
- **已读文献、尚无本轮可确认执行receipt**：R53动态扩散；不是已证software sufficient。
- **没有匹配边界实验**：FP4 scale/transpose交付、动态megakernel调度、不可约TTT状态、Agent共享重建、真实多GPU细粒度通信、多应用消费级GPU驻留、真实故障分布、功率动态。

用这些区别选择下一轮，而不是统计“又关闭了多少方向”。

## 11. 下一轮准备顺序

### A. 优先：低比特表示就绪链

选择一条真实producer→quant/scale/layout→consumer区域，保留实际精度策略与完整operator。强基线包括当前已融合转换、scale布局优化、可用warp specialization。先检查已有优化后producer何时交付payload、scale何时有效、consumer为何等待；不能只清点convert指令。

允许一个有界软件/机制诊断原型，不要求先拿出论文级归因；最终要比较完整同合同输出和时间。若简单fusion解决，保留软件结果；若目标代价藏在mandatory算术，停止硬件解释。

4080可做部分转换/布局和语义实验；**不能假装具备SM100/103原生FP4/TMEM或用其计时代替B200/B300**。真正相关微路径必须先确定可用硬件或明确校准模型；不立即租卡/改模拟器。

### B. 并行准备：动态工作集在强执行模型之后的残差

优先检查R53旧设计/receipt和一个成熟动态执行基线。不同时完整移植多套编译器。区分静态shape专门化、相同算法动态ready集合、减少算法工作三条轴。允许一个小型动态调度原型作为诊断；不拿主机Python循环当唯一baseline，也不把固定步数benchmark作为所有动态请求的反例。

### C. 条件保留：不可直接归约的fast-weight更新

先确认公开checkpoint/input、实际更新目标及算法收益；已有线性attention/scan、ReplaySSM/TreeWY必须进入比较。没有真实运行入口就保持源码资格，不用随机fast-weight矩阵冒充应用。

三张准备卡均不启动执行。预算可合并多个有真实依赖的阶段，科学解释与正确性仍在每一层闭合；无新信息时不要扩成无界参数扫描。

## 12. 当前执行与写作状态

Lane E/174-new、Lane F/109、Lane G/109全部保持STOP。原branch/raw/model资产不改；不新建execution branch。此轮只更新ChatGPT文献分支和候选准备卡。

今后论文阅读记录以“作者提供的能力—实际实验合同—硬件与输入—我们测过的边界—下一个可区分解释的干预”为主。全文暂未取得的工作可以是线索，不能凭摘要替它补齐误差、输入和基线。研究目标仍是有新意且现实可行的体系结构机制；文献复现是有限支撑，而不是把创新无限推迟。

## 13. 本轮内部authority索引

- 文献起点：`5ff0287ce45c3909d53ac44975f6fa488664b085`。
- Round16协调收口：`31d585dc44f90eb70f83603c8b87a2d06efff01a`；本轮直接回读。
- CCE source/experiment authority：`ec1ccad7bbcead8853cd97840a2007d96f325aa3`；具体结果从Round16收口与当前会话继承，未声称本轮重新跑raw。
- R17R1：`29ecc6e5e37005046b1a563c830bed9ae58af656`；本轮直接回读FINAL_DECISION，解释限定见§1。
- R17 Lane G最近邻：`f72aca7938a1b2e8bb2f62953e308444babd8489`；该结果由本会话继承，本轮不冒充重新复现全部15篇。
- R53：文献起点中的Round06设计直接回读；没有取得对应完成receipt，状态只写设计层。
- 旧P1/P2/R54/R81/R82与translation结果：由Round15记录继承，核查深度在边界账本明确。

## 14. 原始来源与未核实线索的处理

41个原始链接见SOURCE_REGISTER；正文引用P编号，与EXPERIMENT_EVIDENCE一一关联。作者代码文档：

C001 `AKKamath/InvariantBitPacking`，`README.md`，默认分支devel，blob `1f439e98eb4449b10f2f64c9e7ce04173544b17d`。
C002 `hao-ai-lab/flash-attention-fp4`，`flash_attn/cute/README.md`，分支fp4，blob `d7c4c5a7ebb6a76544b90f0cc3410fecc480507e`，本轮核前110行；不当统一性能权威表。
C003 同仓库 `flash_attn/cute/debug/b300_fp4_pv_analysis.md`，blob `46f29df0d215664c49747e86a374fdda0cf2b589`，本轮核前120行；作者微基准/插桩诊断，不冒充我们实测。

FIBER本轮原始arXiv未重新取回，仅保留旧Round04/15知识为待复核近邻；不引用聚合站补出新实现结论。Weave/Entwine/mKernel及部分视频检索线索只取得二手入口或原始页取回失败，未纳入41项核心证据。Nixie正文PDF取回超时，仅按官方摘要登记；不说作者未公开全文。
