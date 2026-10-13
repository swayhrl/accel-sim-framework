# AI-ARCH｜当前科研协调状态

**快照日期：2026-10-13。执行者：ChatGPT／AI-ARCH Discovery。**

这是GitHub已发布科研结果的导航，不是节点进程监控，也不是GPU执行授权。AI-ARCH本窗口负责Discovery及总体协调；AWMA由原独立主窗口管理；C16为历史证据。方法遵循[协调协议](COORDINATION_PROTOCOL.md)、[问题图谱](AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md)及[证据索引](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)。

## 当前并行：Round A10｜训练资源生命周期源码与论文对照

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
