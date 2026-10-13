# Round A13｜寄存器/共享存储状态寿命与软件流水瓶颈：Tawa、Twill、MPK原始实验组定点反证

**执行者：ChatGPT／AI-ARCH Discovery，日期：2026-10-13。**  
**工作方式：** 按用户偏好，把与A12直接连续的ChatGPT-only轻量文献/source环节在本次统一完成。只读论文指定arXiv HTML版本、USENIX正式入口、NVIDIA官方PTX说明及此前[Round A2原始实验组审查](AI_ARCH_P01_P13_ROUND_A2_EXECUTION_RESOURCE_BOUNDARIES_2026-10-13_V1.md)。没有实际CUDA/RTx4080/174模拟器、没有申请多卡、没有下载模型、没有Codex任务。  
**科学裁决：`P13_EXTERNAL_ONCHIP_RESOURCE_CONSTRAINT_EVIDENCED_WITH_SCOPE / SOFTWARE_NEAREST_NEIGHBOR_STRONG / NO_NEW_LOCAL_HARDWARE_RESIDUAL_QUALIFIED`。** 仅保留一张条件性的`Q-A13-01`问题卡，状态`PARKED_NEEDS_NATIVE_RESIDUAL_AND_PLATFORM`。

## 0. 固定原文与审读程度

1. [Tawa: Automatic Warp Specialization for Modern GPUs with Asynchronous References, arXiv:2510.14719v2](https://arxiv.org/html/2510.14719v2)；本轮直接核§IV-A/B、§V-A/B、§V-E/F，对Fig.11作者直接文字的趋势，不从图片颜色条捏造缺失的精确性能点。平台H100 SXM5 80GB、CUDA12.7，25次warmup/1000次测量；来源为作者**真实H100局部kernel benchmark**。
2. [Twill: Optimal Software Pipelining and Warp Specialization for Tensor Core GPUs, arXiv:2512.18134v1](https://arxiv.org/html/2512.18134v1)；本轮直接核§5.4、§6.1与§6.3.1–2，对Fig.10/11不从曲线捏造数值。作者平台H100 SXM5 80GB、B200 180GB、CUDA13；计算优化是作者实现的真实局部attention kernel与离线solver，不是完整AI训练过程。
3. [MPK: A Compiler and Runtime for Mega-Kernelizing Tensor Programs, arXiv:2512.22219v2](https://arxiv.org/html/2512.22219v2)及[OSDI 2026正式出版入口](https://www.usenix.org/conference/osdi26/presentation/cheng)；本轮直接核§5.1–5.3、§6.2–6.6、§7。系统实验为作者**A100/H100/B200真实离线LLM推理**，per-thread寄存器固定最大任务需求为**讨论段软件/编译约束**，不是已独立测量的寄存器墙或area收益。
4. [NVIDIA PTX ISA：`setmaxnreg`](https://docs.nvidia.com/cuda/parallel-thread-execution/#miscellaneous-instructions-setmaxnreg)，直接核官方指令语义、每CTA寄存器池、目标架构范围；该规范证明**既有硬件编程能力**，不是本机执行或MPK已经应用此指令的证明。
5. 已接受[A12任务粒度与资源准入审查](AI_ARCH_ROUND_A12_CROSS_WORKLOAD_GRAIN_RESOURCE_IDENTIFIABILITY_2026-10-13_V1.md)：RTX4080 NequIP只证明本地软件批次响应，C16 W4 Split-K只证明局部策略反转；在本轮仅作交叉辨别，不提升为同一寄存器实验。

分类：`PAPER_AUTHOR_NATIVE_LOCAL`、`PAPER_AUTHOR_NATIVE_SYSTEM`、`PAPER_AUTHOR_CAUSAL_EXPLANATION`、`SOURCE_OR_SPEC_CONFIRMED`及`OUR_HYPOTHESIS`分开，不将作者原始kernel benchmark冒充我方109测量，不将编译器约束自动推算为物理扩容收益。

## 1. 三个实际原文实验/能力组：谁调整了什么？

| 实验/能力组 | 研究问题与真实输入/平台 | 受控变量和已有强软件 | 证据和必要限制 |
|---|---|---|---|
| **Tawa T-E：Fig.11／§V-E** | GEMM，§V-B设M=N=8192并扫K，§V-E选择K=16384；H100 SXM5，FP16/FP8系列（Fig.11具体面板的精度以图为准，本轮不从图像单点读取）。矩阵元素来源、随机seed、数值参考的完整轨迹未在所核段落逐项固定 | 在Tawa生成的warp-specialized路径内改变SMEM阶段缓冲数**D**和WGMMA重叠深度**P**，合法区间D≥P；另分persistent与nonpersistent。§V-B强近邻cuBLAS、TileLang、ThunderKittens，**§V-E因果组内不是用弱Triton单点推硬件** | 作者文字：D增大有助TMA预取但增加SMEM；P从1到2通常正，P=3时活跃fragment/accumulator寄存器及SMEM负担使WG occupancy和吞吐下降；persistent多数合法点快约5–10%。**这是真实kernel策略/资源配额组合的性能响应，不是增加物理寄存器或SMEM容量的单变量实验**。 |
| **Twill W-H：Fig.10／§6.3.1 Hopper backward** | FP16非causal FMHA backward，B=4、32 heads、head dim128，序列长度扫描，H100 SXM5，CUDA13。使用FA3所采用的**单pass backward**（5 GEMM＋exp＋atomic reduction），避免Triton tutorial两pass弱算法 | 联合求解SWP/warp specialization，受寄存器及依赖约束，和FA3、cuDNN及合理Triton/CUDA版本比；该组没有改变物理RF容量 | 作者报告solver用88s发现与FA3一致的**仅迭代内ILP**，跨迭代ILP因register容量不可行；但FA3在L=16384时仍比作者实现快约11%，作者把一部分归到FA3更好的80×128 tile；Twill本身**不自动选tile**。只能声称**给定tile、solver模型和寄存器约束内**的调度限制，不能称已证明整个FlashAttention性能/硬件设计最优。 |
| **Twill W-B：Fig.11／§6.3.2 Blackwell backward** | 同类FP16非causal backward，B4、32heads、dim128；B200 180GB，CUDA13；与FA4和作者CUDA翻译对照 | 原solver找到2个warpgroup ping-pong方案；该方案静态寄存器预算理论可行，但**ptxas实际分配时spill**；降低每线程reg预算并重解后得到3 warpgroup、符合FA4的方案 | 作者说明与FA4的性能差距小，Blackwell下single-pass backward受**global atomic reduction completion/bandwidth**影响；这构成重要反例：即使register问题改善，也不代表完整时间继续随寄存器提高。另有编译器抽象→ptxas register allocation落地差距。 |
| **MPK M-R：§5.3及§7** | A100/H100/B200五个LLM的作者原生离线batched推理，提示64／输出1024 tokens，B1–16；BF16强基线vLLM/SGLang。真实自然请求到达/公开token IDs非该组资格 | 持久mega-kernel以SM worker和scheduler执行tGraph/JIT/AOT任务；**SMEM分页按task acquire/release**，减少跨任务准备等待；**寄存器每线程静态占用等于各任务类型最大值** | 这是作者明确承认的软件/运行态结构约束，**未在§7测量若只消除此寄存器最大值造成多少wall或occupancy**，没有真实可实现的动态RF消除oracle，也不等于所有SM资源始终按各task峰值相加预留。 |

论文数据/数值标注：Tawa/Twill本轮是具有明确规格的benchmark或kernel微基准，未复核其矩阵内容生成器/seed，不称自然完整模型输入；MPK主组是作者真实LLM执行、固定离线长度，却没有将具体input token bank作为本轮已验证资产。三个group的**结果分母不同**：TFLOPs/s、kernel time、整迭代/服务时间；不可把它们的speedup相乘或拿来给4080定量预测。

## 2. 更严格的“强软件已做什么”反证

### 2.1 Tawa不只是曝光SMEM容量，软件已主动改变寄存器/warp组织

- §IV-A使用**cooperative compute warp groups**共享计算，使更多consumer warps共同承担更大tile，缓解单warpgroup有限register预算；§IV-B使用persistent CTA减少relaunch和波尾。
- §V-F作者报告同tile从普通实现转warp-specialization已有显著收益，配合更大tile又变化；所以“流水深度不够”不能独立解释所有指标。若想做新机制，必须和**已优化的D/P、tile、warpgroup分配、persistent选择**比较。
- `D`增加既允许更深预取，也增大SMEM占用；`P`增加既带来更多在飞计算，也增加live register，不是只增加可用硬件资源。

### 2.2 Twill已求出给定约束下接近FA3/FA4的策略，但“最优”有范围

- Solver给定的register/liveness/warp assignment约束下找到可行/最优软件调度；**Tile shape仍人工选择**，真实ptxas甚至可能对理论可行的寄存器预算产生spill。
- Hopper作者没有因此测过扩大物理register file后的运行时间；Blackwell原文明确提示atomic reduction可能成为下一瓶颈。**“register约束阻碍软件调度”与“增加物理寄存器容量一定加速”是不同命题。**

### 2.3 MPK已将共享存储资源按任务动态分页，不能重复申请宽泛“任务间共享SMEM”创新

MPK§5.3的每task acquire/release页加cross-task pipelining已存在。其§7明确**每线程寄存器占用按最大任务类型固定**，看起来可能造成轻任务的物理SM驻留受限制；但只有这个源码约束，尚无最大任务与轻任务交错、并发CTA、实际寄存器占用/溢出和完整系统wall的对照实验。若改成多个不同register footprint的megakernel，又会重新引入kernel边界、事件交接与吞吐失衡成本，不能被视作免费的等价替代。

## 3. 重要补充：Hopper/Blackwell已有`setmaxnreg`，RTX4080 SM89不支持

NVIDIA官方PTX明确已有：
`setmaxnreg.{inc,dec}.sync.aligned.u32`，允许warpgroup通过**每CTA寄存器池**归还或申请每线程register配额；`.inc`不足时会阻塞，每warpgroup全部warps应一致执行并正确同步。目标至少`sm_90a`以及列明的若干SM100/110/120架构变体；**没有`sm_89`**。

因此：
- **不能在Hopper研究中宣称“GPU没有动态寄存器分配能力”。** 任何task-phase寄存器生命期机制都必须先和`setmaxnreg`/现有CUTLASS/FA3角色再分配比较，或证明差异是**CTA间驻留/跨SM/持久不同任务类型的launch-static寄存器约束**而非CTA内部角色重新分配。
- 每CTA池内重新分配的总额不等于真实扩SM物理寄存器文件，也不等于凭空提升CTA间occupancy；指令含阻塞/同步、正确性及成本。
- 目标本地RTX4080**SM89**不能直接运行这些`sm_90a`限定的指令或TMA/WGMMA路径。即使未来有109替代源代码的局部对照，也不能称为Tawa/Twill的同架构原位复现。本轮没有新H100/B200授权或多卡资产资格。

这条硬件最近邻是**否定新颖性过度主张的重要证据**；不代表MPK已经实际实现`setmaxnreg`，后者需核代码方可判断。

## 4. 单一P13候选Q-A13-01：持久异构任务的寄存器“静态峰值”是否带来不可被软件重选吸收的真实时间？

**`Q-A13-01 / PARKED_NEEDS_NATIVE_RESIDUAL_AND_PLATFORM`。**

- **精确假设H₁（尚未成立）**：在同一真实LLM请求流、同一合法SM级task执行方案下，不同任务类型的register峰值明显分离，且因为全mega-kernel静态每线程max分配，lighter tasks长期占有本可转化为真实有效SM并发的空间；相对**已有paged-SMEM、角色内`setmaxnreg`、kernel/任务分组及强库**仍存在不可忽略的完整wall损失。
- **主要反证H₀**：轻/重task根本不同时占用大量SM时，寄存器差不影响关键路径；strong compiler改变任务分组/warp数或采用`setmaxnreg`即可缓解；持久kernel节约的launch/跨operator pipeline时间比静态register浪费更重要；或者瓶颈已经转到图调度、SMEM、原子归约或访存。
- **所需最低数据**：同一执行trace中per-task register footprint与live时间、CTA/SM驻留与ready队列长度、编译器spill/occupancy、真实内存服务及**完整请求wall**；不同策略的相同模型/token/精度/正确性与最强kernel选择。没有register峰值真实导致长时间轻任务被阻塞的**实测**，就不能预测硬件收益。
- **更高一级资源反事实**：在功能一致、可审计的编译器/模拟器上只修改物理register可用容量或task-specific allocation限制，保留调度、SMEM、数据和其它资源参数；测wall、area/power/cycle、退化。若只改每thread编译limit或launch occupancy，可能同时改变spill与kernel，必须明确它是**软件/编译器敏感性**，不是一片新硅片资源扩展。
- **状态门槛/STOP**：目前只有MPK源级结构限制＋Tawa/Twill作者外部真实局部资源耦合。没有MPK按task register差异的已测独立wall，也没有SM90平台可用的合格资源对照；故**不创建GPU Goal、不启动模拟器、不提出新硬件机制**。不以人为弱persistent kernel造出正面。
- **最近邻比照**：MPK原生paged SMEM+SM task，Tawa cooperative WGs/persistent，Twill求解器在register约束下优化，NVIDIA`setmaxnreg`支持CTA内重分配。研究命名不能暗示这些功能尚不存在。

## 5. 本轮对A12与下一步的增量

- **新增外部明确约束证据**：Tawa的D/P有界tradeoff、Twill Hopper跨iteration ILP在register限制下不可行、Twill B200 ptxas spill与原子归约下一个瓶颈、MPK`per-thread max of task types`。
- **新增重要新颖性反证**：CTA内部register pool动态分配已经有PTX支持，但Ada SM89不支持；不能简单提出“新动态寄存器管理”并把Hopper已有能力漏掉。
- **本地实验证据没有升级**：Lane M NequIP软件B组织响应仍`ACCEPT_SCOPED_NATIVE_MIXED_RESPONSE`；C16 SplitK局部规模交叉仍是软件策略收益；本轮没有新P13物理资源量化。
- **训练Lane T**当前仍`NO_VALID_SMALL_TRAINING_PAIR`，无新的训练资源授权；C16/AWMA原STOP均不改变。

### 后续Round A14建议｜平台可实现性与有论文价值的资源问题筛选

**执行者：ChatGPT／AI-ARCH Discovery；仍只读，0 GPU和模拟器。**

优先检查是否有**SM89可用且包含真实输入、强软件同语义对照**的资源瓶颈候选，而不是把SM90限定的TMA/WGMMA/动态寄存器设施硬移到RTX4080。候选最多两项：从已接受C16/非LLM原生结果和其它公开AI应用中找到**物理资源单因子可辨识**的对象，先用代码/论文本身排除纯编译与任务组织替代解释；若没有则把`P13_RESOURCE_AXIS_UNOBSERVABLE_ON_CURRENT_PLATFORM`作为阶段决策，考虑更适合的模拟或多卡/Hopper平台需要单独项目授权。不能为了得到正数又重启NequIP的batch扩展或把AWMA translation模拟直接当真实SM89硬件。

**STOP/资源**：本ChatGPT GitHub/官方论文只读，0新增109 GPU、174模拟器、164大文件访问、模型下载/训练、Codex Goal/holdout。新授权必须另立严格科学合同。

**A13最终科学标签：`EXTERNAL_REGISTER_SMEM_LIFETIME_CONSTRAINT_CONFIRMED_WITH_SCOPE / CTA_DYNAMIC_REG_REAL_NEAREST_NEIGHBOR / LOCAL_P13_MECHANISM_NOT_QUALIFIED`。**
