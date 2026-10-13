# Round A12｜跨负载任务组织粒度与GPU资源瓶颈可辨识性：原生证据交叉核查与单一候选收敛

**执行者：ChatGPT／AI-ARCH Discovery；日期：2026-10-13。**  
**执行：仅固定GitHub、小型原始计时与既有原文审查交叉读取、数学归纳、协调笔记。未访问109/174/164节点运行、CUDA、训练、模拟器、NSYS/NCU或新Codex Goal；未启用任何新holdout。**  
**最终结论：`P01_SCOPED_SOFTWARE_GRAIN_RESPONSE_ACCEPTED / P13_RESOURCE_CAUSALITY_NOT_IDENTIFIED / Q_A12_01_PARKED_DESIGN_ONLY / NO_NEW_NATIVE_ADMISSION`。**

> 本轮的目标不是再找一个更大的batch以提高数值，而是检验：同一个“规模敏感”外观之下，哪些干预已经属于已有软件组织选择，哪些才足以构成**强软件之后可归因于物理资源供给**的架构问题。上一轮A11正式已接受的科学证据保持不变；本文件中的新比值是`OUR_DERIVATION`，不是独立新测量或能够实现的零开销oracle。

## 0. 直接依据、固定范围与证据等级

| ID | 固定authority与直接读取范围 | 证据等级、不可扩张边界 |
|---|---|---|
| M1 | [Lane M V1R1执行`1f69559df4f51290589de72876f36a756c5439f0`](https://github.com/swayhrl/accel-sim-framework/commit/1f69559df4f51290589de72876f36a756c5439f0)；[`FINAL_REPORT.md`](https://github.com/swayhrl/accel-sim-framework/blob/1f69559df4f51290589de72876f36a756c5439f0/docs/ai_workload_research/review_packs/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1R1/FINAL_REPORT.md)、`TIMING_SAMPLES.tsv`、`STATISTICAL_SUMMARY.json`、`DIAGNOSTIC_SUMMARY.json`和[`A11独立审查`](../reviews/AI_ARCH_ROUND_A11_LANE_M_T_JOINT_INDEPENDENT_REVIEW_2026-10-13_V1.md) | `NATIVE_PRODUCER_109 / GITHUB_TIMING_RECOMPUTED`，144行/36个配对block已被A11逐行独立重算；同一个0.6M参数OAM-S、32个Si静态帧、RTX4080、同AOT模型；不是自然MD连续轨迹、跨模型或物理资源扫参 |
| M2 | [冻结执行runner `75cfac972a56b71c4b776ce87c8ab311732ec75b`](https://github.com/swayhrl/accel-sim-framework/blob/75cfac972a56b71c4b776ce87c8ab311732ec75b/tools/ai_workload_research/nequip_static_batch_v1r1/observe.py)；另读M1的`DIAGNOSTIC_SUMMARY.json` | `SOURCE_AUDITED + EXECUTION_SIDE_AUX_DIAGNOSTIC`：32帧总完成wall包含数据准备、按后端构图、energy/force/stress模型与CPU输出；diagnostic是事后插桩三次、不同于主计时分母，不得把interval之和当关键路径 |
| C1 | [C16 GROUPED W4 Split-K `a3a36e64ae4a3a316df2bf4dfc9cac95caf8e164`](https://github.com/swayhrl/accel-sim-framework/tree/a3a36e64ae4a3a316df2bf4dfc9cac95caf8e164/docs/vm_tlb/review_packs/C16_GROUPED_RESIDUAL_PARALLELISM_CONSUMER_174NEW_V1)，本轮直接重读`M_SWEEP_COMPARISON.tsv` (Git blob`aa5165f0fdf9f875ea176008326fc9e003707cab`)、`RAW_RECOMPUTE.tsv`、`FINAL_DECISION.json`；对照[A3来源审查](AI_ARCH_ROUND_A3_HISTORICAL_EVIDENCE_CLOSURE_AND_CANDIDATE_ADMISSION_2026-10-13_V1.md) | `ACCEPTED_C16_NATIVE_LOCAL_OPERATOR`，50正式样本/点，局部W4算子而不是请求级全模型；M和Split同时改变计算几何/CTA/归约 |
| L1 | [NanoFlow OSDI 2025官方论文入口](https://www.usenix.org/conference/osdi25/presentation/zhu-kan)、[MPK OSDI 2026官方论文入口](https://www.usenix.org/conference/osdi26/presentation/cheng)；既有[Round A1资源因果精读](AI_ARCH_P01_P13_RESOURCE_MODEL_CAUSAL_READING_2026-10-13_V1.md) | 本轮重新核对原始会议页方法/摘要，沿用A1曾逐章核对的论文特定实验组；`PAPER_AUTHOR / PRIOR_GROUP_AUDIT`，未执行其GPU |
| L2 | [Bullet原文`2504.19516`](https://arxiv.org/html/2504.19516)、[Kitsune原文`2502.18403`](https://arxiv.org/html/2502.18403)、[Tawa`2510.14719v2`](https://arxiv.org/html/2510.14719v2)、[Twill`2512.18134v1`](https://arxiv.org/html/2512.18134v1)；既有[Round A2逐实验组审查](AI_ARCH_P01_P13_ROUND_A2_EXECUTION_RESOURCE_BOUNDARIES_2026-10-13_V1.md) | 本轮**未重新读完整论文各图**，具体平台/实验数字沿用A2接受范围；Kitsune整应用资源扫描主要A100类模拟而非完整原生；Tawa/Twill为H100/B200原生局部kernel |

已接受前提：A11核实M四臂3 fresh processes、每臂36个整组样本、总输入32帧×64 Si、四臂同44,388条有向周期边、各进程同一个AOT产物、数值/力/应力PASS；这些身份来自M的Git报告与执行侧CPU raw复算，本ChatGPT没有登录164重新散列二进制训练/几何产物。Lane T A10 `NO_VALID_SMALL_TRAINING_PAIR`仍STOP，不把它混成P13原生反证。

## 1. Lane M：总工作量固定的批次数关系和最简单的非因果参照

**干预与不变量**：

- 四臂完整执行同样的32个已选Si结构（2048原子），相同训练好的OAM-S模型、相同AOT产物、每结构同样能量/力/应力输出、相同原始图多重边与预冻结FP32模型数值门，完成wall分母相同。
- C2与G2均B2/16次调用，改变的是**CPU matscipy构图 vs GPU alchemiops构图及传输放置**，不是单纯设备算术速度。
- G2/G4/G8固定GPU构图library，B由2→4→8，同时改变单次输入形状、每次图边数、单次模型算子形状、库调用/launch数量、合批准备及内核内部选择；不是单独增加物理SM、HBM或缓存带宽。

### 1.1 从固定32帧整体时间除以调用数（计算账本，不是每次调用的固定耗时）

| arm | B | 32帧总调用数n=32/B | 主计时整组36样本中位wall | `median(wall)/n` | 同G2每调用恒定的简单参照 | 实际相对参照偏离 |
|---|---:|---:|---:|---:|---:|---:|
| N-C2 | 2 | 16 | 20.758169 ms | 1.297386 ms | 不与GPU参照共用 | 另一个backend |
| N-G2 | 2 | 16 | 26.044454 ms | 1.627778 ms | 26.044454 ms | 参照点 |
| N-G4 | 4 | 8 | 13.548172 ms | 1.693522 ms | 13.022227 ms | **+0.525945 ms／+4.04%** |
| N-G8 | 8 | 4 | 7.602214 ms | 1.900553 ms | 6.511113 ms | **+1.091100 ms／+16.76%** |

**`OUR_DERIVATION`：** 简单参照`T_ref(B)=T_G2×(2/B)`只用于判断形状：如果每个较大batch调用的整组成本完全同G2的一次调用，理论上调用数减半/四分之一将得上述对应时间。观测的G4/G8改善接近但**未达到**这条比例。它不是真实可执行“零额外工作”的oracle，更不能把偏离值解释为可以靠扩SM/改cache消除的硬件残余。

尤其，`median(wall)/n`只是**把整组时间按批次记账的平均成本**。它包含随B增长而变化的实际图/模型工作，不能称“CPU launch固定开销”；也不能由接近反比独占认定CPU launch是主要瓶颈。固定同一个AOT文件SHA不等于不同B内部kernel指令/选择均不变。

### 1.2 诊断与硬件解释的距离

事后仪表化三个完整sweep/条件的记录：

| arm | instrumented邻居构图区间中位（ms/32帧） | GPU模型事件区间中位（ms/32帧） |
|---|---:|---:|
| C2 | 10.675 | 7.522 |
| G2 | 16.295 | 7.402 |
| G4 | 8.268 | 3.823 |
| G8 | 4.219 | 2.383 |

- B2两臂主计时wall相差约**5.286ms**（GPU更慢），邻居构图诊断差约**5.619ms**，**方向相容但不是严格差值归因**：阶段观察与完整wall不在同一次主计时路径，诊断会插桩/同步，比较不构成加法分解。
- G2→G8时图构图与模型event均随调用数减少显著缩短。观察并非“GPU计算相同且只有CPU启动数减少”；反之，它也**未测得GPU SM不饱和造成了多少可消除的wall**。主计时没有单变量SM/L2/DRAM改变、硬件服务饱和或校准反事实。
- **最关键的缺失**：没有CPU backend的B4/B8，因此不能得出“GPU构图总体比CPU构图高效”或在每个B下选到最强软件路径。现有G8是**四个已测条件**的最好值，而非强软件全局最优。

**M可接收科学陈述**：相同32个真实静态几何、原生模型正确性合格时，任务提交粒度与后端选择使完整wall发生有范围的强响应；其效果方向随条件而变。**M不足以给出P13物理资源瓶颈。**

## 2. C16：另一种任务粒度更细、但结论并不相同的规模交叉

C1固定原始Grouped W4 Split-K raw与consumer：

| M | Split1 CTA | Split8 CTA | Split1整算子中位（µs） | Split8整算子中位（µs） | 更快策略 |
|---:|---:|---:|---:|---:|---|
| 1 | 96 | 768 | 74.752 | 32.976 | Split8 |
| 16 | 96 | 768 | 76.800 | 40.976 | Split8 |
| 32 | 192 | 1536 | 86.016 | 67.584 | Split8 |
| 64 | 384 | 3072 | 113.904 | 119.808 | **Split1反超约4.93%** |

当前只支持该**定点算子族**中软件策略的规模相关反转。Split8通过更多CTA暴露并行度，却产生附加split/reduction及流量；随M增长有用计算量、tile覆盖、split1 CTA也改变。这里有GPU SM任务供给的机制线索（RTX4080 76SM，小M Split1仅96 CTA），却没有隔离“SM数/物理服务能力”单变量，不能由CTA数和active warp%直接计算端到端加速。

与M形成**有意义但不等价**的横向对照：
- NequIP增大B→**减少**独立batch调用，较大B单调用更重，完整wall下降；适合减少重复准备/图构建/launch的解释。
- C16 Split8→**增加**CTA与K分解，低M时胜出；高M加剧额外工作时Split1反超。
- 二者的共同现象只是“**当工作规模与分解策略变化时，任务粒度的收益取决于额外开销与并行服务的权衡**”，不是相同物理瓶颈，更不能把M的毫秒与C16的微秒放在统一资源曲线上回归。

## 3. 成熟研究对这个问题已经覆盖到哪里？

| 论文/具体组（既有A1/A2准入事实） | 贡献及证据等级 | 对新的P01/P13主张的约束 |
|---|---|---|
| **NanoFlow** OSDI25，§3–4/§6，LLM Serving真实系统 | 纳米批次可拆细并跨计算/访存/网络资源调度重叠；作者§6.4拆后**仅顺序执行**平均吞吐下降13.2%，经过并发调度才收回损失。作者外部native，非本机4080 | “任务越细越好/越粗越好”均非通则；任何新粒度结论必须对照允许重排/重叠、实际干扰的强服务软件 |
| **MPK** OSDI26，§4–7，持久mega-kernel | SM级tGraph/JIT/AOT事件调度、细粒度跨算子流水与共享存储管理已有实机软件实现。每线程寄存器最大task footprint为源码约束，但其时间损失未被独立隔离 | 不能以“GPU现在不支持细粒度数据就绪”作为未经限制的创新，需证明MPK这类强软件之后剩余的寄存器/资源问题 |
| **Bullet** §2–4，Prefill/Decode分区 | 原生SM masking/调度，SM-scaling服务模型由实机标定；不同阶段任务波尾随请求长度变化 | 调整可用SM配额**不等于改变物理芯片SM数量**，不同代GPU变化多资源，相关性不等于物理扩容因果 |
| **Kitsune** §4/§6 | A100真实queue微基准；较广泛应用效果和on-chip compute/L2 bandwidth×2主要为**A100类修改模拟器**。有的资源实验会同时改变两种资源 | 不能把其作者模拟器两资源一起翻倍的增益说成独立L2或compute因果，也不能直接映射到本轮NequIP编译后RTX4080 |
| **Tawa/Twill** 局部H100/B200 kernel | 作者有寄存器/SMEM与软件流水深度的实际局部权衡、编译器/调度在固定资源下接近强FA3/FA4的限制 | 提示具体物理资源寿命可能值得研究，但这些局部kernel不同于M、C16完整对象；若进入硬件题，必须优先对照这类强软件而非弱串行baseline |

**OUR_INFERENCE**：GPU“有效ready工作量”与“软硬件资源服务”确实是横贯算子/AI系统的一组概念，但是软件已经拥有融合、split、persistent、overlap、分区等多种组织手段。实际硬件剩余必须是在**上述最佳合法软件之后**仍存在的服务时间或资源争用，而不是低batch GPU利用率低的表象。

## 4. 因果可辨识性矩阵：为什么现在无法宣布资源瓶颈？

| 需要区分的解释 | 若成立应具有的有条件现象（未来检验标准，不是本次证据） | M/C16当前实际证据 | 当前判定 |
|---|---|---|---|
| S0：提交/分组摊销主导 | 固定32结构总量下，时间随批次数大体同比减少；其残余随每批真实工作增加产生非线性 | M确实近比例，G4/G8相对朴素比例**分别多4.04%/16.76%时间**，不能将其反推为纯launch | `PLAUSIBLE_NOT_UNIQUELY_PROVEN` |
| S1：形状/算子选择与额外流量 | 同编译产物内核路线、图规模/边分布或reduction变化可带来额外work/time，甚至策略交叉 | M每调用大小与图构建路径变；C16 Split8多CTA也多归约/流量 | `CONFOUNDER_PRESENT` |
| H1：独立ready任务供给不足（SM/SMEM/register） | 在软件调用开销与kernel形状已控制后，能独立看到active-ready服务不足、有效resident CTA/warp及其对**单独的资源改变**的wall响应 | M无grid/ready-counter的可归因独立资源干预；C16 CTA数随算法变 | `NOT_IDENTIFIED` |
| H2：片上/全局访存服务饱和 | 固定同一语义/后端与工作量条件，资源服务时延/流量与执行wall可分辨，资源能力有独立可控轴 | M无DRAM/L2/SM容量的资源缩放；C16已有L2 hit/DRAM bytes，但不同split更改工作/表示 | `NOT_IDENTIFIED` |
| H3：CPU/GPU图准备与异步交接 | 原生完整wall与分阶段wall同一时钟/界限；相同batch比CPU/GPU并包括传输及host工作，能解释主要差异 | M C2/G2已比较，但C4/C8缺席，事后诊断不与主wall可加 | `PARTIAL_SOFTWARE_RESPONSE` |

**两个不同的资源函数不能混写**。对同一工作量W与硬件资源R，固定某个已合法软件策略S₀时的`T(W,R,S₀)`，不同于允许每个R上重新择优完整强软件策略后的`T_best(W,R)=min_{S∈Legal(W,R)} T(W,R,S)`。只有前者有意义地解释固定策略的资源灵敏度，后者才描述**强软件后硬件收益**的更公平前沿。M和C16目前均没有一组合法的多R值，无法计算任一硬件响应曲线；单张4080改B、SM mask或更换GPU型号均不能自动替代严格的单变量物理扩容。

## 5. 唯一保留问题卡 Q-A12-01（不发实验）

**标题：强软件任务组织选优后，是否仍存在可归因于单一物理资源的工作量规模转折？**

- **科学对象**：P01的任务粒度/调用摊销规律，尝试在具备足够source和模型资格时检查其是否转为P13的physical-resource敏感性。当前具体native锚点是M固定Si/OAM-S；C16 W4 Split-K仅作跨负载反例，不能作为同一个matched hardware-baseline。
- **可证伪H₀（软件解释）**：随着B或算法拆分变化，至少大部分wall收益由已实施的软件提交数量、算子形状、数据准备、归约/搬运与软件资源争用解释；强软件下不需要提出新的硬件机制。其**精确等比版本**已经被G4/G8的4%/16.8%参照残差否定，但“软件/shape解释族”仍可解释这些偏差。
- **备选H₁（硬件剩余）**：在同输入/模型/精度、同数学计算与同强软件可选集条件下，即使从host launch、准备及算法额外代价隔离出来，完整wall仍对某个实际可控的**单一硬件资源R**有显著且一致的灵敏度；并需独立样本支持，而非观察低active warp%后直接假定可线性提升。
- **必要可观察指标（未来条件，不是本轮实测）**：完整未插桩wall，实际单次kernel/grid及CUDA提交数/host时间、准备/传输真实时间、相同有效输出的计算及读写量、SM ready/resident与stall服务、一个可证实只改变R的受控反事实；若为软件编译路径重排/混合调度，还需符合近邻强基线。
- **分层最低验证，不自动执行**：
  1. `GATE_SW`：先补同一个成熟后端的合法强软件规模点/匹配CPU-B4/B8或可验证的提交成本控制，保持原32结构和能量/力/应力。**这只能回答强软件是否解释效果**，单纯增加CPU点本身仍不是硬件因果。
  2. `GATE_R`：只有发现真正的残余、目标应用仍显著、且存在已校准/已资格化的**单一SM、L2/内存服务、register/SMEM资源轴**，才定义新的硬件反事实；任何模拟器必须对编译OEQ/ALCHEMI的执行语义、指令和平台验证一致，不能直接用AWMA TLB模拟10/80模型或借Kitsune A100模拟数字充当4080。
  3. `GATE_VALIDATION`：真实不同自然输入或独立模型/算子族的保留样本**另行资格化且未碰holdout**；对照最好合法软件策略，显式报告物理资源成本/面积/能耗、退化与局限。没通过软件/资源/身份任一门就`STOP`，不投入新机制。
- **关键最近邻及反例**：M GPU G2慢于C2；C16 Split8到M64反转；NanoFlow拆粒度但顺序执行反而减速；MPK持久异构SM任务；Bullet已做SM配额动态划分；Tawa/Twill对register/SMEM流水深度的强实现。
- **当前裁决**：`Q_A12_01_PARKED_RESOURCE_AXIS_NOT_IDENTIFIABLE`。在现有四点M+八点C16下，不具备单变量物理资源R、完整强软件B2/B4/B8前沿或跨负载统一工作分母。**明确0项新109 GPU、174 simulator、profile、训练或机制授权**，也不要求先“用最少预算再跑几个点”。当前保留的是科学问题，**不是可交Codex的Goal**。

## 6. 本轮最终科研收敛及下一步

1. **保留已证P01现象**：M为合法完整energy/force/stress、固定32帧的原生软件批量响应；C16为W4 Split-K局部算子规模策略反转，二者均适用于各自固定科学对象。不能凭一次加速得到`P13_SM_OR_CACHE_BOTTLENECK`。
2. **不继续扩NequIP batch寻正**：G8已优于G2，但缺C4/C8强软件比较，也缺跨模型/连续MD时间身份。若仅为了再得到一个更大数字投入GPU，无法解决硬件因果，暂不授权。
3. **训练T线保持源审STOP**：现有TorchTitan SAC/offload/paged stash能力属强近邻，当前尚无真实token身份+单卡合法整步pair。不要把作者8×H100原生前沿转成109单GPU性能。
4. **外部资源研究的优先级**：相比重复小结构batch，`Tawa/Twill寄存器-异步流水深度`和`MPK每线程最大任务register footprint`是真正显式与硬件有限资源相关的近邻。但作者已提供强软件机制，**仍必须先找一个独立实测的剩余瓶颈**，不能声称这个方向是新发现或立刻做硬件。

### 建议Round A13｜强软件后的片上状态寿命与资源因果缺口定点精读

**执行者：ChatGPT／AI-ARCH Discovery；不新增Codex/GPU任务。**

- **为何**：A12已用原生数据足以关闭从M批量曲线直接产生硬件机制的捷径。要寻找P13本身的物理资源候选，先审真实SMEM/register生命周期是否仍是强软件可规避之外的时间成本。
- **怎么做**：只对照Tawa`2510.14719v2 §V-E`、Twill`2512.18134v1 §6.3`和MPK`OSDI26 §5.3/7`三处已选实验/资源说明，逐组核模型、输入形状、真实GPU/模拟等级、所变资源与保持不变的轴、强对照、数值/退化及与本地平台的可移植性。不要重新泛搜GPU论文。
- **交付**：一张强近邻反证矩阵，最多一张可证伪`ready-data lifetime × registers/SMEM`问题卡；若真实资源可辨识性不足就标`PARKED`并更换方向，不因为A12报告形成候选就自动立项。
- **STOP/资源**：当前仅本ChatGPT原文/GitHub源码只读；0新增109 GPU/174模拟器、0模型下载、0新holdout、0新Codex、0 AWMA/C16复活。需要新原生资源扰动必须另立受限Goal并由用户明示批准。

**最终状态：`ROUND_A12_P01_ACCEPTED_SOFTWARE_ORGANIZATION_PATTERN / P13_NOT_IDENTIFIED / NO_NEW_NATIVE_OR_MECHANISM_ADMISSION`。**
