# Round A3｜P01/P13历史证据闭环与候选准入核查

**执行者：ChatGPT／AI-ARCH Discovery（只读GitHub源审＋原始论文核对；不是Codex）**  
**日期：2026-10-13**  
**研究层次：AI-ARCH Discovery / P01＋P13，科学问题准入，不是GPU或模拟器实验。**

> **核心结论**：C16已有可审查的**局部任务分解策略反转**，但它并不能隔离“可供执行任务数”这一硬件因果轴；当前FFN仅证明原双流方案负面、tiling交接需新依赖合同，不能直接证明剩余硬件机会。两个问题都**尚未达到新109原生实验或新硬件机制的正式准入条件**。本轮不下发Goal，不运行109 GPU/174模拟器，不恢复Stage A/AWMA，也不动原始raw。

## 0. 审查对象、边界与资料

这是已获同意的Round A3，由本ChatGPT窗口直接执行。不以协调分支信息替代历史独立review pack；证据层次区分：`NATIVE_MEASURED/RECOMPUTED`（原C16执行与174独立重算）、`SOURCE_AUDITED`（源代码/方法事实）、`PAPER_AUTHOR`（作者限定平台结果）、`HYPOTHESIS`（本轮新的架构解释）。

**直接核查的固定原始权威**：

1. [C16 grouped residual正式consumer @ a3a36e64](https://github.com/swayhrl/accel-sim-framework/tree/a3a36e64ae4a3a316df2bf4dfc9cac95caf8e164/docs/vm_tlb/review_packs/C16_GROUPED_RESIDUAL_PARALLELISM_CONSUMER_174NEW_V1)：`M_SWEEP_COMPARISON.tsv`、`RAW_RECOMPUTE.tsv`、`PARALLELISM_INTERPRETATION.md`、`FINAL_DECISION.json`、`OPEN_ISSUES.md`、`AUTHORITY_AUDIT.json`。
2. [C16 Split-K容量现象正式consumer @ 6d226cd9](https://github.com/swayhrl/accel-sim-framework/tree/6d226cd99946d3bd7b41c5ee005285183efbb915/docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_THRESHOLD_CONSUMER_174NEW_V1)：`CAPACITY_THRESHOLD_COMPARISON.tsv`及`MECHANISM_INTERPRETATION.md`。
3. [C16 FFN headroom正式consumer @ 30b3016a](https://github.com/swayhrl/accel-sim-framework/tree/30b3016a7ad5b5ef86a3494c784e072938dee6c5/docs/vm_tlb/review_packs/C16_FFN_TIMELINE_HEADROOM_QUALIFICATION_174NEW_V2)：`FFN_F2A_GATE_UP_CONCURRENCY_CEILING.json`、`FFN_F2B_TILE_PIPELINE_ANALYSIS.json`、`FFN_STRONG_SOFTWARE_BASELINE_AUDIT.md`及`FINAL_DECISION.json`。
4. [C16 two-stream V2原生报告 @ e8a2553f](https://github.com/swayhrl/accel-sim-framework/tree/e8a2553f5c7a9861ddd2a31ae50e79e79d78d3a7/docs/vm_tlb/review_packs/C16_FFN_GATE_UP_CONCURRENCY_NATIVE_DIAGNOSTIC_109_V2)：`IMPLEMENTATION_AND_RESULT_AUDIT.md`及计时审查；[Stage A独立终态 @ ccd6928b](https://github.com/swayhrl/accel-sim-framework/blob/ccd6928bfb420d1e4c554ec0e377bb8fbe377501/docs/vm_tlb/review_packs/C16_STAGEA_TERMINAL_INDEPENDENT_CONSUMER_174NEW_V1/STAGEA_TERMINAL_SYNTHESIS.md)。
5. [C16最终Reset决策 @ 635b2f22](https://github.com/swayhrl/accel-sim-framework/blob/635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f/docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_RESET_174NEW_V1/CANDIDATE_DECISION.md)，及[既有观察归档](https://github.com/swayhrl/accel-sim-framework/blob/635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f/docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_RESET_174NEW_V1/EXISTING_OBSERVATION_ARCHIVE.tsv)。
6. 原始论文部分重点反核[Tawa 2510.14719v2 §V-E](https://arxiv.org/html/2510.14719v2)、[Twill 2512.18134v1 §4/6.3](https://arxiv.org/html/2512.18134v1)；沿用[Round A2](AI_ARCH_P01_P13_ROUND_A2_EXECUTION_RESOURCE_BOUNDARIES_2026-10-13_V1.md)精读过的MPK、VTC、Kitsune（其模拟/原生范围不变）。新增直接只读检查MPK的[固定作者artifact分支 @ 8b981a449597](https://github.com/mirage-project/mirage/tree/8b981a44959727b9a31873cd78cf8cd80ab97e65)，未编译或运行它。

**重要范围**：本轮是Git blob和固定审查报告的**只读核对**，不是现场SSH读取node164 raw、重新计时或重新执行NCU；相关数据的正式独立重算等级沿用原review的接收范围。

## 1. Q-A2-01｜任务供给与服务饱和：最小证据账本

**问题**：固定语义和强软件之后，增加ready任务数是否使瓶颈从任务供给转向真实计算、L2或DRAM服务？当前C16能证明到哪一层？

### 1.1 数据：GROUPED后的M形状扫描

来源：`a3a36e64…/M_SWEEP_COMPARISON.tsv`与`RAW_RECOMPUTE.tsv`，RTX4080（76SM），W4 Split-K对应固定算子族，M=1/16/32/64。每点50个正式样本，原始consumer确认数值PASS。时间为**各点native operator计时中位数**，不是整个模型的自然服务时间。以下微秒由文件毫秒换算：

| M | Split1 CTA | Split8 CTA | Split1 median (µs) | Split8 median (µs) | Split8相对Split1速度比 (T_1/T_8) | 对照要点 |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 96 | 768 | 74.752 | 32.976 | 2.267× | Split8显著快；独立CTA数与执行分解一同改变 |
| 16 | 96 | 768 | 76.800 | 40.976 | 1.874× | 时间优势缩小；同一16行tile覆盖M1/M16 |
| 32 | 192 | 1536 | 86.016 | 67.584 | 1.273× | Split1任务数增加，Split8额外工作仍存在 |
| 64 | 384 | 3072 | 113.904 | 119.808 | 0.951× | **Split1反超**约4.93%；原bootstrap区间4.50%–5.13% |

附带指标：该审查表的独立`split1_active_warps_pct_elapsed`约5.0%、5.0%、9.5%、17.8%，Split8约24.2%、24.3%、30.2%、33.6%。**active-warps elapsed、发射波数/SM和launch CTA不是同一概念**，不能据此直接换算成可节省wall。该样本的NCU TEX L2 read-side hit fraction均报1.0，不应套到其它真实上下文或解释为完全没有DRAM访问：表中仍记录GEMM DRAM字节。

**真正支持的事实**：在这个已经采用分组映射的定点算子族内，Split8对小M更快、到M64反转；任务供给、tile利用、split后的归约额外成本共同形成规模相关取舍。

**不能支持的升级**：
- M从1增加到64时，实际有用计算量和tile数本身同时变化；Split1↔Split8还改变CTA数量、局部K分解、reduction及存储流量，**不是“只增加SM/只增加任务就绪数”**的隔离干预。
- 拆分时高warp activity不是硬件应该增加SM的理由；不能认定Split1 M1受阻的唯一原因是low occupancy。
- **Stage A compiled Qwen2.5-3B B1合法Mode A/B只有一个同点差异**（354.598ms vs 361.457ms，Graph带来1.897%省时），B4身份失败，因此不能拿MP02/03补齐“强编译完整Decode的B1→B4扩展曲线”。

### 1.2 反例：K维容量和强软件映射

`6d226cd9…`原生/NCU对照中，K2560→3072（×1.2）时，Split1的GEMM DRAM约×4.04、时间约×1.60；Split8总DRAM仅约×1.03。**工作集容量/复用是因素，但64MiB不是严格阈值，DRAM字节不能全部归权重，更不能唯一归因L2。**

`e7855278…` grouped CTA强软件baseline正式审查表明GROUP_M16使Split1的L2 hit回到约95.95%，恢复了主要空间局部性。按后来的`a3a36e64…`结果，剩余现象是**parallel decomposition和reduction之间的普通算法映射取舍**，旧Cache-aware Split-K机制已关闭。

### 1.3 Q-A2-01科学准入判定

| 资格维度 | 目前可核状态 |
|---|---|
| 受控合法算子与计时 | **有**：同算子族M/split扫描，50样本正式重算 |
| 规模变化导致运行策略反转 | **有**：Split8→Split1优势递减并在M64反转 |
| 单变量“ready任务数变化” | **没有**：M、CTA数量、运算量、部分tile与reduction同时变化 |
| 强软件后仍有新硬件残余 | **没有资格化证据**：GROUP_M16解决主要cache局部性，split数量的选择是已有映射能力 |
| 完整自然模型中该族占时 | **尚未有对应时间分母**：固定算子代理非完整编译模型 |
| 独立家族/平台泛化 | **未做**：不能把旧探索样本改称新holdout |

**结论：`RETAIN_AS_LOCAL_SCALING_CASE / NO_NEW_NATIVE_ADMISSION`**。将该现象保留为P01/P13关于任务粒度与资源调度的可信**局部教材/方法样本**，但不要重开旧Split-K机制或由此申请新的109 GPU扫描。今后确有新的自然family+同后端隔离对照时，再针对新问题提小探针。

## 2. Q-A2-02｜资源生命周期与数据就绪：最小证据账本

**问题**：在producer/consumer双方各使用成熟实现后，是否存在可实测、非软件已经处理的buffer/register/ready依赖等待？

### 2.1 已有正确性和时间负例：FFN gate/up

`30b3016a7…`已重建112个D0–D3 FFN完整窗口，原同流gate→activation→up→multiply→down，整体合法FFN wall union占选定whole decode 28.4797%（不能将独立NVTX累计时间当wall）。双流gate/up理想**无资源争用**且保持非目标gap的时间减少是7.732849ms，whole decode时间减少比例7.893%，对应理想1.0857×；这**只是反事实，并非可实现机制收益**。

`e8a2553f…` V2在修复V1 Prefill污染后满足正确性，24×B0与24×B1、12完整ABBA；实际只在112窗口中有10次gate/up重叠（544,929ns）。选定区间由74.2159ms变为81.4339ms，**慢约9.73%（B1/B0时间比1.0973）**；gate/up单核duration分别膨胀约2.48%/19.38%，对共享资源争用提供支持，但不足以唯一定量解释全部减速。不能取原理想并发7.893%来断言硬件应提供该幅收益。

**最强软件邻近性限制**：vLLM的merged gate_up确实是成熟能力；此前尝试的特定AWQ checkpoint同语义对照336处中14处超冻结容差，不能在同一数值合同下合法排名该merged实现与旧AutoAWQ实现的速度。此数值失败属于**未资格化的A/B**，不是merged本身性能为负。

### 2.2 F2B tile-ready：仍缺真正可执行的数据依赖

来自`30b3016a7…/FFN_F2B_TILE_PIPELINE_ANALYSIS.json`：
- W4 gate/up输出后乘法是**单个whole-tensor向量化kernel**；乘法产生的目标形状`[1,1,18944]`，约37,888 Byte。
- down-proj `K=18944,M=1,N=3584`，当前执行包含一个W4 GEMM及一个reduce kernel。存在GEMM内部partial accumulation，**不等于**跨operator的分块可消费状态。
- 当前down在乘法kernel结束后才launch；**没有**当前producer的tile-ready信号。
- 重新划分为tile pipeline要求确切consumer chunk映射、chunk可见性、合法部分和/归约顺序、同步/缓冲及新的K分块kernel。不具备这些时，`max(T_producer,T_consumer)`不是合法的免费oracle。

**结论**：`TILE_PIPELINE_ORACLE_NOT_WELL_DEFINED`仍应维持；不因Tawa/Twill/Kitsune已有流水概念就假定此FFN具备新的硬件headroom。

### 2.3 外部软件与编译器近邻，进一步压缩宽泛新意

| 近邻 | 本轮重新核对的原文/固定源码 | 限制我们的创新叙述 |
|---|---|---|
| **MPK**（OSDI26） | [作者固定artifact @ 8b981a4](https://github.com/mirage-project/mirage/tree/8b981a44959727b9a31873cd78cf8cd80ab97e65)，`include/mirage/persistent_kernel/persistent_kernel.cuh`有worker/scheduler队列、任务事件与页队列；`runtime_header.h`区分架构的动态SMEM预算。其Python编译入口留有过去`-rdc=true`导致Blackwell寄存器166→255的工具链历史注释，并提及后续组合环境已避开。**注释是源码作者记录，不是本窗口新测性能**。 | 常驻SM task、device端事件/队列、SMEM按需分配均非空白；寄存器占用要与具体编译、任务和headroom绑定 |
| **Tawa**（2510.14719v2 §V-E） | aref的`put/get/consumed`及共享内存槽归还；H100 GEMM sweep中D≥P，P1→P2通常有利，P3反因accumulator/register/occupancy压力下降；该论文是H100局部kernel并非完整自然FFN。 | “增加异步缓冲”“自动producer/consumer同步”已是成熟软件；更深流水不是通用收益 |
| **Twill**（2512.18134v1 §4、§6.3） | 求解器含register liveness、warp assignment、cross-warp spill/sync约束；H100单pass FA3 backward受register限制；B200一个理论寄存器可行的两warp group方案由ptxas产生实际spill，降低预算后变为三warp方案恢复性能。作者部分schedule手工lower到CUDA；最优性仅在指定机器/循环成本模型内。 | 不能声称“自动联立warp分工与流水是空白”；抽象可行与真实分配不一致可能值得研究，但已有软件修复反例 |
| **VTC**（OSDI26） | A100/H100 vLLM单Decoder Layer强路径；H100默认选择保持4.230ms，而强制虚拟tensor路径变为4.600ms。改变kernel选择影响了净收益。 | “删除物理中间张量”不足以证明净关键时间可省，更不能只对慢kernel提出硬件融合 |
| **Kitsune**（2025） | A100 queue原生microbenchmark；主体应用加速与SM/L2带宽变化是修改后的NVArchSim **模拟器结果**。 | SM级数据流/队列已有近邻，不能直接继承为4080 native结论 |

**真正可能剩余但未被证明的约束**：当运行时任务类型变化、寄存器live ranges无法按任务释放时的可驻留工作限制；成熟后端最佳tile之间的数据交接成本；编译器静态schedule和动态ready状态失配。此表只是研究缺口登记，不证明这些限制在目标自然工作负载中占用可测wall。

### 2.4 Q-A2-02科学准入判定

| 资格维度 | 当前状态 |
|---|---|
| 强软件能力与最邻近工作 | **已有非常强近邻**：MPK、Tawa、Twill、VTC、Kitsune |
| 当前合法producer/consumer pair | FFN双流正确性通过，但性能负；跨tile依赖**没有合法定义** |
| 可消除的额外关键路径时间 | 仅有冲突-free gate/up理想量和实际负响应；tile-ready本身无法形成合法上限 |
| 不改变数值/布局/算法的对应实现 | 特定merged AWQ严格数值A/B不合格；tile-ready方案尚未确定 |
| 跨模型或训练/非LLM真实natural pair | **未具备新的、合格的具体pair**；Kitsune的非LLM应用主要在模拟器 |

**结论：`PARKED_MISSING_VALID_OPERATOR_PAIR / NO_NEW_NATIVE_ADMISSION`**。没有科学依据现在就实现buffer、queue或register硬件机制；保留作后续真实负载发现的一个约束维度，不重开既有FFN工程。

## 3. 训练与非LLM能否作为独立“第二family”？

- **MegaScale-MoE 352B训练 / 240–1440 H800**：是实际大规模训练扩展证据，但同时变化分布式并行方式、pipeline气泡及通信；不能移植为单RTX4080同一SM/task响应。训练天数投影也不是完整实际训练时间。
- **Sobek RTX5090非LLM等变TPConv**：是有真实kernel容量/导数阶对照的强数据流近邻；图生成/索引准备、长时真实几何轨迹不在其kernel局部时间分母。相比天真边物化，流式软件已解决大量容量问题，未证明硬件剩余。
- **AWMA Round21的图/几何准备**：已审源码证明存在预处理、per-graph缓存和合法reuse接口；没有现有完全同语义的自然真实几何/强后台端到端时间结论。AWMA仍独立管理，不因AI-ARCH研究该主题而恢复R21 Goal。

因此本轮训练与非LLM是**边界反例/应用类别覆盖**，并没有通过它们找到可以跨family复用的定量资源转折点。下一阶段若希望新探针，必须先有独立自然应用及软件身份，而不是从模型资产库存倒推。

## 4. Round A3最终准入裁决

| 问题 | 已有科学证据层 | 阻断新实验/机制晋升的关键缺口 | 本轮决策 |
|---|---|---|---|
| **Q-A2-01：任务供给到服务饱和转折** | RTX4080局部W4 M/split真实算子、独立重算；作者MPK/Bullet支持任务调度的重要性 | M变化包含计算量/tile/拆分/reduction，多变量耦合；GROUP已有强软件解决主要L2问题；没有新的自然强执行family时间剩余 | **保留局部有条件规律，NO_NEW_NATIVE_ADMISSION** |
| **Q-A2-02：异构task资源与就绪生命周期** | C16 FFN负结果；Tawa/Twill原文真实H100/B200局部限制；MPK源码有调度与SMEM管理 | 合法分块producer→consumer DAG缺失；无受数值合同保护且软件仍无法解决的实际时间残余 | **停车保存问题，NO_NEW_NATIVE_ADMISSION** |

- 本轮**0个已晋升硬件候选、0个获准109探针、0个新模拟器任务**。这不是宣称P01/P13不存在，而是拒绝重复已被强软件解释的旧机制或让诊断范围越权。
- **没有生成未来109探针的具体冻结Goal**：当前缺的不是某个指定参数或执行脚本，而是可代表自然family、又能保持同语义/强后端/唯一实验变量的合法目标。如果继续做“新M/新Split8点”只是在封闭问题上寻找新的正数。
- 若后续发现一个新自然目标，将按`DISCOVERY_PROBE`提出单独问题、固定输入/强基线、最轻未插桩时间和任务供给指标、竞争解释、有限预算、独立样本以及STOP。没有此前的名单不构成授权。

## 5. 下一轮：Round A4｜跨负载自然场景选样与资源问题辨识（执行者：ChatGPT／AI-ARCH Discovery）

**为什么**：再在原Split-K或旧FFN上展开成本很高且不能形成新claim；应寻找一个**具有自然阶段/工作量/依赖变化、且强软件后确有可观察时间权重**的不同AI场景，以便真正筛查P01/P13是否值得开新原生探针。

**怎么做（本ChatGPT窗口只读执行，不开Codex Goal）：**

1. 以已审原始论文+公开实现能力，形成不超过**3个自然负载family**的候选清单，至少覆盖**一个训练**和**一个非LLM**；例如真实训练中的backward/通信阶段、天然拓扑变化的几何/等变应用，Dense/MoE服务只作必要对照。具体模型从问题所需数据与合法软件选择，不以已下载资产为先决条件。
2. 对每个family做四项证据审计：**必要完整工作区间与真实输入身份**；**成熟软件已消除什么**；**哪个单变量/天然变化可能改变ready工作量或资源服务限制**；**局部指标是否对应真实时间/容量分母**。从AWMA Round09/21去重，禁止把源码能力当作native测量。
3. 只保留**最多2个**有可证伪现象的候选，每个给最低成本只读/CPU验证办法和可停止的反例。如果缺自然输入或最强基线，优先不立项、不建新环境。
4. 仅当其中至少一个已具备冻结模型/输入、强软件、单变量、受限region wall、资源锁与样本预算，才另外提不超过**1份未来109 DISCOVERY_PROBE草案**供审阅；**Round A4本身不启动109 GPU、174模拟器、旧Stage A、AWMA R27R3、新机制或额外raw下载。**

**Round A4交付**：跨训练/非LLM与推理的候选比较表、最近邻能力/反例及最多2张真正可辨识问题卡；如没有符合条件的自然family，明确给出“无新GPU问题”的负面结论。

## 6. 项目权限和authority不变

AI-ARCH Discovery仅维护协调分支知识索引；C16 Stage A依然`TERMINAL_PARTIAL`、Reset已收口；AWMA R27R3已独立审阅`B0_REFERENCE_NOT_REPEATABLE`并STOP，由原窗口管理；node109 GPU和174模拟器不因该科研总结出现新的执行权。本次不读取164大raw、运行程序、调整模型或变更已有accepted科学commit。
