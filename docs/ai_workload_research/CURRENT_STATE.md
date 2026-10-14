# AI-ARCH｜当前科研协调状态

**快照日期：2026-10-14。维护者：ChatGPT／AI-ARCH Discovery。**

本页是研究导航，不是节点进程监控，也不产生GPU执行授权。AI-ARCH窗口负责Discovery及总体协调；AWMA仍由原独立主窗口管理；C16为冻结历史证据。遵循[协调协议](COORDINATION_PROTOCOL.md)、[问题图谱](AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md)及[证据索引](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)。

**历史保存：** 本次将导航收敛为最新状态。A30及全部更早轮次的完整长日志原样保存在[固定历史CURRENT_STATE@15d20bb0](https://github.com/swayhrl/accel-sim-framework/blob/15d20bb0bbf045e9dc05f2d51eecb70c9b0cfd5f/docs/ai_workload_research/CURRENT_STATE.md)。不删除或改写任何实验报告、Goal、历史commit或scientific authority；旧段落中的“待启动/STOP/proposal”须按其当时合同理解，不能代替下面的最新用户运行报告。

## 0. 最新执行状态：用户确认三个窗口都在执行

用户在A30发布之后明确报告：**“三个窗口都在执行”**。M/T/N均记录为**用户报告运行中**，不是本窗口SSH、进程或GPU锁的实时核验。当前没有收到或审定三者的新终态报告。

| Lane | 科学任务 | 固定启动入口与状态 |
|---|---|---|
| **M／109** | 原A26GR1真实Rubble／GS-Scale有界原生发现 | 原执行合同和已有启动上下文不变。用户报告运行中；不重发、不重启、不换数据/代码、不扩预算。 |
| **T／174-new** | A30T完整MoE decode算子强软件与执行粒度源审 | [Goal@6f4cd8bc](https://github.com/swayhrl/accel-sim-framework/blob/6f4cd8bc1e2c9623cbc70053eba607d8c0484ec3/docs/ai_workload_research/goals/AI_ARCH_A30T_MOE_COMPLETE_OPERATOR_SOURCE_DISCOVERY_174NEW_V1.md)，branch `hrl/aiarch-a30t-moe-complete-op-source-174new-v1`。用户报告运行中；本轮未核当前执行HEAD。 |
| **N／174-new** | A30N一个图像DiT部署在已有优化后的资源组织源审 | [Goal@cfdad590](https://github.com/swayhrl/accel-sim-framework/blob/cfdad590390f75ff56d7e263c233f7b1bcd4a554/docs/ai_workload_research/goals/AI_ARCH_A30N_DIT_POSTOPT_RESOURCE_SOURCE_DISCOVERY_174NEW_V1.md)，branch `hrl/aiarch-a30n-dit-postopt-resource-174new-v1`。用户报告运行中；本轮未核当前执行HEAD。 |

A30T固定启动commit：`6f4cd8bc1e2c9623cbc70053eba607d8c0484ec3`；A30N：`cfdad590390f75ff56d7e263c233f7b1bcd4a554`。启动记录见[A30批准/隔离/预算](ops/AI_ARCH_A30_TN_PARALLEL_SOURCE_DISCOVERY_LAUNCH_2026-10-14_V1.md)，其中“待启动”是发布时快照，本段追加的是用户随后确认的运行状态，不回写旧记录。

**资源边界维持：** T/N各CPU≤2 workers、RSS≤4GiB、新增≤100MiB，独立worktree/output/tmp，只读论文/源码与轻量研究设计；不运行Torch/CUDA、GPU、模型、模拟器、NCU/NSYS/NVBit，不下载权重/依赖，不访问109/164。M仅按其原合同工作；本窗口不接触节点、锁或执行目录。

## 1. 最新Discovery：Round A31｜CPU–GPU协同MoE的共享主存服务与资源分界

**执行者：ChatGPT／AI-ARCH Discovery，已完成。**

[**A31完整研究笔记**](literature/AI_ARCH_A31_CPU_GPU_MOE_COEXECUTION_RESOURCE_FRONTIER_2026-10-14_V1.md)。研究从A29第三储备继续，不重复T的GPU完整算子核查。指定段落审查五篇核心原文与公开Qwen配置；没有运行论文代码或建立作者实现固定源码/本机资格。

- **已有能力：** MoE-Lightning的异构资源模型、DALI的动态专家放置、CoX的AMX协同、HiNa的普通布局/NUMA优化，以及OSDI26混合系统的并发主存争用结果，都构成直接近邻。不能将动态调度、预取、热门驻留或“发现争用”直接称为新贡献。
- **条件推导：** 在明确的BF16三投影例子中，Q30单expert权重9MiB，未共享输入输出8mKiB；这是逻辑字节推导，不是实测traffic、CPU收益或C16新输入authority。
- **唯一候选Q-A31-01：** 独立测量的CPU／权重传输／GPU成本，在真实并发时是否仍能保持合法放置策略的性能排序？若排序改变，在强软件重新选优后是否还有值得研究的资源组织成本？论文存在争用或简化公式，不足以证明本机策略错误。
- **当前科学等级：** 原文支持的发现性问题＋最小实验草案；没有本机策略反转、性能headroom、新硬件机制或创新性成立的结论。不因缺完整oracle否定有界发现，也不因为源码存在操作就推断瓶颈。
- **后续决策：** 与T/N的候选一起按证据、强对照和增量执行成本筛选。只有确需执行的具体小合同另获批准后才进入节点；不现在增设第四Lane、不自动安排GPU、模拟器或机制实现。

## 2. A29与3DGS最近已审事实继续保留

[A29研究组合](literature/AI_ARCH_A29_3DGS_HARDWARE_HOTSPOT_AND_PARALLEL_NON3DGS_PORTFOLIO_2026-10-14_V1.md)：3DGS为一个有界探索分支；AI-ARCH总问题继续是P01/P13，不能随当前哪个模型已下载而改变主目标。

[A28 Rubble/CLM/GS-Scale来源审查](literature/AI_ARCH_A28_RUBBLE_CLM_AND_GSSCALE_TRANSFER_SOURCE_AUDIT_2026-10-14_V1.md)：真实Rubble来源、CLM强软件近邻与GS-Scale条件字节账保持；没有新的native结果可取代它。A26G的原合法G0 STOP与后续单独批准的A26GR1不是同一次执行，不能因目前R1在跑就改写原STOP。

此前所有A27/A26/A25及更早review、NequIP与Green Context、C16 Stage A和AWMA独立authority均维持原范围；完整记录从本页顶部固定历史快照进入。

## 3. 回收结果与下一阶段

每条Lane完成后独立提供exact commit、报告、真实证据等级、资源收据与远端核验。本窗口逐份审查，不要求一条有效结果等待所有其它Lane结束，也不提前采用尚未提交或未审定的数据。

筛选中心：**观察到什么、最接近方案已解决什么、剩下哪种解释、哪一项最小对照值得做。** 目标kernel family、应用覆盖加权和端到端分别评价；固定软件与允许软件重新选优后的资源收益分开。3DGS、MoE、DiT不必最终共用一个机制。

**本轮边界：** 只更新协调研究笔记和导航，0新节点任务、0新模型下载、0新GPU/模拟器/机制授权。三条正在执行的合同不受本页更新影响。
