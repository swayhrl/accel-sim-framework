# Round A30N｜DiT优化后的资源配比与执行组织：174-new CPU-only Goal

**授权来源：** 用户2026-10-14明确同意[Round A29](../literature/AI_ARCH_A29_3DGS_HARDWARE_HOTSPOT_AND_PARALLEL_NON3DGS_PORTFOLIO_2026-10-14_V1.md)的T/N并行探索。**仅CPU/source/paper、最小后续实验设计得到授权**。不准入GPU、模拟器、模型运行、下载或新机制实现。

**执行者：** 新的、独立的Codex窗口／174-new，标识Lane N (A30N)；既有旧Lane N进程和STOP资产不得被接管、覆盖或重启。**Git输入固定：** `swayhrl/accel-sim-framework`，独立branch `hrl/aiarch-a30n-dit-postopt-resource-174new-v1`，起点`b806777afb33be0985ec7678e69f320578eefa43`。与Lane T完全不同worktree、output、tmp和可变状态。

## 0. 要回答的问题

**Q-A30N：** 固定实际DiT生成任务、质量要求与一个已经存在的复用/稀疏策略时，优化后产生的工作量变化是否导致GPU tile/片上存储/矩阵与非矩阵阶段组织失配？在允许现有强软件进行合法kernel选择和重映射后，有没有一个可识别、可用小型native诊断区分的剩余资源成本？

**不要**将“扩散步骤之间相似”重新包装成新跨步Cache、token skipping、attention mask reuse机制。不要因为已有缓存/稀疏论文，就预判全部DiT体系结构方向关闭；必须逐项比较已解决的能力和仍未解决的具体约束。一个明确、被强近邻覆盖的负结果，是本轮合法结论。

本轮仅挑选一个**图像DiT**具体部署作为拟定未来实验对象；视频扩散和VLA动作规划只当近邻或迁移边界，不同时搭工程。

## 1. 初始authorities与关键原文

按序阅读：`docs/ai_workload_research/CURRENT_STATE.md`、`COORDINATION_PROTOCOL.md`、`AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md`的P01/P13/P14、`docs/ai_workload_research/literature/AI_ARCH_A29_3DGS_HARDWARE_HOTSPOT_AND_PARALLEL_NON3DGS_PORTFOLIO_2026-10-14_V1.md`的``3、5、7–9``。历史C16/AWMA仅作为只读异构对照，不自动复用任何旧性能结论。

重点独立核下面的**具体实验组与能力**，最多4篇关键近邻：
- [Cambricon-D，ISCA2024／IEEE摘要](https://ieeexplore.ieee.org/abstract/document/10609724/)：差分计算、sign-mask dataflow、硬件模型/质量；若只有摘要，`ABSTRACT_ONLY`。
- [DiSC，arXiv 2605.25798](https://arxiv.org/html/2605.25798)：cached-token与attention mask复用、dense/sparse混合、bank及执行单元组织；核真实模型、输入、step区间、质量约束、模拟/RTL/native实验组。
- [DiTPA，ISCA2026作者机构记录](https://researchportal.hkust.edu.hk/en/publications/ditpa-a-dit-based-action-planner-accelerator-exploiting-action-de/)：动作用例/硬件已有能力和闭环任务质量，除非为反证必需，不展开机器人平台。
- 必要时选一个真实、可合法阅读的强DiT baseline/开源kernel仓库（固定exact commit）以及一篇最直接的2025–2026论文；不是看到最新论文就不断扩大调查数量。

按“论文版本×实际实验组×模型与checkpoint×scheduler/denoising steps×提示词/条件与seed×分辨率×质量/收敛指标×GPU/实现与dtype×控制变量×证据层级×强对照”逐项写明。作者的输入选择理由和我们归纳分列；未披露字段保持未披露，审不到正文不得制造数值。

## 2. 同一Goal连续完成G0–G4

**G0｜节点资源/隔离检查：** 在174-new独立worktree创建前确认CPU/RAM/swap/IO/overlay free以及其他长任务；仅在资源安全时开CPU/source任务，不kill旧进程或清理用户数据。与Lane T和109 Lane M可以科研并行，不能抢它们的资源。无足够余量则`RESOURCE_DEFERRED`并在本分支记录，STOP。

**G1｜近邻功能与实验级反证：** 逐组审Cambricon-D/DiSC/必要DiTPA实际改动的计算、片上状态、质量要求及成本报告。严格区分真机、架构模型、局部kernel与完整图片/视频/机器人指标；用户可复现的GPU软件路径不等于论文里的专用硬件。形成一个`ALREADY_SOLVED_VS_UNQUALIFIED`矩阵，明确哪些想法已经直接被覆盖。

**G2｜选择一条**具体可追溯的图像DiT部署**：** 优先从DiSC正文实际使用的DiT/PixArt-Sigma及其合法公开checkpoint/code确定一个研究对象，若其源/权重/完整eval入口不透明，允许选择另一篇论文里的真实开源图像DiT对象并说明理由；不能仅因本机已有模型就倒推选题。**只登记**checkpoint release/revision、合法分辨率、scheduler、步数、conditions/seed、数值和质量对照、实现/后端/最低硬件需求、原论文每个实验组的真实性；不运行模型/安装环境/下载权重。对于同shape但实际工作可能变小的假说，先核作者到底有没有稀疏比例及真实有效token变化，没核到则标`UNSUPPORTED`。

**G3｜一份最小、可证伪的未来发现实验设计：**
- 选一个固定质量目标和一个已有（而不是本项目新发明的）优化策略；设计`强dense路径 vs 同质量的已有优化路径`，至多选择3个事先确定的denoising step/层实例；如质量无法逐bit保持，必须说清是什么质量指标和容许差异，不假称算法同义。
- 同一个运行条件下区分`有用工作、实际执行tile、index/mask准备、重排和调度、寄存器/SMEM或buffer需求、整个block的未插桩时间、最终image的时间/质量`；明确哪些观测可以来自现有作者证据，哪些必须未来native/NCU才有。**不要用稀疏比例代替可实现speedup或发明已有论文没测到的瓶颈。**
- 至少列两个竞争解释：`仅软件kernel选型/数据布局导致的差异`与`确有资源组织残余`；明确一个反证。举例：若已有强kernel选优后目标区域成本消失或优化改变质量/工作量不可同义比较，则`NO_HARDWARE_PROBE_READY`。
- 规定未来实验的baseline、诊断（必要时限定source-only oracle而不模拟器）、独立验证样本及平台最低要求；不得提前把模拟器资源×2设计成必做实验。
- 提交**最多一个**有明确证据入口、输入身份与资源预算待审批的发现性probe；无合法候选就明确STOP，不为凑满两个方向制造工作。

**G4｜完整收口：** 报告作者来源与原文定位、已解决能力、一个图像DiT部署、一个资源问题/或否定原因、最小实验合同、resource receipt和所有未核的边界；只完成一次正确提交、push并从远端fetch-back exact commit/tree/blob。工程链接/索引/编码小问题本Goal自行solve-and-continue，不反复请求确认；缺实质科学来源、关键语义或越预算则STOP而不是静默改目标。

## 3. 产物、资源与严格禁令

只在本branch新增一份：

`docs/ai_workload_research/reviews/AI_ARCH_A30N_DIT_POSTOPT_RESOURCE_DISCOVERY_174NEW_V1.md`

包含`SOURCE_EXPERIMENT_MATRIX`、`NOVELTY_COLLISION`、`ONE_IMAGE_DIT_DEPLOYMENT`、`WORK_RESOURCE_HYPOTHESES`、`ONE_PROBE_OR_STOP`、`CLOSEOUT`；最多以小型报告和必要citation/源码定位完成，不开发新benchmark框架。不要写同一份`CURRENT_STATE.md`；协调主窗口随后统一审查两线结果再更新导航。

每Lane CPU≤2有效workers、maxRSS≤4GiB、新增下载与文件总≤100MiB、PDF下载总≤40MiB且单PDF≤20MiB、建议≤6小时有界STOP。条件允许且资源实际充足时T/N同时进行；不要机械排队，也不能强制占满资源。需要更高预算/另一平台时只提交科学申请，不执行。

**禁止**：Torch/CUDA import、推理/训练/denoising、模型和权重/数据/依赖下载、编译/JIT/模拟器、109/164访问、GPU锁、NCU/NSYS/NVBit、shared worktree、对其他branch和历史authority写入、旧AWMA/C16任务恢复、A26GR1干预、自动新机制开发/holdout或新增GPU任务。

最终状态取`SOURCE_QUALIFIED_PROBE_CANDIDATE`、`STRONG_PRIOR_ART_COVERS`、`DATASET_OR_PLATFORM_NOT_QUALIFIED`或`EVIDENCE_INSUFFICIENT`之一。若只完成Goal文件发布，状态仍是`A30N_AUTHORIZED_READY_FOR_CODEX`而不是已执行。