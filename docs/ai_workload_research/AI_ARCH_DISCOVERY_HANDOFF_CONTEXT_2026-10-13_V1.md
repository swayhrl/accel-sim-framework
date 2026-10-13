# AI-ARCH Discovery｜新ChatGPT窗口完整交接上下文（2026-10-13 V1）

> **用途**：交给新的AI-ARCH ChatGPT窗口，继续统一AI负载体系结构研究的问题发现、文献调研、证据管理及未来实验设计。本文件是**科研交接和只读恢复说明**，**不是任何Codex Goal，也不授权GPU、模型下载、模拟器、holdout或新机制实验**。
>
> **状态日期**：2026-10-13（截至本次可核对的GitHub提交；不声称实时SSH监控）。  
> **总研究计划**：**AI-ARCH — AI Workload Architecture Research（AI负载体系结构研究）**。  
> **当前窗口工作线**：**AI-ARCH Discovery**（兼顾AI-ARCH总体研究规划；不再把新研究轮次叫C16）。  
> **统一仓库**：[`swayhrl/accel-sim-framework`](https://github.com/swayhrl/accel-sim-framework)。  
> **科研协调分支**：`hrl/ai-workload-research-coordination`。  
> **历史项目**：C16（已冻结的负载/机制探索证据）、AWMA（独立ChatGPT窗口继续管理已有课题）；DTC-L1/ISCAS是另一个独立项目，不归本交接自动接管。

---

## 0. 新窗口先读：此刻最重要的结论

1. **这是一条新命名的总主线，不是复活C16旧Stage A**。目标是建立AI负载的体系结构认识，涵盖训练和推理、LLM/MoE与非LLM应用、单卡/多卡及CPU–GPU协同；不把研究预设为Cache或TLB。
2. **本ChatGPT窗口承担AI-ARCH总体协调及Discovery**：持续阅读原始论文的具体实验组，综合已有C16/AWMA证据，提出和筛查新的可证伪架构问题；AWMA使用原独立窗口继续其机制、软件和训练实验的审查与论文工作。
3. **共同知识在GitHub协调分支**。不再靠用户把研究底稿在两个窗口手动转发；但协调分支**不是**两个项目的统一执行代码主干，不通过Git merge实验分支统一科学authority。
4. **当前没有自动准入的新AI-ARCH GPU/模拟器实验**。C16最后十个问题筛查结果为0个正式主候选、0备选，两个future-only；AWMA R27R3现已独立审查并STOP。未来新发现性GPU探针也必须就具体问题单独授权，不能因GPU空闲自行开始。
5. **AI-ARCH Discovery下一步已经确定方向，但尚未开始新实验**：第一轮重点研究“AI负载中GPU资源瓶颈随工作量、阶段与部署条件如何变化”，即问题图谱P01/P13；从NanoFlow、MPK、相关推理扩展规律论文及非LLM/训练实例的原文实验组出发，边研究文献，边把已有实测证据映射到统一资源约束框架。
6. **不要误读历史状态**：C16 Stage A观测链终止，不等于没有AI架构现象；AWMA模拟器服务抑制不等于真实芯片整模型加速；AWMA R27R3的B0自身不满足冻结BF16数值重复性判据，不等于C1/S2已经被证伪。

### 新窗口第一轮优先阅读

按顺序读取协调分支（使用**最新HEAD**，不要固定到最初的`d0a8a833…`）：

- `docs/ai_workload_research/README.md`
- `docs/ai_workload_research/CURRENT_STATE.md`（导航快照，注意与较新同步记录的先后）
- `docs/ai_workload_research/AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md`
- `docs/ai_workload_research/AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md`
- `docs/ai_workload_research/COORDINATION_PROTOCOL.md`
- `docs/ai_workload_research/R27R3_INDEPENDENT_REVIEW_SYNC_2026-10-13.md`
- **本文** `docs/ai_workload_research/AI_ARCH_DISCOVERY_HANDOFF_CONTEXT_2026-10-13_V1.md`

协调分支在编写本交接文件之前，最近读回HEAD为`77a1c5267563adde12a883b694d8a280d87858be`。**这只是写作时的父版本，不是本交接文件发布后的最终HEAD；请以新窗口实际fetch的ref为准。**

---

## 1. 项目命名与长期目标

### 1.1 名称规则

| 名称 | 定义 | 后续使用规则 |
|---|---|---|
| **AI-ARCH** | AI Workload Architecture Research，统一研究计划 | 研究问题图谱、论文调研、研究优先级、共享证据与资源协调 |
| **AI-ARCH Discovery** | 当前ChatGPT窗口管理的主动问题发现线，现阶段兼总协调 | 首先建立跨负载认识，再设计低成本原生诊断；以后新课题成熟可拆窗口 |
| **AWMA** | 保持原名、原独立窗口的既有具体研究线 | 按AWMA自己的已批准Goal/commit/实验合同执行、独立审查；向协调分支同步已审查结果 |
| **C16** | 历史项目及其commit、文件、实验标签 | 只作历史证据与兼容索引；**不再作为新的研究线名称**，不重开Stage A旧任务 |
| **DTC-L1 / ISCAS** | 相邻独立论文项目 | 不因AI-ARCH成立而改变其工作安排、科学边界或资源授权 |

### 1.2 科学主目标

系统理解**模型结构 × 输入/任务 × 运行阶段 × 软件部署 × GPU资源配置**怎样共同决定AI程序的性能、容量、能耗及扩展性限制，识别成熟软件优化之后仍有意义的体系结构约束。不限于L1/L2/TLB，可涵盖：

- 计算单元的有用工作占比、指令/CTA/warp级并行度和工作量形状；
- GPU调度、执行顺序、同步、producer→consumer数据就绪、跨算子中间态；
- 片上存储、L2/DRAM、TLB/PTW、工作集寿命、KV/专家权重与跨时间复用；
- 量化/稀疏/MoE、多模态/图/科学ML/推荐/扩散/3DGS等AI结构；
- 前向/反向、梯度累积、优化器状态、数值顺序、训练质量与容量约束；
- 多GPU通信、CPU–GPU分层、服务到达/SLO和资源扩展规律。

希望形成：**可信的跨负载观察规律 → 可证伪的瓶颈解释 → 最强合法软件基线与可改善上限 → 值得时的硬件机制与论文成果**。

不要求每轮都产出新机制；可信的否定结果、阶段/规模规律或证实软件已吸收某机会也有价值。也不以“下载了什么模型”倒推必须做哪些实验。

### 1.3 原则上的两条平行研究路线

**路线A：文献驱动**。ChatGPT优先读顶会及原始论文具体实验组，核实模型/输入/平台/软件/改变项/指标、作者实测和模拟范围、已解决的能力与留白；提出可能的新科学问题，不直接复制论文机制。

**路线B：实验驱动**。Codex只在已经设计清楚的问题上按阶段执行：轻量原生观察、对照定位、必要时模拟/硬件验证；实验也可反过来启发下一轮文献检索。

两线互相反馈但不用彼此等待。当前没有“要保持109忙碌”的指标；没有可辨别的科学问题时不发GPU Goal。

---

## 2. 项目组织与分支边界

~~~text
AI-ARCH（科学目标与资源协调）
  │
  ├── 本窗口：AI-ARCH Discovery + 当前阶段总协调
  │     ├── 文献：原文实验组、近邻与已解决能力
  │     ├── 问题：跨负载瓶颈图谱、候选与反证
  │     ├── 实验：发现性诊断设计/结果审查（需独立授权）
  │     └── GitHub：hrl/ai-workload-research-coordination
  │
  ├── AWMA：另一个ChatGPT主窗口
  │     ├── Pre-L1地址翻译请求合并（已有论文资格化证据）
  │     ├── R23G在线稀疏输出分派（有范围的软件正结果）
  │     ├── R24–R27R3训练梯度/容量/数值研究
  │     └── 其他归档/待测课题与AWMA原有Lane
  │
  ├── C16：历史研究与采集资产（已冻结，不是新项目名）
  │     ├── 三条MoE selected-shard trace/地址证据
  │     ├── E1缓存、Split-K、dequant、FFN等已完成探索
  │     └── Stage A/Problem Discovery Reset终态
  │
  └── 新具体课题：只有经过科学筛查、值得长期推进时才另开窗口
~~~

**协调分支只存**：统一图谱、跨项目证据索引、文献实验组、已审查的状态入口、研究规划与交接。**不存/不替代**：大型raw、模型权重、各项目正式运行结果主分支、未授权的执行Goal、已有trace生成源。

AWMA窗口通过fetch协调分支获取问题地图；本窗口通过固定Git提交/独立审查了解AWMA新结果。任何新GPU任务仍由负责该科学问题的项目形成独立Goal。不要把AWMA的实验HEAD直接merge进协调分支。

### 2.1 已验证的协调仓库入口

- GitHub：[协调分支目录](https://github.com/swayhrl/accel-sim-framework/tree/hrl/ai-workload-research-coordination/docs/ai_workload_research)
- 图谱：[AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md](https://github.com/swayhrl/accel-sim-framework/blob/hrl/ai-workload-research-coordination/docs/ai_workload_research/AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md)
- 证据索引：[AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md](https://github.com/swayhrl/accel-sim-framework/blob/hrl/ai-workload-research-coordination/docs/ai_workload_research/AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)
- 协调协议：[COORDINATION_PROTOCOL.md](https://github.com/swayhrl/accel-sim-framework/blob/hrl/ai-workload-research-coordination/docs/ai_workload_research/COORDINATION_PROTOCOL.md)

版本化图谱V1中关于R27R3的“待审”应按较新的独立审查与同步文件理解，**不静默篡改V1历史快照**。

---

## 3. 截至2026-10-13的当前状态与权限

| 工作 | 最新可核对来源 | 当前结论 | 能否自动开新任务 |
|---|---|---|---|
| AI-ARCH Discovery | 本协调分支图谱V1 + 本交接 | 新主线已命名、研究范围和方法已定；尚无新原生实验 | **不能**；先开始文献/CPU科研分析 |
| C16旧Stage A | `ccd6928bfb420d1e4c554ec0e377bb8fbe377501` | `C16_STAGEA_TIER0_TERMINAL_PARTIAL`；DQ1、DQ2、DQ3、DQ4a均不完整 | **不能**；不修Observer V3、MP03_B或重开V2/Tier1/holdout |
| C16 Problem Discovery Reset | `635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f` | 14个既有观察、10个候选；0 PRIMARY/0 BACKUP；PC03/PC04 future-only | **不能**；不是无架构问题的证明 |
| AWMA Pre-L1翻译合并 | 机制paper qualification与独立holdout | 有范围的翻译服务抑制，部分正/零/小负性能；可围绕有限claim写作，尚无通用实机E2E | AWMA窗口决定；协调分支不授权 |
| AWMA R23G | `99d05f0ad221a1d44dd11bac0ed83965bb2c0942` | 在线策略计入CPU union/dispatch后的局部正结果；非稳定普遍端到端收益 | **不能自动扩展** |
| AWMA R26 | `1a2485011b300cddd5137bbccb91dd6d30cfc22f` | 冻结重复输入、tied-W训练，S2多完成一个物理batch；不是多样输入结论 | **不能自动扩展** |
| AWMA R27R2 | `ba73fa0bacf3db09f44d8ad421a0a36f56645898` | WikiText-2输入合格；B1 C1/S2与B0梯度数值对照未资格化；无容量测量 | 已STOP |
| **AWMA R27R3** | 执行`7bd31fae4c54e121d54743a803d978ee02a64959`；独立审查/状态`f0a6ec310c09cd011fffbe8a5ca22d6effacdf6b` | **独立接受`R27R3_B0_REFERENCE_NOT_REPEATABLE`，COMPLETE/STOP**；两次新进程B0在262,668,288个BF16梯度元素中有25个未过冻结逐元素门槛；未进入候选修正或容量 | **无新AWMA GPU Goal授权** |
| DTC-L1/ISCAS | 不在本轮审查 | 独立项目 | 本文不改变其状态 |

**关于R27R3的新旧来源优先级**：协调分支中`R27R3_INDEPENDENT_REVIEW_SYNC_2026-10-13.md`及AWMA最新`STATUS_AFTER_R27R3_REVIEW_2026-10-13.md`已经确认独立审查；此前README/CURRENT_STATE或图谱V1若写“pending”，以这些较新文件为准。严格禁止把25个梯度超限解释成B0数学错误、C1/S2正确/错误或候选的容量负结果。此结果是**当前预冻结数值参考的跨进程重复性门槛失败**。

没有亲自在本交接阶段SSH检查109的当前进程或GPU占用；上表是固定Git执行与审查结论，不是实时远程资源探针。将来下发GPU任务之前必须先复核锁和实际任务状态。

---

## 4. 历史C16：已经完成了什么，为什么不直接续跑

**最初任务**：Cross-Model Native Memory Characterization and Stratified Sampling。目标是用真实GPU运行/采集而非仅从矩阵形状推断AI访存，再按科学问题选代表性样本。后来的C16研究逐步走向“强软件基线后的真实时间瓶颈”，最终作为AI-ARCH历史证据保留。

### 4.1 真实模型和采集基础

建立了Qwen3-30B-A3B、DeepSeek-V2-Lite、OLMoE-1B-7B三条MoE模型线的选定任务数据；历史正式统计分别为：

| lineage | executed / zero selected paths | warp记录 | 活跃线程访存事件 |
|---|---:|---:|---:|
| Qwen3-30B-A3B | 41 / 202 | 100,352 | 3,147,776 |
| DeepSeek-V2-Lite | 169 / 74 | 362,496 | 11,538,432 |
| OLMoE-1B-7B | 129 / 114 | 132,096 | 4,196,352 |

三个lineage均为243条selected静态路径；“zero”可能是自然未选择专家，不是自动错误。采集为selected-shard证据，不等于完整模型连续执行中的真实缓存/TLB历史，也不能无损地从C16WARP1/MREF恢复模拟器所需指令/同步信息。

### 4.2 主要机制探索及结果

| 方向 | 真正观察到的现象/数值 | 为什么当前停止 | 不能否定什么 |
|---|---|---|---|
| E1量化权重缓存驻留 | 局部缓存保护有效；后续模拟的有界整窗略慢约0.205%；后续选择器的target-zero整窗上限约0.956% | 自然序列中其他权重竞争、保护成本及当前收益空间不足 | 其他容量、模型、未来执行模式的缓存研究 |
| 4-bit Split-K / grouped CTA | K2560→3072时split1 DRAM约4.04倍、时间1.60倍；经典GROUP_M16使split1 L2命中约95.95%；M64不拆比split8快4.93% | 成熟软件任务映射吸收主要局部性损失；剩余为并行任务数、局部tile与reduction取舍 | 所有矩阵运算的低并行度问题 |
| 低比特dequant结果复用 | M64严格重复比例75%，但新展开表示/共享同步成本高；局部隔离方案约0.826×，选定自然覆盖下整段理想上限约1.77% | 重复请求量不等于可省的关键路径时间；强kernel已有寄存器/共享存储局部复用 | 不同表示格式或其他算子真实执行瓶颈 |
| FFN gate/up并行 | 真实合法FFN wall约28.48%，gate/up理想零竞争并行上限7.893%；正确性合格的两流版本74.216→81.434ms，慢9.73% | 实际并发重叠有限且存在资源竞争，vLLM已有成熟merged实现 | 其他异构producer/consumer pair与布局交接问题 |
| DeepSeek GEMV重复 | 约50%选定逻辑字节重复，主要同warp/CTA内 | 没有证据把其换算为独立DRAM服务/等待时间 | GEMV某些具体工作划分优化 |
| Qwen MoE热点诊断 | 自然N/U近似；极端合成热点H更快 | 改变了专家集合，不能作为自然同语义零成本oracle | 自然专家活跃集变化的系统级成本 |
| 地址翻译静态页分析 | 选定权重/KV虚拟页集合可整理 | 没有真实GPU翻译阻塞时间和同进程完整时序 | AI/TLB研究问题本身 |

**解释上必须保留**：当前旧机制是对**冻结输入/实现/参数**的负面或收益不足，而不是“AI负载没有Cache/TLB机会”。

### 4.3 Stage A：四个系统问题没有得到完整归因

后来采用Qwen2.5-3B BF16/AWQ、vLLM的强编译路径，研究：DQ1算子时间组成、DQ2 batch与CUDA Graph、DQ3内存服务、DQ4a跨算子交接。结果如下：

- MP01 BF16 Prefill与MP05 AWQ representation control获得**各自范围内的局部有效时间结构**，但不能将旧Graph-OFF family比例搬到强编译Graph-ON整请求。
- Mode A＝编译开/Graph开；Mode B＝编译开/Graph关；历史Mode C＝编译关/Graph关。MP02/03旧Mode C的生成正确性不合格，不能与A直接做科学计时比较。后来无observer的A/B生成正确性通过。
- 编译路径下Python模块hook出现**0/4608**预期事件，说明观测方法没有被实际compiled runtime使用，不说明推理计算不存在或Mode B错误。后续静态编译产物分析停在语义归因`LEVEL_0_UNRESOLVED`，不能通过kernel名字强行恢复逐层/逐token事件。
- MP02/B1合法请求计时：Mode A **354.598205566ms**，Mode B **361.456542969ms**，A请求时间少**1.897416864%**；两边各5正式样本，只代表该冻结B1 32-token请求，不等于纯decode、GPU利用率或B4结论。
- MP03/B4 Mode B编译cache执行身份未达到事前合同，**0正式B-arm样本**；两次warmup输出正确，不能自动填充formal。故无B4完整A/B pair，无法评估B1→B4 throughput scale或Graph与batch的交互。
- 四个DQ均为`QUESTION_INCOMPLETE`；不是四个科学假设被否定。Stage A V2、Tier1、holdout、Observer V3、MP03_B第三次cache挽救、机制晋升均关闭/不授权。

固定审查入口：[Stage A终态独立综合](https://github.com/swayhrl/accel-sim-framework/blob/ccd6928bfb420d1e4c554ec0e377bb8fbe377501/docs/vm_tlb/review_packs/C16_STAGEA_TERMINAL_INDEPENDENT_CONSUMER_174NEW_V1/STAGEA_TERMINAL_SYNTHESIS.md)。

### 4.4 最后Problem Discovery Reset

Lane6在CPU/source-only下回顾14条既有观察、10个可证伪问题，最后`NO_NEW_PROBLEM_READY_FOR_NATIVE_VALIDATION`，0 PRIMARY、0 BACKUP，未启动109。

保留future-only **PC03自然MoE活跃专家集合成本**与**PC04异构tile交接**，但尚无自然同语义完整时间对照或具体合格算子对与成本上限；这**不是**两个已授权的实验，也不是完整AI-ARCH候选列表。

说明：这次较严格的正式native准入，并不禁止AI-ARCH未来为新问题设计**低预算发现性探针**。探针必须有合法任务、单变量强对照、可识别指标和STOP，但初期无需已证明完整机制的性能上限。正式机制与论文阶段仍须强baseline、headroom及独立验证。

固定：[Problem Discovery Reset](https://github.com/swayhrl/accel-sim-framework/blob/635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f/docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_RESET_174NEW_V1/CANDIDATE_DECISION.md)。

---

## 5. AWMA：过往演进及与AI-ARCH的关系

**AWMA不是只有一条TLB研究**。它继承了相关C12–C15模拟及C16真实采集技术，经历：地址翻译行为→native/simulator校准→pre-L1请求合并机制→AI执行组织/稀疏/动态图/训练显存，已经有不同成熟度的研究成果。

### 5.1 Q05翻译研究与模拟平台

历史Qwen2.5-0.5B FP16、Prefill2048/Decode32中，Q05 Prefill Attention在早期固定10k模拟周期下理想身份翻译的进度相对基准提高约56.55%，50k周期约76.55%。这是**固定周期进度/IPC敏感度**，不是整kernel或整模型speedup。125个翻译miss requester可归为19个新分配+106个合并，不是125次独立page walk。

随后发现simulator/native并发形状可能方向不一致。RTX4080/Ada模拟基准`AWMA_RTX4080_SIM_BASELINE_V1_PROMOTED_WITH_SCOPE`已资格化，但10/80周期是研究overlay，不是4080实际TLB参数；平台仅对限定VM/translation研究可用，不能宣称所有AI kernel全周期准确。

### 5.2 Pre-L1 translation coalescer：已有机制证据，范围有限

机制在L1翻译服务前识别重复的in-flight相同翻译请求并共享结果。已有有限容量模拟结构、正确性门、对照和独立留出样本；独立Reduce中L1翻译发起130→10，但执行周期同为7,716。其他核存在正/零/负响应，因此主要结论是**服务量可抑制，收益由是否落在关键路径决定**。

已取得`READY_FOR_PAPER_WRITEUP_WITH_OPTIONAL_EXPANSION`，但没有证明普遍加速、真实RTX4080整模型受益或真工艺硅片PPA，也没有最终的新颖性保证。该子课题由AWMA窗口独立管理/写作，不因新主线需要而重复机制实验。

### 5.3 更宽广的AI执行/访存与非LLM文献支线

AWMA已经研究过FP8表示准备、稀疏输出在线选择、确定性归约、动态几何图、3DGS优化器、GNN/等变计算、SSM/扩散、训练更新等，既有源码调研也有实际native实验。**注意其很多条目只有文献/源码，不是本机测量**。

有代表性的结果：

- R19 FP8准备的明显局部额外成本，经过成熟软件融合后显著缩小：说明不能把低效baseline制造的空隙直接当硬件机会。
- R20的某个fixed always-worklist求解版本整段退化约66.6%；最终hybrid未通过运行语义/正确性门，所以**不是**一个合法的hybrid性能负结果。
- R21/R22动态图或等变模型的准备、排序、force求导等问题：有源码能力和混合实验；仍缺一个严格代表自然图变化、强软件后显著净成本的完整结论；旧R21A/R22F1不应改名复活。
- R23G Qwen2.5-0.5B约束生成的真实在线CPU集合union/选择/头部切换：3个公开来源B4批次、9组正式比较的局部LIVE_HEAD改善约15.5%—33.8%；包含必要前置CPU成本；**完整生成改善并非稳定且一般化**，也尚未证明新硬件贡献。

AWMA已保留较大文献库，尤其Round09（27项工作/不同阅读深度）、Round21/24以及Round22边界账本；AI-ARCH的第一批文献阅读**先去重再增量调研**，不要因为换了新名字就重新做全部论文。

### 5.4 AWMA训练内存与数值：R24→R27R3

- **R24**：在冻结Qwen tied embedding/lm_head W目标区域，S2避免完整密集V×H梯度物化，相对原B0目标峰值减773.06MiB；时间相对更强的比较仍是mixed，只有短期数值资格。
- **R25**：采用更强的C1一完整梯度缓冲对照，Qwen发现点与独立Llama点，S2仍减少目标区峰值约535.8MiB和1,350.0MiB；相对C1的时间并非跨模型一致（Qwen有小正收益、Llama有极小退化）。适合保留为**软件/数据流容量收益及Pareto取舍**。
- **R26**：Llama tied-W、相同序列复制的5步训练，C1 B70 PASS/B71 OOM，S2 B71 PASS/B72 OOM，端点各3/3；只增加一个物理batch。共同B70时整步峰值S2反而高3.828MiB，计时不稳定；不能称显著整体内存下降或训练速度普遍提升。
- **R27/R27R1**：多样输入准备时停止，未得到容量实验。
- **R27R2**：合法WikiText-2多样输入到位，但B1上C1/S2对B0完整梯度的固定数值门未过；没有测多样输入容量。
- **R27R3最新已审**：在任何C1/S2归因之前，两个独立新进程的**B0对B0**自身已出现25/262,668,288元素的逐元素容差失败；Gate B1 STOP，0容量实验，无修正也无32步。独立AWMA审查认可此有限结果。其根因未定位，不意味着B0数学错误、S2机制被否定或R26结果失效。**没有R27R4自动执行权**。

该训练线一旦涉及浮点累积顺序/梯度数值可重复性、batch可行性、收敛质量等，必须与推理token正确性及模拟器时间研究分开设合同。AWMA继续独立决策，新Discovery窗口只同步证据及跨问题启发（图谱P08/P09）。

固定入口：[R27R3已接受独立审查](https://github.com/swayhrl/accel-sim-framework/blob/f0a6ec310c09cd011fffbe8a5ca22d6effacdf6b/docs/vm_tlb/literature_notes/awma/plans/STATUS_AFTER_R27R3_REVIEW_2026-10-13.md)。

---

## 6. 统一问题图谱：目前有哪些方向

图谱V1中的14个问题不代表14个已获资格的机制，也不等于14项新GPU任务。分类如下：

| 问题编号 | 科学问题（简写） | 目前证据状态 |
|---|---|---|
| P01 | 模型/Batch/阶段变动时，GPU瓶颈如何迁移 | C16部分算子真实结果；跨负载规律待建立 |
| P02 | 低M/低比特的资源利用低是否真的损失关键执行时间 | 几何填充率已见；强软件后时间headroom不足 |
| P03 | 权重/状态跨时间保持与缓存争用的收益平衡 | E1局部正但已测保护整体负/低上限 |
| P04 | 地址翻译服务何时可以早合并 | AWMA已有模型内服务抑制；时间效果不普遍 |
| P05 | 自然MoE专家动态选择真正昂贵在哪里 | 合成路由诊断存在；自然同语义残余未定 |
| P06 | 上下游算子数据就绪/异构tile交接 | 当前FFN双流负例；新具体算子对未定 |
| P07 | 结构化/稀疏输出的在线策略成本 | AWMA R23G有限软件正结果；硬件剩余未知 |
| P08 | 训练梯度/优化器状态哪些必须物化 | AWMA容量结果有范围；多样输入资格仍未闭合 |
| P09 | 浮点累积顺序如何限制可接受的数据流重排 | R27R3证实当前reference重复性难题；根因未知 |
| P10 | 动态图拓扑/索引/执行计划准备是否成为必要前序 | 主要文献/源码线索与部分混合实测 |
| P11 | 长上下文/KV/异构存储层次瓶颈 | 文献线索，当前项目缺同部署合法时间结论 |
| P12 | 服务/多GPU中的计算、通信和访存重叠 | 近邻较多，尚无本项目真实服务到达/SLO工作量 |
| **P13** | **GPU资源配比和扩展规律** | **当前优先开展的统一表征框架**；没有现成跨负载实验结论 |
| P14 | 非LLM稀疏执行与状态生命周期 | 已有文献覆盖，需选真实任务/质量/导数阶 |

重点联系：P01↔P02↔P12↔P13（并行度、利用率、资源饱和）；P03↔P04↔P05（数据和映射寿命）；P06↔P07↔P10（数据准备、发布、消费者就绪）；P08↔P09↔P14（训练状态与数值）；P05↔P11↔P12（MoE/KV/通信）。

### 6.1 下一轮真正优先的研究问题

我们已经同意由**P01 + P13**开启AI-ARCH Discovery，而不是立即选L1/L2或TLB新机制。

工作问题可以表述为：

> 负载从小batch到大batch、从Prefill到Decode、从推理到训练、从单GPU到更复杂部署时，计算供给、并行度、存储带宽/容量、调度与数据就绪，何时先后成为性能限制？扩大某一种资源后为什么收益开始饱和、下一类瓶颈何时显现？

先从**已有权威和论文中建立假设/反例**，不要在尚无可靠模拟校准的资源维度直接进行无穷端口/无限ROB式外推。可借鉴CPU ILP/资源上限研究的分解思路，但GPU是大量并行任务+多级存储/调度的不同约束结构；使用oracle需定义工作量、功能正确性及测量层级。

其他问题不删除；非LLM和训练必须在第一轮文献选样中实际出现，不是仅在研究范围封面上声明。

---

## 7. 文献研究路线与标准

### 7.1 第一轮建议阅读簇（优先具体实验组）

| 簇 | 论文/来源入口 | 要回答什么 | 注意 |
|---|---|---|---|
| 整体AI服务资源利用 | NanoFlow（OSDI 2025）、Bullet、MPK（OSDI 2026）、推理扩展研究 | 负载如何从计算、内存、调度和通信之间转换限制 | 服务到达/硬件配置/吞吐或SLO分母都需明确；不能把作者结果直接认定为4080结果 |
| 跨算子就绪与任务粒度 | Kitsune、VTC、Tawa、Twill、Syncopate | 已有流水/融合/虚拟张量/SM任务能力，剩下什么不易由软件解决 | 区分软硬件实现与可用平台，避免把已有软件primitive重写成创新 |
| MoE、KV与长上下文 | Patterns Behind Chaos、ReMoE、DirectKV等 | 自然输入路由、时间/空间局部性、数据驻留和传输条件 | synthetic hot-set和真实语义不能混；GH200/多GPU结果不迁移到RTX4080 |
| 训练和数据状态 | CCE、FlashOptim、FBGEMM，及R24–R27结果对应论文 | 梯度、优化器状态何时必须产生/存活；时间/容量/数值如何权衡 | 仔细区分短步数值资格、训练收敛、端到端与局部容量 |
| 非LLM代表负载 | Sobek、ALCHEMI、GS-Scale/TideGS，推荐/扩散/SSM | 不规则工作量和状态变化在真实应用中如何形成瓶颈 | 几何、导数阶、模型质量和输入时间顺序必须合法；不拿随机张量代替真实应用 |

上述是阅读候选，不是宣称已经完整精读全部论文或本机复现。**必须在实际论文阅读时核对公开版本/发表状态、具体数据和实验协议。** AWMA既有Round09/21/24、Round22账本和C16 LR12先作为去重入口。

### 7.2 一篇论文应留下的实验组记录

最小字段：

- paper title、版本/公开日期、原始链接、实际阅读章节/图表、是否完整原文；
- **exact scientific question**、作者动机、主要限制和已解决的能力；
- 具体实验组及其模型/数据/训练或推理场景、输入来源、预处理及长度/形状、平台/GPU/部署；
- software baseline和是否已采用已有优化；实验改变的唯一/多个变量，正确性/质量条件；
- 指标、分母、样本数量、观测层次（真实原生执行、局部算子、模拟器、估算、作者投影）；
- 作者报告的结论与**我们的推断分开**；未披露则标“未披露”，图上无明确数字不伪造精确值；
- 最近邻已有能力、可能的新约束、最小可证伪诊断、潜在资源成本与停止条件。

同名benchmark跨suite、GPU、输入条件不当作相同样本；论文作者的吞吐数字不转录为C16/AWMA本机headroom。

### 7.3 文献与实验并行方式

ChatGPT在Codex独立实验运行时继续查文献，重点寻找能区分解释的实验组；Codex实验有结果再回到图谱修正问题。不要把所有实验等文献综述结束才开始；也不要靠持续分配GPU任务来产生研究进度。

新论文笔记建议继续保存在协调分支的独立子目录（例如`docs/ai_workload_research/literature/`），每轮整理一个主问题及若干实验组，与AWMA已收录文献去重。**不要一开始建大型数据库/爬虫、全面重建文献平台**。

---

## 8. 新实验从发现到机制的三个层级

1. **DISCOVERY_PROBE｜发现性诊断**：确切可证伪问题、有意义的模型/输入与正确性、一个足以区分解释的原生指标、合理强的软件对照、有限预算、事前STOP。**不要求先拥有完整模型的headroom**；可以做很轻的可失败实验。但须用户给该具体GPU/CPU执行合同授权。
2. **HEADROOM_QUALIFICATION｜瓶颈定位**：冻结目标工作集合、必要前序/后续/同步与输出成本、目标族的实际时间权重、强软件基线、可移除成本或理想资源反事实、独立样本；区分局部时间、整段/整请求和容量收益。
3. **MECHANISM/PAPER｜机制与论文**：在问题确实存在且现有软件不足以解决后做有限机制设计（软件、模拟器或硬件）；对照要公平，完成数值/功能正确性、独立验证和所需PPA/可实现性。可以产出有价值的软件/数据流工作，不强行宣称硬件。

**不统一使用整应用5%作为所有方向生死线**。一个被证明独立的算子族可能有有价值的局部研究；但不能把低覆盖的局部收益写成整模型加速。时间、峰值内存、物理Batch容量、模型质量、收敛、能耗是不同结论。

特别容易犯的错误：

- 75%重复指令/50%逻辑重复字节 ≠ 75%/50%DRAM流量，更不是同幅加速。
- L2命中率和长scoreboard占比 ≠ 可直接缩短的请求wall time。
- 完全删除一个上游kernel但改变表示/算法 ≠ 免费oracle。
- 把多个并发kernel duration直接求和 ≠ 合法wall union；profiler带扰动的kernel时间也不能与未插桩wall随便相加。
- 更换模型/推理runtime/Graph/fusion后不能只把精度一个变量写成严格A/B。
- 单模型某输入成功 ≠ 跨模型结论；已使用于调试的输入不能再叫独立holdout。
- 源码支持的功能 ≠ 本机真实运行已成功；论文原型 ≠ 硬件/真实芯片性能。
- 失败的测量身份/正确性/数据权威 ≠ 研究假设科学为负。

---

## 9. 计算节点、SSH、资产与分工（恢复线索，不是实时配置）

| 资源 | 角色 | 使用规则 |
|---|---|---|
| **node109** | RTX4080 16GB、SM89真实GPU；Native producer、CUDA/NSYS/NCU/NVBit/SASS等 | 只有冻结的任务合同可使用GPU；AWMA/C16/AI-ARCH共用**一个GPU互斥锁**；正式测量前核GPU占用与软件身份 |
| **174-new** | CPU侧源码审查、文献或模拟准备、独立consumer；已资格化任务的Accel-Sim | 没有新合同不运行模拟器；可以执行CPU-only分析；不复制大型模型权重或假装有109同样的CUDA环境 |
| **node164** | 长期模型、输入、raw、manifest与checkpoint的durable authority | 大文件不进Git；数据写入后核验最终落盘size/SHA；不在协调分支迁移原raw |
| **ChatGPT（新AI-ARCH窗口）** | 读论文、分析原始来源、审核数据与研究判断、更新协调文档、生成Goal | 通过GitHub connector可直接读写授权仓库；**不等于已经SSH进节点执行** |
| **Codex** | 在对应109或174窗口执行明确Goal，冻结、采集、处理、提交、反馈 | 不跨分支/项目自动续跑；普通工程问题在科学边界不变时可solve-and-continue |

### 9.1 曾经使用过的精确环境/路径

~~~text
Repository: swayhrl/accel-sim-framework

174-new 历史主仓库:
  /root/workspace/accel-sim-framework

109 历史主仓库:
  /home/huangrulin/workspace/accel-sim-framework

109 独立worktree历史根:
  /home/huangrulin/workspace/worktrees/

109 活跃资源数据根:
  /data/c16/

164 从174视角的历史共享挂载:
  /root/share/mnt164/huangrulin/c16_ai_workload/

109 所有CUDA/JIT/profiling任务共享锁:
  /data/c16/locks/c16_gpu_campaign.lock

109 过去用于C16 Stage A的特定runtime:
  /data/c16/envs/c16-vllm-v0.30.0-sm89-v1

109 曾用SSH入口:
  ssh loongson@10.156.120.109

174-new 曾见容器端口:
  2239
~~~

以上仅为**历史恢复线索**，不是新实验强制环境，也不意味着这些目录和连接方式今日不变。新窗口如需真正下发任务，让所属Codex先检查其已有worktree、SSH config、repo/ref、环境和GPU锁，不要凭路径猜测而reset或重建。不要打印SSH私钥、token或其他凭据。

### 9.2 大数据流向与Git交接

~~~text
109真实执行/原始采集
→ 冻结输入、GPU、软件、runner、sample身份
→ 109本地输出与manifest / SHA
→ node164 durable raw、checkpoint、index、独立落盘校验
→ Git发布小型review pack / digest / final decision
→ 174-new按需只读拉原始raw做独立consumer或重算
→ ChatGPT审查科学结论
→ 仅在有新问题时更新AI-ARCH协调分支证据索引
~~~

模型权重长期以**164权威、109活跃副本、174不留权重副本**为默认分工。文件名、长度、checksum、git blob SHA、Git commit SHA是不同的身份字段。`.nsys-rep`、大trace、模型权重、完整梯度原始张量不放Git。不会为统一新名称搬迁既有大文件。

### 9.3 当前Lane状态不要混淆

- 旧C16 **Lane6/174-new**：最后CPU-only Problem Discovery Reset已经完成（`635b2f22…`），历史任务**STOP**；未来可作为新Discovery CPU任务执行者，但需要一个新、独立的Goal。
- 旧C16 **Lane7/109**：Stage A已收口，历史任务STOP。不要重启任何compiler attribution、cache身份恢复或旧Observer。
- AWMA **Lane G/109**：R27R3已执行并在AWMA窗口独立审查`COMPLETE/STOP`。当前没有从其结果自动授权下一轮；**不因名为G或109而被AI-ARCH接管**。
- AWMA **Lane E/F**、其他历史窗口：以AWMA自己的最新独立协调状态为准；没有本文件的新执行权。
- DTC-L1或其他项目可能使用计算资源，**实际未来运行前再检查**，不能仅凭本记录“没有AWMA GPU Goal”就判整个109 GPU无人使用。

### 9.4 给Codex的Goal方式（用户明确偏好）

未来若需要在节点下发：

1. **一个可一键复制的完整代码块**，包含工作branch、固定starting commit/tree、exact Goal名、必须读的handoff、模型/输入、权限/不能做的事、验证指标、停止规则、raw与Git交付。
2. 合并可连续执行的“CPU证据/设计 → 正确性门 → 小规模正式测试 → 自检/发布”，避免为每个普通工程修补另开对话；可执行条件充分时**solve-and-continue**。
3. 普通路径、环境包装、manifest或Git传输问题，在不改变科学合同且可确定性解决时修复并继续；无法还原的scientific payload、数值/语义身份/预算/观察端点变化需STOP由用户审。
4. 所有模拟器新功能必须**opt-in、默认关**，避免改变历史baseline；观察/统计工具必须验证不改变结果。
5. **严禁干扰已经运行的Goal**：不重启、不中断、不调整cache/模型、不开并发GPU任务；并行只用于独立CPU/source工作和有真实资源隔离的任务。
6. 交付要有raw索引、大小/SHA、固定commit/tree、远端fetch-back、必要源码/数据自检、资源锁释放及终态报告；ChatGPT审查时区分“Git端直接核过”和“节点执行者receipt报告”。

不要为了效率跳过必要的科学gate，也不要为了完美可复现无限做工具工程。用户偏好**轻→重、并行推进有实际价值的工作、负结果及时停止、留独立验证样本**。

---

## 10. 研究方法、阅读优先级与实验论证标准

### 10.1 强软件先行，但不把论文近邻当strict A/B

原论文的软件最优实现、当前vLLM/Inductor/Marlin/QUICK/FLUTE/FlashAttention等能力，以及我们实际能跑的fixed runtime必须分开。公共论文证明某软件“支持融合”只能限制创新，不能充当本机等同checkpoint/shape的性能对照；反过来单纯CPU/GPU运行低效也不能自动表示硬件瓶颈。

对任何候选，至少问：

- 谁在什么具体AI场景下必须做这份工作？
- 当前最好合法软件已经如何缓存/融合/合并/调度？
- 是执行时间、物理数据服务、状态容量还是数值限制？能否合法观测？
- 能否设计一个结果明确时即可停止的单变量诊断？
- 若后来要设计硬件，当前GPU/模拟器能表示这种干预吗，是否需改指令/语义？

### 10.2 证据状态分层

- **NATIVE_MEASURED**：真实GPU测量，准确指出region、model、sample、时间分母；可独立raw重算才提高可信度。
- **SIM_MODELED**：有绑定配置/trace的模拟结果；不是实硅事实，尤其AWMA翻译overlay须明确作用范围。
- **SOFTWARE_SOURCE**：源码证明可行能力或依赖；不证明运行时净收益。
- **PAPER_AUTHOR**：论文作者的特定实验组结论；不是我们复现的结果。
- **DESIGN/HYPOTHESIS**：未资格化的问题卡或机制设想，不能表述为已观察瓶颈。
- **QUALIFICATION_FAIL/UNKNOWN**：因数值/输入/实现身份或观测工具不足未能判断；必须与有效负面性能结果分开。

正式独立审查的接受范围优先于简单执行报告；协作Git分支同步**不自动变成科学权威**。

### 10.3 需要避免的“工程黑话遮蔽科学问题”

面对用户优先用中文讲：研究问题是什么、为什么可能发生、做了什么对照、得到什么、不能说明什么、下一步是否有论文价值。内部decision标签与SHA保留作事实锚点，但不要用满屏PASS/STOP字符串代替科学分析。

---

## 11. 下一步应该做什么（新窗口的前两轮）

### Round A：文献与已知实测交叉复核（优先启动，不消耗GPU）

**目标**：从负载/资源扩展角度提取3—5条有明确条件的候选体系结构规律，且每条至少有一个实际研究实验组和一个反例/限制。不按模型资产库存倒推；必须包含至少一组训练、至少一组非LLM问题，推理也要覆盖不同执行阶段。

建议最先认真读：NanoFlow的计算/内存/网络平衡、MPK的执行粒度、推理规模变化研究、AWMA旧Round09中的GPU异步/流水与数学计算调度，以及非LLM Sobek或3DGS案例。逐篇回原文方法、图表、具体模型/配置，不按标题泛泛总结。新窗口可从2026年的新公开版本检索增量论文，但要核对日期/版本。

**交付**：

1. 每篇“实际实验组→作者结论→我们推论→缺失数据”的可追溯笔记；
2. 一份轻量的**计算/并行/存储/调度/就绪/容量/通信瓶颈对照矩阵**；
3. 对图谱P01/P13的初步修订建议：哪些现象是可迁移的约束，哪些只适用于某平台/软件；
4. 最多2—3个新**可证伪**问题，分别注明最便宜证伪实验、强软件对照、可能的负结果、是否必须109。

**不要**直接把两篇论文的加速比平均、据此推我们GPU的理论极限；不要提前写“新机制必须是L2/TLB”。

### Round B：必要的CPU-only证据核查与极小实验准备

只有Round A识别出值得检验、而且已有raw/source确实可帮助区分的具体问题时，才考虑给**174-new**一条**新AI-ARCH Discovery CPU-only Goal**：复用固定C16/AWMA evidence index，最多检查与该问题直接有关的几份raw/index/source，不全量重hash旧资产、不重启Stage A或模拟器。

如果必须用109真实GPU才能判别，先列严格的**DISCOVERY_PROBE合同**：模型/输入、可观察时间/资源、强基线、竞争解释、单变量、预算、STOP及必要样本；与AWMA/DTC正在使用的GPU资源协调。**现在并未批准该GPU Goal**。

### Round C：独立验证/机制开发（只有科学结果正面才进入）

若发现性实验存在稳定、合法的资源限制，才进入更完整的headroom、最近邻、独立样本，并决定软件机制、模拟器资源上限研究或硬件微结构。没有结果时停，不为了机制或论文题目硬凑positive。

**本交接文件本身绝不自动触发Round B/C。** 但Round A中的论文研究与跨项目只读核对可在新ChatGPT窗口直接进行。

---

## 12. 并行支线、保留资产与停止项

| 支线 | 当前归类 | 后续态度 |
|---|---|---|
| **AWMA Pre-L1翻译请求合并论文** | 既有有范围资格化研究 | 由AWMA窗口独立推进写作/必要补充，不要求本窗口重新做模拟；文献中考虑intrawarp/MSHR等最邻近机制 |
| **AWMA R23G在线稀疏分派** | 已接受有限软件正结果 | 可作为“运行时已知信息→选择执行方式”的范例；没有新硬件任务 |
| **AWMA R24—R27R3训练梯度** | 容量正结果+新参考重复性资格问题 | AWMA窗口继续独立审查与以后决策；在图谱P08/P09保留跨项目信息 |
| **AWMA动态图/NequIP/3DGS/推荐等** | 文献与源码/部分局部实测；不少未成正式机制 | AI-ARCH非LLM研究的优先去重来源；不能把源码推断当原生瓶颈 |
| **C16 PC03自然MoE专家集合** | FUTURE-ONLY / NOT ADMITTED | 有自然同语义路由、可比较时间及真实覆盖时才可重新设计小探针 |
| **C16 PC04异构tile交接** | FUTURE-ONLY / NOT ADMITTED | 先找真实算子对与强软件完整pair成本；不由旧FFN负例直接否定 |
| **C16旧E1/Split-K/dequant/FFN** | 冻结/关闭的机制试验 | 保留作用范围与反例；不能简单改名后重跑，不代表所有负载无机会 |
| **C16旧Stage A Observer/MP03_B** | TERMINAL | 不做Observer V3、第三次cache修复、旧Tier1、holdout或旧DQ重建 |
| **DTC-L1/ISCAS** | 独立论文项目 | 不合并证据/不擅自抢占资源；仅在用户另行授权下交换可适用的方法知识 |

未来特别建议留意：不同AI阶段GPU资源瓶颈迁移、跨算子就绪与异构tile、长上下文KV与分层存储、训练状态生命周期、非LLM不规则计算。所有这些是**研究主题**，不是已存在/已授权的硬件机会。

---

## 13. 复现与独立审查规则（新窗口接管必读）

- **读固定来源优先**：实验结果以review pack与独立review的确切commit/tree为准；协调文档是导航，可能滞后；不要仅看旧README顶部“当前进行”。
- **按身份审计**：采样、数据与输入、模型revision、GPU、precision/backend、CPU/GPU流程、版本、原始文件大小/哈希及数值/时间分母是不同的证据维度。
- **不重用holdout**：已经用来修工程/选择winner/画趋势的输入不能在论文声称为新的独立验证。
- **对照的结果应公平**：相同语义、相同必需计算范围；必要准备（图排序/union/dequant/梯度发布）不能悄悄移出时间分母；同输入的GPU进程锁独占；不要依赖未经对齐的profile来支持完整wall归因。
- **实验失败的分类**：输入科学payload缺失；可从accepted raw确定性恢复的runner/index包装缺失；执行cache/二进制身份错；正确性错；统计未稳定；机制实际为负。前者不必都升级为“研究不可能”，后者不能改窗口/阈值挑到正面为止。
- **opt-in & fail-closed**：新simulation功能默认OFF；发现不符合事前关键身份、数值或资源安全门就立即STOP受影响任务，保留已合法数据。只有普通工程问题自主修复并继续。
- **人和模型的职责边界**：ChatGPT可通过GitHub connector核仓库，但不声称亲自SSH、查看164真实bytes或结束109进程；Codex的结果也要区分实际运行收据和独立审查。

---

## 14. 关键Git证据与按需阅读顺序

### 14.1 必须先看

1. AI-ARCH协调目录最新README / CURRENT_STATE / 统一图谱V1 / 跨项目证据索引V1 / 协调协议 / 本交接。
2. [协调层R27R3审查同步](https://github.com/swayhrl/accel-sim-framework/blob/77a1c5267563adde12a883b694d8a280d87858be/docs/ai_workload_research/R27R3_INDEPENDENT_REVIEW_SYNC_2026-10-13.md)。
3. [AWMA最近状态](https://github.com/swayhrl/accel-sim-framework/blob/f0a6ec310c09cd011fffbe8a5ca22d6effacdf6b/docs/vm_tlb/literature_notes/awma/plans/STATUS_AFTER_R27R3_REVIEW_2026-10-13.md)。

### 14.2 C16固定历史恢复点

| 事项 | commit | 路径或备注 |
|---|---|---|
| 旧探索轮terminal | `ca6c33ae0431d91aa7c6a43cbb79522402dd7580` | `docs/vm_tlb/review_packs/C16_AI_WORKLOAD_EXPLORATION_WAVE_TERMINAL_SYNTHESIS_174NEW_V1/` |
| Stage A最终独立consumer | `ccd6928bfb420d1e4c554ec0e377bb8fbe377501` | `docs/vm_tlb/review_packs/C16_STAGEA_TERMINAL_INDEPENDENT_CONSUMER_174NEW_V1/` |
| 最新C16问题筛查 | `635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f` | `docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_RESET_174NEW_V1/` |
| C16当前历史handoff | 同上 | `docs/vm_tlb/chatgpt_handoff/c16/C16_PROBLEM_DISCOVERY_RESET_CURRENT_STATE.md` |
| C16跨模型采集/旧长期handoff | 按项目证据索引 | 不把selected shard直接当完整模型地址时序 |

### 14.3 AWMA关键固定恢复点

| 事项 | commit或入口 | 说明 |
|---|---|---|
| Q05早期TLB/PTW | `bb92e5a1559dd7e2b2520e9a7a4937262664512c` | 10k/50k固定周期的机会，而非E2E加速 |
| Pre-L1 coalescer论文资格化 | `docs/vm_tlb/review_packs/AWMA_PREL1_COALESCER_PAPER_QUALIFICATION_V1/` | 机制服务抑制与有范围性能、RTL proxy；保留其冻结机制身份 |
| R23G在线分派 | `99d05f0ad221a1d44dd11bac0ed83965bb2c0942` | 有范围局部软件正结果，完整生成不稳定 |
| R26训练容量 | `1a2485011b300cddd5137bbccb91dd6d30cfc22f` | 相同序列复制，C1 B70 / S2 B71 |
| R27R2多样输入资格 | `ba73fa0bacf3db09f44d8ad421a0a36f56645898` | C1/S2梯度资格失败，无容量测量 |
| R27R3执行结果 | `7bd31fae4c54e121d54743a803d978ee02a64959` | B0自身参考重复性门失败、STOP |
| **R27R3独立接受与最新AWMA状态** | `f0a6ec310c09cd011fffbe8a5ca22d6effacdf6b` | 已确认审查、无自动下一Goal |
| AWMA文献研究（最新此时） | `hrl/awma-chatgpt-literature-notes-v1` | Round09/21/22/24及按需最新状态；先查ref别读旧首页 |

### 14.4 文献来源（第一轮起点）

- NanoFlow：https://www.usenix.org/conference/osdi25/presentation/zhu-kan
- MPK：https://www.usenix.org/conference/osdi26/presentation/cheng
- Bullet：https://arxiv.org/abs/2504.19516
- Kitsune：https://arxiv.org/abs/2502.18403
- VTC：https://www.usenix.org/conference/osdi26/presentation/hu-muyan
- Sobek：https://arxiv.org/abs/2607.18074
- AWMA Round09固定笔记：`docs/vm_tlb/literature_notes/awma/rounds/2026-09-27_ROUND_09_BROAD_SIDE_RESEARCH.md`
- AWMA Round22边界账本：`docs/vm_tlb/literature_notes/awma/empirical/ROUND22_FAMILY_BOUNDARY_LEDGER.tsv`

这是一组**研究入口**，非已在本handoff重新做全原文审计。不要只看本文摘要就凭空补出作者未披露的平台/形状/加速数字。

---

## 15. 新ChatGPT窗口第一条消息：可直接复制

> 以下是AI-ARCH Discovery项目截至2026-10-13的完整交接。请先完整阅读仓库`hrl/ai-workload-research-coordination`分支下：  
> 1. `docs/ai_workload_research/AI_ARCH_DISCOVERY_HANDOFF_CONTEXT_2026-10-13_V1.md`  
> 2. `docs/ai_workload_research/AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md`  
> 3. `docs/ai_workload_research/AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md`  
> 4. `docs/ai_workload_research/COORDINATION_PROTOCOL.md`、`CURRENT_STATE.md`及R27R3较新独立review同步。  
> AI-ARCH是总科研计划，本窗口负责AI-ARCH Discovery和当前阶段的总体协调；AWMA继续由原独立ChatGPT窗口管理，C16只作为历史证据，不再叫新研究线C16。研究范围包含训练和推理、LLM及非LLM、单GPU/多GPU与CPU–GPU。  
> **当前不授权任何109 GPU、174模拟器、Stage A恢复或新机制任务。** AWMA R27R3已经独立审查为`R27R3_B0_REFERENCE_NOT_REPEATABLE`并STOP；不要依据旧README的pending信息重启它。  
> 新主线从**P01/P13：AI负载GPU资源瓶颈迁移与资源扩展规律**开始。请先核对最近两年的代表性原始论文（NanoFlow、MPK、推理扩展研究，并加入训练与非LLM实例）的**具体实验组**：研究问题、实际模型/输入、平台、强软件基线、改变和控制变量、真实/模拟/估算的指标及局限；把作者报告与我们的推断分开。  
> 先向我输出一份有科学解释的第一轮研究计划和最值得精读的论文顺序，不需要为保持节点忙碌开新Goal。与AWMA通过协调分支交换**已审查**结果，不干扰AWMA原实验工作。之后按需要将论文和研究结论写回协调分支；新GPU任务必须另经我批准。

---

## 16. 最终接管清单

- [ ] 新窗口明确：AI-ARCH Discovery兼当前总协调；AWMA另窗口；C16是历史。
- [ ] 查协调分支**最新HEAD**及R27R3的最新独立审查，不用旧的pending快照。
- [ ] 图谱P01/P13作为第一轮文献研究主问题，不把14张问题卡当14个批准实验。
- [ ] 第一轮文献不仅包含LLM推理，还包含至少一个训练和一个非LLM典型负载。
- [ ] 复用AWMA Round09/21/22和C16 LR12已有纸面实验证据，先去重。
- [ ] 109 RTX4080共享锁、174-new CPU/模拟、164 raw authority规则不变。
- [ ] 不启动C16 Stage A V2、Observer V3、MP03_B恢复；不重新执行AWMA R27R3。
- [ ] 新问题满足发现性诊断合同后，才为对应Lane起新任务；机制/论文证据的门槛更高。
- [ ] 新科学事实先审查原始权威，再更新协调索引；GitHub协调分支不能覆盖实验authority。

**交接总结**：这不是“C16失败后换一个项目名”，而是把C16和AWMA积累的正负实验证据整合成更高层次的AI负载体系结构问题发现方法。下一项实际工作是**论文原始实验组与GPU资源瓶颈规律的交叉研究**；当前不存在由本交接触发的GPU/模拟器执行任务。
