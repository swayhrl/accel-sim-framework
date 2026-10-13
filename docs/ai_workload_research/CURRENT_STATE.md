# AI-ARCH｜当前科研协调状态

**快照日期：2026-10-13。执行者：ChatGPT／AI-ARCH Discovery。**

这是GitHub已发布科研结果的导航，不是节点进程监控，也不是GPU执行授权。AI-ARCH本窗口负责Discovery及总体协调；AWMA由原独立主窗口管理；C16为历史证据。方法遵循[协调协议](COORDINATION_PROTOCOL.md)、[问题图谱](AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md)及[证据索引](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)。

## 当前获准：Round A16｜Lane M最小NequIP Green Context API与数值资格canary

**执行者：Codex Lane M／109（仍需用户向Codex窗口发送Goal）；设计审查者：ChatGPT／AI-ARCH Discovery。** 用户已回复“同意”上一轮提出的低成本API与数值canary方案；**只允许本次一档SM配额的受控API/数值资格，没有正式性能采样或新机制。**

- [**唯一Goal V1**](goals/AI_ARCH_A16_NEQUIP_GREEN_CONTEXT_109_CANARY_V1.md)、[固定用户同意与自限预算记录](goals/AI_ARCH_A16_NEQUIP_GREEN_CONTEXT_109_CANARY_V1_APPROVAL_2026-10-13.md)。对象仅原已审NequIP OAM-S/Si canary帧0与109、同AOT SHA、原FP32 model_dtype与FP64辅助常量、5次均值`atol=rtol=5e-5`，不重新下载/编译模型。
- GPU硬上限**10分钟非阻塞共享锁、4GiB显存、12GiB RAM/4 CPU worker、512MiB本地增量、0模型/依赖下载**；锁忙立即DEFER。只用109 RTX4080，限制**一档约半数合法SM资源**、一个绿流小kernel及条件性两帧数值canary。任何不合平台/兼容/身份、无法证明stream所有权或改变软件行为必须STOP。
- 逐门：`G1 CUDA12.6 Green API + actualSM`→`G2 自有绿流kernel及结果`→`G3 torch2.10/OEQ/ALCHEMI/AOT stream集成`→`G4 原模型数值`。**有条件地执行G4；若G3不可证明则直接STOP，不能把Driver API通过写成真实全模型SM quota通过。**
- 建立单独`hrl/aiarch-a16-nequip-greencontext-109-v1`分支和新worktree，不修改旧Lane M V1R1结果`1f69559d…`、其AOT/env/cache，以及C16/AWMA与174 Lane T/N。
- **状态：`USER_APPROVED_NARROW_API_NUMERIC_SCOPE / PREPARED_AWAITING_CODEX_LAUNCH / NO_NATIVE_RESULT`**。ChatGPT只做GitHub准备，没有连接109启动实际CUDA/Goal。
- 最新已接收A15源结论仍是`CUDA12.6_DRIVER_API_EXISTS / Torch210_CUDA126_INTEGRATION_NOT_QUALIFIED`，A16真正新增的证据应来自固定执行receipt；用户没有授权SM quota性能曲线、NCU/NSYS、Qwen模型或新P13机制。

**以下A15及更早轮次为历史已接受结论；不因本次批准被修改。**

## 最新已审：Round A15｜CUDA12.6底层Green Context与PyTorch2.10源码接口闭环

**执行者：ChatGPT／AI-ARCH Discovery；连续source-only（与A14同轮窗口完成，无设备执行）。** [Round A15固定源码接口核查](literature/AI_ARCH_ROUND_A15_GREEN_CONTEXT_CU126_SOURCE_INTERFACE_CLOSURE_2026-10-13_V1.md)。

- NVIDIA **CUDA12.6.0 Driver API**文档已经包含Green Context资源split/create及相关stream API，对8.x明确最小分区量级；不能从现代PyTorch的CUDA>=12.8便利封装推出“底层12.6完全没有”。
- 原109已接受PyTorch**2.10.0+cu126**的固定[`torch/cuda/green_contexts.py@v2.10.0`](https://github.com/pytorch/pytorch/blob/v2.10.0/torch/cuda/green_contexts.py)源码**确实已有条件性Python shim**：仅当`torch._C._CUDAGreenContext`存在才`SUPPORTED=True`；这是早期`GreenContext.create/set_context`接口，**不是**当前PyTorch文档中的`GreenContext(...).Stream()`包装。当前109 wheel是否编译启用、具体driver能否申请SM分区，均**没有实际查询**。
- `torch.cuda.ExternalStream`在v2.10.0也存在，但其合法接管NequIP AOTInductor、OEQ、ALCHEMI和跨流事件/allocator语义仍不合格；不能只因Python API可调用就把旧V1R1观测升级为SM敏感性实验。
- **最终`SOURCE_FEASIBILITY_COMPLETE / NO_NATIVE_ADMISSION`**。A14的C14-01（已有原生Si模型）与C14-02（Qwen0.5B自然模型候选）均PARKED；后续如需真正新结果，必须先独立批准对象/授权GPU小型API与数值canary或新的模型/输入资格，不再重复无限源码版本搜索。
- Lane M、T、N继续原STOP；旧V1、C16/AWMA和GPU共享锁边界不变，0新GPU/模拟器/训练/权重下载。

**下面A14及更早结论为已接受历史来源，不自动启动任何新任务。**

## 历史已审：Round A14｜SM89资源旋钮与负载可行性筛选

**执行者：ChatGPT／AI-ARCH Discovery；全部GitHub与作者/NVIDIA官方文档只读。** [**Round A14完整报告**](literature/AI_ARCH_ROUND_A14_SM89_RESOURCE_AXIS_AND_WORKLOAD_FEASIBILITY_2026-10-13_V1.md)。**没有GPU、模拟器、模型下载或新Codex执行。**

- **找到可研究的资源API，但不是已证明本机工作**：官方CUDA Green Contexts支持给执行流分配SM集合/配额，可在功能保持时测试减少可用SM后的响应。它不会增加物理SM，也会捆绑变化SM附带register/SMEM/算力，L2和DRAM仍共享；不能假装是“只加寄存器”或从少SM线性预测新GPU。PyTorch GreenContext封装要求CUDA≥12.8，与已审109原A9环境的torch2.10+cu126不匹配，兼容与stream执行资格仍未确认。
- **Ada正式能力**：SM89每SM64K×32位寄存器、100KiB共享存储最大容量、128KiB统一L1/shared data cache；`cudaFuncAttributePreferredSharedMemoryCarveout`为L1/SMEM容量互换的**提示**，并非单独增加物理Cache或SMEM，必须核真实配置才是有效对照；SM90限定的TMA/WGMMA/`setmaxnreg`不适用于SM89，但8.x仍有基本异步copy能力。
- **C14-01**：原生已接受的OAM-S 32帧/完整energy-force-stress作为低成本真实输入锚点，旧109结果仍限定`ACCEPT_SCOPED_NATIVE_MIXED_RESPONSE`。其GreenCtx quota接管AOT/OEQ/ALCHEMI整路径未合格、SM受限残余未见，`PARKED_LOW_HEADROOM`。
- **C14-02**：[Qwen2.5-0.5B-Instruct模型页](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)（24层/14Q2KV/BF16/head64）+官方支持Ada的FlashAttention2/SDPA，可作为实际边缘LLM规模候选。但**完整权重SHA、自然token bank、目标执行后端和109整请求正确性均未资格化**；`PARKED_IDENTITY_AND_PLATFORM`，不是下载/执行授权。
- **C16 Grouped W4 Split-K**旧P01规模反转属额外算术/CTA/reduction的软件组织响应，不经本轮升级为P13新机制。所有固定Lane M、T、N旧STOP以及C16/AWMA原权威不变。
- **科学结论：`API_LEVEL_SM_QUOTA_PATH_FOUND / TWO_CANDIDATES_SCREENED / P13_HARDWARE_RESIDUAL_NOT_ESTABLISHED / ZERO_NATIVE_ADMISSION`。**
- **后续Round A15建议（执行者：ChatGPT／AI-ARCH Discovery）**：只读核低层Green Context driver合约与现有PyTorch/cu126集成断层、强后端实际stream要求，先选一个科学对象；任何109实机API查询/性能、版本升级、权重下载、NCU/模拟器或holdout均须重新明示预算与授权，不能自行启动。

**下面Round A13及更早轮次为历史已接受结果/旧提议，不构成新执行许可。**

## 历史已审：Round A13｜片上状态寿命与寄存器资源最近邻审查

**执行者：ChatGPT／AI-ARCH Discovery，连续source/literature-only（未启动Codex/GPU/模拟器）。** [**Round A13原始论文/官方PTX定点审查**](literature/AI_ARCH_ROUND_A13_ONCHIP_STATE_LIFETIME_STRONG_SOFTWARE_CAUSAL_AUDIT_2026-10-13_V1.md)。与A12使用相同窗口连续完成，以减少纯ChatGPT阶段的重复审批。

- **Tawa** H100真实GEMM（K=16384）§V-E：aref的SMEM buffer深度D与WGMMA pipeline深度P（D≥P）形成tradeoff；P1→2通常改善、P3因register/SMEM/liveness引起occupancy/吞吐退化。作者已经使用cooperative warpgroup、persistent和强cuBLAS/FA3对照，不是新的空白。
- **Twill** H100/B200真实FMHA backward：Hopper给定tile+register限制下不支持跨iteration的更深ILP，solver重获FA3类似策略；B200理论可行的两warpgroup方案在ptxas下spill，减register budget后得到三warpgroup、接近FA4方案，但作者同时指出atomic reduction/bandwidth会成为后续瓶颈。属于作者有范围软件/硬件约束，不是寄存器扩容实测加速。
- **MPK** OSDI26真实LLM离线推理与源描述：SM级任务/事件调度、**paged SMEM已按task生灭重用**；per-thread寄存器仍按mega-kernel中最大task需求静态占用。**没有直接报告“只去掉reg最大值”能提升完整wall多少**。
- **硬件重要反证**：[NVIDIA官方PTX `setmaxnreg`](https://docs.nvidia.com/cuda/parallel-thread-execution/#miscellaneous-instructions-setmaxnreg)可在**SM90a及部分更新架构**的每CTA register池中动态调节warpgroup配额；**SM89/RTX4080不支持**。不能把“任何GPU缺少动态寄存器再分配”作为新机制，也不能把CTA内重新分配当作物理扩容/提高CTA级occupancy。
- **唯一`Q-A13-01`**：MPK持久异构task的最大寄存器需求是否在已有paged SMEM/动态CTA内reg重分配/强软件重选后，仍造成真实可量化的轻任务占用及完整wall损失？`PARKED_NEEDS_NATIVE_RESIDUAL_AND_PLATFORM`，当前只有结构限制+外部局部kernel资源权衡，没有该对象真实剩余墙或合格SM90对照，**不准入硬件机制、新GPU或模拟器任务**。
- **后续Round A14建议（执行者：ChatGPT／AI-ARCH Discovery）**：只读筛选SM89本地真正可运行、强软件之后仍有物理单变量资源可辨识的候选；若无则停止当前平台P13实证路线并重新评估独立Hopper/仿真资源资格，而不是再扩大NequIP batch或重启C16/AWMA。
- Lane M（109）、T（174-new）、N（174-new）继续STOP；原V1/Stage A/R27R3权威不改；0新109 GPU、174模拟器、164大raw、Codex/模型下载、holdout。

**以下Round A12及之前记录是有范围历史接受事实，而非新项目执行授权。**

## 历史已审：Round A12｜跨负载任务粒度与硬件资源可辨识性

**执行者：ChatGPT／AI-ARCH Discovery（GitHub source/literature-only，无Codex/GPU）。** [**Round A12固定研究报告**](literature/AI_ARCH_ROUND_A12_CROSS_WORKLOAD_GRAIN_RESOURCE_IDENTIFIABILITY_2026-10-13_V1.md)。

- **P01有限成立**：Lane M `1f69559d…`的RTX4080/OAM-S真实32帧，CPU B2=20.758ms、GPU B2/4/8=26.044/13.548/7.602ms；软件组织与批次数选择对完整energy/force/stress wall具有强响应，三进程/144样本已在A11独立复算并核数值。四臂不构成纯物理资源扫描。
- **新增`OUR_DERIVATION`，仅数学参照非硬件oracle**：保持G2每调用整组平均成本不变时，G4/G8按8/4次调用推得13.022/6.511ms，实际13.548/7.602ms（比分组比例参照分别多4.04%/16.76%）。说明改善接近批次数比例，而非出现需假设SM/Cache机制的额外收益；也不能证明全部来自CPU launch，因单次形状、图构建、模型kernel选择同时变化。
- **跨负载反例**：C16已审`a3a36e64…`的GROUPED W4 Split-K在M1/16/32使用Split8更快，M64 Split1反超4.93%；它增加CTA并产生额外reduction，与M缩减批次调用具有不同干预身份，不能拼成同一“资源扩展曲线”。
- **强近邻已审核对**：NanoFlow纳米批次异构重叠、MPK SM级持久任务、Bullet SM配额、Kitsune资源模型与Tawa/Twill SMEM/register流水均已有作者限定范围证据；**原生真实时间、局部kernel、模拟器模型和当前source检查不可混成统一实测**。
- **唯一候选`Q-A12-01`**：强软件任务组织选优后是否仍存在单一物理资源敏感的剩余wall？**`PARKED_RESOURCE_AXIS_NOT_IDENTIFIABLE`**，原因：M缺CPU B4/B8的成熟对照，M/C16均缺物理资源R的受控单因子干预、跨负载统一时间与独立样本。明确`NO_NEW_NATIVE_OR_MECHANISM_ADMISSION`，不是当前可执行Goal。
- **建议下一轮Round A13｜强软件后的片上状态寿命与资源因果缺口定点精读（执行者：ChatGPT／AI-ARCH Discovery）**：仅选Tawa§V-E、Twill§6.3、MPK§5.3/7逐实验组核register/SMEM生命周期与实际时间上限，最多一张可证伪问题卡；若最近邻覆盖充分或缺资源单变量则PARKED；0新109 GPU、174模拟器、Codex或新holdout。
- **Lane**：M／109 Round A9与T／174 Round A10均STOP、M原V1独立STOP不变；N／174旧源审STOP。C16 Stage A、AWMA科学authority及所有既有资源锁边界保持不动。本次只更新GitHub科研笔记与协调导航。

**下面Round A11及更早轮次保持为历史已审证据，而非当前待执行阶段。**

## 历史已审：Round A11｜Lane M原生结果与Lane T训练源审联合科学审查

**执行者：ChatGPT／AI-ARCH Discovery。** [固定联合独立审查](reviews/AI_ARCH_ROUND_A11_LANE_M_T_JOINT_INDEPENDENT_REVIEW_2026-10-13_V1.md)；当前两Lane均**已完成并STOP**，且没有获准执行的新109 GPU/174模拟器任务。

| Lane | 固定执行提交 | 独立科学裁决 |
|---|---|---|
| **Lane M／109，Round A9 V1R1** | [`1f69559df4f51290589de72876f36a756c5439f0`](https://github.com/swayhrl/accel-sim-framework/commit/1f69559df4f51290589de72876f36a756c5439f0) | **`ACCEPT_SCOPED_NATIVE_MIXED_RESPONSE`**。固定OAM-S模型+32 Si真实静态帧，3 fresh processes×12完整blocks=144原生wall样本，四臂均通过num/edge/compiled资格。整组中位C2/G2/G4/G8：**20.758/26.044/13.548/7.602ms**；36对block下C2→G2变慢约25.48%，GPU G2→G4/G8时间下降约48.07%/70.86%。本窗口独立复算全部144行时序/108个配对比与7个Git小文件SHA；属**软件组织响应**，不证明物理SM/Cache/带宽瓶颈。 |
| **Lane T／174-new，Round A10** | [`859eb16a51c7bf085d6e39a9000de198c0f4e710`](https://github.com/swayhrl/accel-sim-framework/commit/859eb16a51c7bf085d6e39a9000de198c0f4e710) | **`ACCEPT_SCOPED_SOURCE_ONLY_NO_VALID_SMALL_TRAINING_PAIR`**。直接源审TorchTitan GraphTrainer已有SAC、offload和MoE paged stash；当前配置C4未固定真正token bank、没有RTX4080单卡合法完整训练步的证明。不存在新training GPU Goal资格；不否定其它公开小训练模型。 |

- **Lane M现为`NATIVE_QUALIFIED / MIXED_RESPONSE / NORMAL_COMPLETION_STOP`**；原Round A8 V1 `ENVIRONMENT_BLOCKED/NOT_EVALUATED`独立终态不变。164 raw **444项**和closeout **30项**由执行者报告readback PASS；ChatGPT未SSH独立复核164实际raw，仅GitHub固定小包与原始时序复算。
- **Lane T**当前A10完成/STOP，历史A4仍STOP；原Lane P仅是尚未启动时拟议名称，新任务实际上在174复用**Lane T**执行。Lane N（174-new）旧报告完整性问题及历史STOP不变。
- **优先科研解释**：NequIP响应主要是提交粒度、构图与完整评估的**P01工作量组织**；没有可从四点直接晋升的**P13单变量物理资源扩展**。训练线有强软件近邻，不应再开发朴素offloader。
- **建议下一步Round A12｜跨负载资源约束可辨识性与候选收敛（执行者：ChatGPT／AI-ARCH Discovery）**：优先source/literature-only，利用新原生M数据与旧限定证据，给最多一项真正能区分批次摊销与硬件资源约束的候选；不自动做profiling、更多GPU、新机制或模型下载。新执行需独立合同和明确权限。

下面A10以及A9“正在执行/已批准/等待”均保留**当时快照**，最新完成状态以本段为准。

## 历史并行安排：Round A10｜训练资源生命周期源码与论文对照

**执行者：ChatGPT／AI-ARCH Discovery（原文与因果审计，已完成）；拟执行：Codex Lane P／174-new（独立CPU/source-only，尚未由用户启动）。** 109 **Lane M**的已批准V1R1由用户报告正在执行，**不干预、重启、改GPU锁或改变数据合同**。当前ChatGPT不能核验Lane M实时进程。

- [**ChatGPT本轮实际研究报告**](literature/AI_ARCH_ROUND_A10_TRAINING_RESOURCE_LIFECYCLE_NEAREST_WORK_2026-10-13_V1.md)：2026-06-23 PyTorch Graph-based CPU Offloading官方报告的8×H100真实训练实验组、2026-10-09 SlackSwap作者arXiv**摘要级**A100 trace-driven仿真、固定TorchTitan 2026-10-13 GraphTrainer source强能力与MoE paged-stash；不把文献模拟/源码升级为RTX4080性能。
- **重要近邻**：TorchTitan固定源码已有`sac_and_offload`和`sac_and_paged_stash`，后者移植Megatron-Core 0.19.0且用于静态capacity padded MoE。普通activation offload/prefetch和capacity-padded共享页本身并非待发明硬件空白。
- **P13因果要求**：同策略固定时的真实资源响应，与每一硬件点重新优化强软件之后的响应必须分开。单卡改budget/seq属于P01负载/软件变化，不是单变量扩SM/host-link实验。没有新GPU授权或硬件机制晋升。
- [**Lane P／174-new单一独立Goal**](goals/AI_ARCH_A10_TRAINING_LIFECYCLE_SOURCE_AUDIT_174NEW_V1.md)：冻结公开`pytorch/torchtitan@8a75afd90773fe410340e0709b0b1af427c4af58`，审≤10处source的训练输入、GraphTrainer lifecycle及小规模真实训练pair可行性。独立分支`hrl/aiarch-a10-training-lifecycle-source-174-v1`；**本ChatGPT未启动Codex窗口**。不得访问109 GPU或164、运行模型/模拟器、安装环境。
- 预计下一步：Lane P固定报告回来后，ChatGPT独立核其强软件/自然输入/容量准入；Lane M的V1R1结果独立审查，两线互不构成授权。若新训练pair不成立，明确STOP；不得为了多窗口并行制造实验。

**下面的A9“执行尚待窗口启动”为写入当时的审批时点，不可据此否定用户随后报告Lane M已运行。**

## 已批准的Round A9历史执行许可（批准时尚待窗口启动）

**用户2026-10-13明确批准两个阶段：A＝官方原版本ANTLR源码包的一次受控本地wheel构建；B＝仅在A以及其它已冻结依赖门合格之后，按V1原科学参数与剩余累计预算恢复109 GPU观察。** [固定审批记录](goals/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1R1_APPROVAL_2026-10-13.md)、[完整V1R1方案](goals/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1R1_WHEEL_EXCEPTION_DRAFT.md)及[原V1合同](goals/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1.md)为本次执行依据。

- 运行执行者：**Lane M／node109独立新worktree**；准备独立分支`hrl/aiarch-nequip-static-batch-109-v1r1`，起点为原V1正式STOP提交`06674a961632c107681ac146d735d932dde112d6`。原V1 STOP、原164归档及前轮资源消耗不能覆盖或清零。
- `EXPLICIT_APPROVAL_V1R1_A_AND_B / AWAITING_LANE_M_LAUNCH / V1_STOP_PRESERVED`。本ChatGPT仅记录批准与准备GitHub，**没有登录109启动Codex、安装任何wheel或初始化CUDA**。是否真的运行须依用户/执行报告。
- 唯一打包例外是官方`antlr4-python3-runtime==4.9.3`固定同一sdist SHA的一次CPU构建；不得换版本、使用第三方wheel或擅自处理第二个源码包。
- 原四条件N-C2/N-G2/N-G4/N-G8、数值/输入/强软件基线、GPU锁和STOP仍冻结；原累计依赖下载8GiB上限减前轮保守消耗3,333,112,827 bytes，**余5,256,821,765 bytes**，其它资源原V1预算不重新计起。
- Lane T、Lane N（174-new）、AWMA、C16全部继续原独立任务状态。只有具本次确切许可的Lane M能进入本轮。

下面的Round A8停止审查和更早“拟议/已启动”描述保留作为历史，不应覆盖此新批准状态。

## 最新已审：Round A8｜Lane M依赖wheel门STOP（执行者：ChatGPT独立审查）

**当前接受的科学状态：`V1_ENVIRONMENT_BLOCKED / NOT_EVALUATED / COMPLETE_STOP`。** [Round A8独立审查](reviews/AI_ARCH_ROUND_A8_LANE_M_ENV_STOP_INDEPENDENT_REVIEW_2026-10-13_V1.md)已在固定[执行提交`06674a961632c107681ac146d735d932dde112d6`](https://github.com/swayhrl/accel-sim-framework/commit/06674a961632c107681ac146d735d932dde112d6)和公开PyPI官方发行上核对停止依据。执行分支`hrl/aiarch-nequip-static-batch-109-v1`保持STOP，**不自动恢复、重启、merge或修改旧receipt**。

- 受控解析锁定82个发行包，`antlr4-python3-runtime==4.9.3`的**PyPI官方wheel缺失**触发V1预冻结wheel-only STOP；官方sdist存在且hash相符。轮子缺失不是模型加载失败，也不是Python包被证实不能安装。
- **四条件N-C2/G2/G4/G8全部0计时样本**，0正式进程、0数值/边集合/compiled资格；不能给性能排序或新硬件现象。
- 执行者报告模型/Si字节身份PASS，109 GPU锁占用/正式观察/峰值显存为0；依赖下载保守计约3.11GiB、wheel阶段RAM峰值约92.6MiB，但全部resolver阶段RAM峰值未测。164归档通过是执行侧报告；本窗口GitHub抽检5份关键文件SHA通过，不宣称现场重算164全部raw。
- [**Round A9候选V1R1合同**](goals/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1R1_WHEEL_EXCEPTION_DRAFT.md)只提出从**原官方同版本sdist**有界构建一次本地wheel并继续原参数/预算下的资格；**尚未获得新的GPU/依赖打包例外批准，未创建V1R1执行分支**。不允许换4.13、随意降低数值门或从第三方wheel补包。
- Lane M（109）现已STOP；Lane N（174-new）非LLM旧审查与Lane T（174-new）训练旧审查仍STOP。C16 Stage A、AWMA R27R3旧科学结论及独立管理边界不受本轮影响。

**下面A7/A8批准与启动段落保留为历史时点记录，其“当时待启动/已启动/待审批”状态都已经由本段A8正式STOP取代。**

## 历史授权：Round A8｜109静态结构有限观察（当时已批准、用户报告已启动）

**用户于2026-10-13在本AI-ARCH窗口明确同意A7提出的整份A8合同及资源硬预算。** [固定批准记录](goals/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1_APPROVAL_2026-10-13.md)与[科学合同V1](goals/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1.md)共同界定本轮唯一执行范围。状态：`EXPLICITLY_APPROVED / USER_REPORTED_LAUNCHED / NOT_NATIVE_VALIDATED`。用户已报告在109启动Codex并将窗口命名为**Lane M**；本窗口未直接核验node109实时任务、GPU锁或任何执行门结果。

- 执行者：**Lane M（node109，Round A8）**；原**Lane N（174-new，非LLM源审）**和**Lane T（174-new，训练源审）**继续保留原名与STOP。三个Lane名称在节点间不复用；仅命名更正，不变更科学合同或资源预算。
- 四条件N-C2/G2/G4/G8、相同32帧、单batch编译产物与完整energy/force/stress，GPU单RTX4080及既有非阻塞共享锁，依V1预冻结数值/边集合/时间统计与STOP。
- 用户批准GPU锁占用硬上限90分钟、观察阶段15分钟，模型和Si下载<=12MiB、依赖下载<=8GiB、新环境<=25GiB、CPU<=8 workers/RAM<=32GiB/GPU显存<=12GiB、raw日志<=256MiB；任何科学/资源边界变化均不得静默执行。
- **用户随后明确报告Lane M已在109启动。** 这是`USER_REPORTED_LAUNCHED`，不是本窗口已经核验运行、CUDA资格PASS、采集完成或结果有效。不得从Git HEAD推断实时GPU状态；执行合同、锁与STOP条件全部保持。

## 历史设计完成：Round A7｜非LLM发现性观察完整合同与执行前审查

**执行者：ChatGPT／AI-ARCH Discovery。连续设计阶段已一次完成；没有启动Codex或109 GPU。**

[完整合同：AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1](goals/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1.md)，初始发布提交 `8d4ed06e3696b0721b83f706b03cbc6b058f9f46`。

| 项目 | 本轮完成内容 | 当前边界 |
|---|---|---|
| 模型固定 | OAM-S:0.1；Zenodo 18775904的指定5.6MB文件与官方MD5已核，禁止注册名自动升级 | 本轮未下载包；实际SHA256/dtype/包内源码在获批后的资格门核验 |
| 输入与选样 | 固定Si文件；32个零基帧号、canary 0/109明确；所有臂相同2048原子工作量 | 静态结构评估，不声称连续MD、跨帧复用率或统计独立holdout |
| 软件/数值 | 候选PyTorch 2.10.0 cu126、固定NequIP/OEQ/ALCHEMI；FP32/TF32-off；沿官方5次均值与5e-5 allclose；边集合精确比较 | 静态接口核查通过不等于本机组合已可运行；不调容差或替换模型 |
| 四条件 | CPU构图B2；GPU构图B2/B4/B8；共用一个batch AOT产物 | 是构图放置及提交粒度研究，非物理SM/带宽扩容实验 |
| 测量/统计 | CPU常驻输入至CPU结果完整wall；3 fresh process×12完整四条件block=144样本；诊断另列 | 编译/准备一次性成本另报；不从局部event之和推全程关键路径 |
| 连续执行合同 | 从隔离环境、资格、canary、计时、自检到发布一次Goal；失败按事前规则STOP | `DESIGN_COMPLETE / GPU_APPROVAL_PENDING / NOT_NATIVE_VALIDATED`；执行分支尚未创建 |

## 历史规划：Round A8｜109静态结构有限观察（当时待明确GPU审批）

**原设计时的拟执行者标签为Codex Lane N／109；现更名为Lane M／109（用户报告已启动）；科学审查：ChatGPT／AI-ARCH Discovery。**

不是再开一轮ChatGPT方案整理。若用户批准完整合同的设备/获取/编译边界，就按该合同一次Goal完成必要资格与观察，再交本窗口独立审查。未批准之前不发送启动指令、不改变现有Lane本地工作区。

拟申请范围：固定模型＋几何合计下载<=12MiB；隔离依赖下载<=8GiB、环境/缓存/产物增量<=25GiB；CPU<=8 workers、RAM<=32GiB；单109 GPU，任务显存<=12GiB，现有共享锁独占硬上限90分钟，纯观察阶段<=15分钟。以上是预算上限，不是已用资源或完成时长预测。禁止NSYS/NCU/NVBit、训练、MD、驱动升级和新机制。

有意义结果包括软件组织收益、CPU构图更快、批量响应、零/不稳定响应；不强求5%端到端收益，不因正数自动晋升硬件。当前仍无新GPU执行授权。

## Lane与独立项目状态

| 工作线 | 固定已审来源 | 当前状态 |
|---|---|---|
| Lane T | [A4训练源审@a1a70180736499687435b1e2d99984d4ebba4c53](https://github.com/swayhrl/accel-sim-framework/blob/a1a70180736499687435b1e2d99984d4ebba4c53/docs/ai_workload_research/reviews/AI_ARCH_A4_TRAINING_SOURCE_REVIEW_174NEW_V1.md) | 原任务完成/STOP；A5接受有限未准入判断。不追加352B调查 |
| Lane N原174源审 | [V1@e355f096eeac44328d7463ef3256cc649ec9cb03](https://github.com/swayhrl/accel-sim-framework/blob/e355f096eeac44328d7463ef3256cc649ec9cb03/docs/ai_workload_research/reviews/AI_ARCH_A4_NONLLM_SOURCE_REVIEW_174NEW_V1.md) | A5确认文本丢失，整体文档仍PARTIAL；A6最后读回仍此HEAD。本轮未重读分支，不声明V2已修复或本地进程状态；修复不阻塞本窗口直接核实的源码设计 |
| C16 | [Reset@635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f](https://github.com/swayhrl/accel-sim-framework/commit/635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f)；[Stage A@ccd6928bfb420d1e4c554ec0e377bb8fbe377501](https://github.com/swayhrl/accel-sim-framework/commit/ccd6928bfb420d1e4c554ec0e377bb8fbe377501) | 历史Stage A TERMINAL_PARTIAL、Reset关闭；不恢复Observer、Tier1或旧holdout |
| AWMA R27R3 | [独立review@d6e9bbfb562814bcd5dc5adb444d3c572e7f446b](https://github.com/swayhrl/accel-sim-framework/blob/d6e9bbfb562814bcd5dc5adb444d3c572e7f446b/docs/vm_tlb/literature_notes/awma/empirical/R27R3_B0_REFERENCE_REPEATABILITY_REVIEW_2026-10-13.md)；[协调同步](R27R3_INDEPENDENT_REVIEW_SYNC_2026-10-13.md) | 保持B0_REFERENCE_NOT_REPEATABLE、COMPLETE/STOP；AWMA后续以原窗口最新已审权威为准 |
| 训练新方向 | [Round A6](literature/AI_ARCH_ROUND_A6_NEQUIP_PATH_AND_PUBLIC_TRAINING_2026-10-13_V1.md)的TorchTitan/C4、SimpleFSDP与卸载近邻 | 公开输入与软件方法研究保留，不用单卡代理冒充多GPU实验；本轮不新开训练任务 |
| AWMA其它证据 | [C16/AWMA证据索引](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md) | Pre-L1模拟、R23G局部软件、R26容量与R27R2资格失败分别保留；本窗口不改实验结论 |

## 历史轮次与证据导航

A6完整旧导航保存在[CURRENT_STATE@5fd748c3f2da64924ed84978c07bca90e7e6ea92](https://github.com/swayhrl/accel-sim-framework/blob/5fd748c3f2da64924ed84978c07bca90e7e6ea92/docs/ai_workload_research/CURRENT_STATE.md)，A1–A5旧导航保存在[CURRENT_STATE@3d0a959d3d6b77de67fdf9cc3f891d4adcc5416b](https://github.com/swayhrl/accel-sim-framework/blob/3d0a959d3d6b77de67fdf9cc3f891d4adcc5416b/docs/ai_workload_research/CURRENT_STATE.md)。导航更新不重写历史报告。

- [A1论文实验组](literature/AI_ARCH_P01_P13_EXPERIMENT_GROUP_AUDIT_2026-10-13_V1.md)；[A1资源/调度因果](literature/AI_ARCH_P01_P13_RESOURCE_MODEL_CAUSAL_READING_2026-10-13_V1.md)。
- [A2执行资源近邻](literature/AI_ARCH_P01_P13_ROUND_A2_EXECUTION_RESOURCE_BOUNDARIES_2026-10-13_V1.md)。
- [A3历史证据与准入](literature/AI_ARCH_ROUND_A3_HISTORICAL_EVIDENCE_CLOSURE_AND_CANDIDATE_ADMISSION_2026-10-13_V1.md)。
- [A4三family与并行安排](literature/AI_ARCH_ROUND_A4_NATURAL_WORKLOAD_PARALLEL_DISCOVERY_2026-10-13_V1.md)。
- [A5联合独立审查](reviews/AI_ARCH_ROUND_A5_LANE_T_N_INDEPENDENT_REVIEW_2026-10-13_V1.md)。
- [A6非LLM路径与公开训练](literature/AI_ARCH_ROUND_A6_NEQUIP_PATH_AND_PUBLIC_TRAINING_2026-10-13_V1.md)。

后续同一ChatGPT可连续完成且不依赖新外部结果的核查、设计与自审合并处理，不因轮次编号反复索要同意；实际GPU/资源授权边界仍独立。工具Skill只用方法，不安装或合并候选分支；尚未直接读取的节点raw不声称本窗口已重新验证。
