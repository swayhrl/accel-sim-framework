# AI-ARCH｜当前科研协调状态

**快照日期：2026-10-14。维护者：ChatGPT／AI-ARCH Discovery。**

本页是研究导航，不是节点进程监控，也不产生GPU执行授权。AI-ARCH窗口负责Discovery及总体协调；AWMA仍由原独立主窗口管理；C16为冻结历史证据。遵循[协调协议](COORDINATION_PROTOCOL.md)、[问题图谱](AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md)及[证据索引](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)。

**历史保存：** A30及更早的完整长日志保存在[固定历史CURRENT_STATE@15d20bb0](https://github.com/swayhrl/accel-sim-framework/blob/15d20bb0bbf045e9dc05f2d51eecb70c9b0cfd5f/docs/ai_workload_research/CURRENT_STATE.md)；A32收口导航见[CURRENT_STATE@80c4362f](https://github.com/swayhrl/accel-sim-framework/blob/80c4362fbe79fc92fb82c786513153a4f7231bb7/docs/ai_workload_research/CURRENT_STATE.md)。不删除或改写任何旧实验、Goal、报告、commit或scientific authority。旧“待启动/STOP”按其当时合同理解。

## 0. 最新执行状态：M保持原任务；T/N已独立审查并STOP

用户最新报告Lane M还需数小时；这是用户运行报告，不是本窗口SSH核验。A30T/A30N已提交固定Git报告并由[A32独立审查](reviews/AI_ARCH_A32_A30T_A30N_INDEPENDENT_SCIENTIFIC_CLOSEOUT_2026-10-14_V1.md)核对commit/tree/blob及报告SHA。节点资源、无CUDA、现场worktree clean仍是执行侧receipt。

| Lane | 科学任务 | 当前状态和边界 |
|---|---|---|
| **M／109** | A26GR1真实Rubble／GS-Scale有界原生发现 | **用户报告仍在执行，还需数小时**；未收到正式终态。不登录、不重发、不重启、不改数据/代码/锁/预算。 |
| **T／174-new** | A30T完整MoE decode operator源审 | [最终commit `1a8b9317`](https://github.com/swayhrl/accel-sim-framework/commit/1a8b9317de4c16e3dd19018f7f42cae1ebf5750e)，**SOURCE_ONLY COMPLETE / STOP**；H200/SM90a条件性发现卡，109 SM89未资格化，无新硬件机制。 |
| **N／174-new** | A30N图像DiT优化后的资源组织源审 | [最终commit `6f78a2e1`](https://github.com/swayhrl/accel-sim-framework/commit/6f78a2e1e9a2fdb04bc9468f4b2d5594bc3229a6)，**SOURCE_ONLY COMPLETE / STOP**；证据不足，当前无硬件probe。 |

不恢复T/N、不移植MonoMoE或DiSC，不因研究新候选开启GPU/模拟器。A26G原STOP、A26GR1单独许可、C16/AWMA冻结authority均不变。

## 1. 最新Discovery：Round A33｜GPU向量检索的搜索状态与资源权衡

**执行者：ChatGPT／AI-ARCH Discovery；公开原文、固定源码及纯算术研究已完成。**

[**A33完整研究笔记**](literature/AI_ARCH_A33_GPU_ANNS_SEARCH_STATE_RESOURCE_DISCOVERY_2026-10-14_V1.md)。初筛DScale变长验证与OneLA大beam状态复用后，不重复其已覆盖机制；本轮保留GPU图式ANNS作为新的**AI系统检索算子**候选，不称神经网络forward或完整RAG加速。

- **直接强近邻：** CAGRA已比较遗忘历史表、global表和单/多CTA；Jasper已研究删除历史hash与查询并发；IVF-RaBitQ已有LUT/bitwise资源折中和阶段式SMEM复用。不能把“少存状态换重算”“新增缓存/并行”当新意。
- **固定源码：** `NVIDIA/cuvs@bc23aa84a0ef26d85900185ad5e68d3372be487e`。planner的hash容量、reset interval与AUTO block/algo相互耦合；当前multi-CTA也有私有visited/shared traversed两类状态。改一个软件参数不能冒充单一物理资源干预。
- **条件推导：** itopk128/degree64/width1/fill0.5/uint32时，2/4/8/16KiB小表对应2/6/14/30轮清理。所有数值是源码算术，不是实际重算、recall、occupancy或延迟。
- **唯一Q-A33-01：** 同一真实图与质量要求下，现有强软件是否已经处理搜索状态与查询并发的矛盾；若没有，剩余完整search时间是否对明确资源约束有可区分响应？仅保留有实验出口的发现问题，未证明硬件剩余或新颖性。
- **最小草案：** GloVe100真实向量/查询/真值，3个batch×3条固定single-CTA历史表路径＋官方AUTO reference，共12格；固定路径诊断与同recall强软件选优分开。无数据下载、本机资格或执行。官方CC8.0+范围不排除Ada，但不等于当前109环境可直接运行。
- **下一步：** 不让T/N再做重复源审。若以后选择该候选，按独立预算将环境/资产/功能canary和小矩阵放在一个连续Goal；M优先且当前无新GPU授权。不先建tracer、模拟器或新控制器，不把已知tradeoff复现写成新机制。

## 2. 最近独立审查：Round A32｜T/N有范围收口

[A32完整review](reviews/AI_ARCH_A32_A30T_A30N_INDEPENDENT_SCIENTIFIC_CLOSEOUT_2026-10-14_V1.md)：N的DiSC专用硬件模型不能证明强GPU CTR+ST软件后的剩余，质量/时间/tile配对尚缺；T的MonoMoE相对tuned vLLM提升已是作者软件结果，不等于强Mono后硬件headroom。公开Mono API从router_logits进入，未来对照不能漏计边界。两条STOP均接受，未否定整个DiT/MoE领域。

## 3. 储备Discovery：Round A31｜CPU–GPU协同MoE

[A31完整笔记](literature/AI_ARCH_A31_CPU_GPU_MOE_COEXECUTION_RESOURCE_FRONTIER_2026-10-14_V1.md)。MoE-Lightning、DALI、CoX、HiNa与OSDI26混合系统已覆盖多种协同/资源/争用问题，不能将动态分派、预取或发现争用直接作为新意。

唯一Q-A31-01：独立测量的CPU／权重传输／GPU成本，在真实并发时是否保持策略的性能排序；若改变，强软件重选后还有什么资源组织成本？仍为文献级问题，无本机策略反转/硬件剩余。不增设第四Lane、不在109运行未经授权的协同任务；与A33及M实际结果一起按科学区分度、强基线和增量成本选择。

## 4. A29与3DGS已审事实保留

[A29研究组合](literature/AI_ARCH_A29_3DGS_HARDWARE_HOTSPOT_AND_PARALLEL_NON3DGS_PORTFOLIO_2026-10-14_V1.md)：3DGS是一个有界探索分支，AI-ARCH总问题仍为P01/P13，不因哪个模型先下载而改变主目标。

[A28 Rubble/CLM/GS-Scale审查](literature/AI_ARCH_A28_RUBBLE_CLM_AND_GSSCALE_TRANSFER_SOURCE_AUDIT_2026-10-14_V1.md)：真实来源、CLM强软件近邻及条件字节账不变。原A26G合法G0 STOP与后续单独批准A26GR1不是同次执行，R1运行不能改写旧STOP。NequIP/Green Context、C16 Stage A和AWMA独立authority保持各自冻结范围。

## 5. 后续任务选择与权限

本轮只新增A33研究笔记并维护导航，没有新Codex、节点访问、模型/数据/依赖下载、GPU、模拟器、机制实现或holdout执行。M结果回来后独立审查，不提前宣布完成或科学结论。

发现阶段允许真实输入、合理强软件对照下的小预算观察，不要求先完成全部oracle；硬件贡献阶段仍要求因果与成本证据。目标family、应用加权与end-to-end分开；固定软件和允许软件重新选优后的资源收益分开。不得以维持并行为理由人为填充空闲窗口，也不把一个具体baseline缺口无限扩张成工具工程。
