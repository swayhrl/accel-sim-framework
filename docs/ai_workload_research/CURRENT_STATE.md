# AI-ARCH｜当前科研协调状态

**快照日期：2026-10-14。维护者：ChatGPT／AI-ARCH Discovery。**

本页是研究导航，不是节点进程监控，也不产生GPU执行授权。AI-ARCH窗口负责Discovery及总体协调；AWMA仍由原独立主窗口管理；C16为冻结历史证据。遵循[协调协议](COORDINATION_PROTOCOL.md)、[问题图谱](AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md)及[证据索引](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)。

**历史保存：** 本次将导航收敛为最新状态。A30及全部更早轮次的完整长日志原样保存在[固定历史CURRENT_STATE@15d20bb0](https://github.com/swayhrl/accel-sim-framework/blob/15d20bb0bbf045e9dc05f2d51eecb70c9b0cfd5f/docs/ai_workload_research/CURRENT_STATE.md)。不删除或改写任何实验报告、Goal、历史commit或scientific authority；旧段落中的“待启动/STOP/proposal”须按其当时合同理解，不能代替下面的最新用户运行报告。

## 0. 最新执行状态：Lane T/N完成并完成独立审查；Lane M保持原任务

用户已提交两条174-new的A30T/A30N终态和固定GitHub报告；本窗口已直接核对其远端commit/tree/blob、报告SHA与唯一文件变更，并发布[**A32独立科学审查**](reviews/AI_ARCH_A32_A30T_A30N_INDEPENDENT_SCIENTIFIC_CLOSEOUT_2026-10-14_V1.md)。各Lane内部CPU/GPU使用和worktree clean仍属于Codex原始回执，本窗口未SSH实时检查。

| Lane | 科学任务 | 当前有权威的证据范围及决定 |
|---|---|---|
| **M／109** | 原A26GR1真实Rubble／GS-Scale有界原生发现 | **用户最后报告运行中**，本窗口尚未收到正式终态；不重发、不重启、不改数据/锁/预算。 |
| **T／174-new** | A30T完整MoE decode operator源审 | [最终commit `1a8b9317`](https://github.com/swayhrl/accel-sim-framework/commit/1a8b9317de4c16e3dd19018f7f42cae1ebf5750e)，**SOURCE_ONLY COMPLETE / STOP；H200/SM90a条件性source probe候选，109 SM89不合格；没有新硬件机制资格**。 |
| **N／174-new** | A30N图像DiT优化后的资源组织源审 | [最终commit `6f78a2e1`](https://github.com/swayhrl/accel-sim-framework/commit/6f78a2e1e9a2fdb04bc9468f4b2d5594bc3229a6)，**SOURCE_ONLY COMPLETE / STOP；EVIDENCE_INSUFFICIENT / NO_HARDWARE_PROBE_READY**。 |

T/N本轮不续跑、不移植、不开109 GPU或174模拟器。它们各自在独立branch只新增一份报告，已由本窗口独立核验；A26G原STOP、A26GR1正在执行的单独许可、C16/AWMA冻结authority不变。

## 1. 最新独立审查：Round A32｜T/N为何没有立即晋升硬件实验

[A32完整独立review](reviews/AI_ARCH_A32_A30T_A30N_INDEPENDENT_SCIENTIFIC_CLOSEOUT_2026-10-14_V1.md)：
- **N：** DiSC原文确实覆盖CTR、ST、混合稀疏执行和hash-bank映射；以作者cycle-model vs A100 native的对照，不能证明PixArt-Σ1024的强GPU CTR+ST软件后仍存在物理资源残余。完整质量/时间/实际tile的同语义pair尚缺，当前正确STOP；不因没有作者reference就直接启动重型移植。
- **T：** MonoMoE相对于tuned vLLM的H200加速已经是作者**软件**结果；FlashInfer Mono公开API以预计算router_logits为输入，只能按logits→routed output建立公平边界。独立复算报告FP8 MAC/权重/scale账全部一致。它尚未证明**强Mono之后**额外硬件headroom；H200仍需独立平台/科学合同，RTX4080不能冒充。
- **决策：** T保留有范围的H200条件发现卡、N停止、A31 CPU–GPU协同MoE继续source-only储备。当前仅等待M真实结果供单独审查，后续Discovery不应为了填满174窗口重复派source-only任务。

## 2. 最新Discovery：Round A31｜CPU–GPU协同MoE的共享主存服务与资源分界

**执行者：ChatGPT／AI-ARCH Discovery，已完成。**

[**A31完整研究笔记**](literature/AI_ARCH_A31_CPU_GPU_MOE_COEXECUTION_RESOURCE_FRONTIER_2026-10-14_V1.md)。研究从A29第三储备继续，不重复T的GPU完整算子核查。指定段落审查五篇核心原文与公开Qwen配置；没有运行论文代码或建立作者实现固定源码/本机资格。

- **已有能力：** MoE-Lightning的异构资源模型、DALI的动态专家放置、CoX的AMX协同、HiNa的普通布局/NUMA优化，以及OSDI26混合系统的并发主存争用结果，都构成直接近邻。不能将动态调度、预取、热门驻留或“发现争用”直接称为新贡献。
- **条件推导：** 在明确的BF16三投影例子中，Q30单expert权重9MiB，未共享输入输出8mKiB；这是逻辑字节推导，不是实测traffic、CPU收益或C16新输入authority。
- **唯一候选Q-A31-01：** 独立测量的CPU／权重传输／GPU成本，在真实并发时是否仍能保持合法放置策略的性能排序？若排序改变，在强软件重新选优后是否还有值得研究的资源组织成本？论文存在争用或简化公式，不足以证明本机策略错误。
- **当前科学等级：** 原文支持的发现性问题＋最小实验草案；没有本机策略反转、性能headroom、新硬件机制或创新性成立的结论。不因缺完整oracle否定有界发现，也不因为源码存在操作就推断瓶颈。
- **后续决策：** 与已审T/N、未来M结果按证据、强对照和增量执行成本筛选。只有确需执行的具体小合同另获批准后才进入节点；不现在增设第四Lane、不自动安排GPU、模拟器或机制实现。

## 3. A29与3DGS最近已审事实继续保留

[A29研究组合](literature/AI_ARCH_A29_3DGS_HARDWARE_HOTSPOT_AND_PARALLEL_NON3DGS_PORTFOLIO_2026-10-14_V1.md)：3DGS为一个有界探索分支；AI-ARCH总问题继续是P01/P13，不能随当前哪个模型已下载而改变主目标。

[A28 Rubble/CLM/GS-Scale来源审查](literature/AI_ARCH_A28_RUBBLE_CLM_AND_GSSCALE_TRANSFER_SOURCE_AUDIT_2026-10-14_V1.md)：真实Rubble来源、CLM强软件近邻与GS-Scale条件字节账保持；没有新的native结果可取代它。A26G的原合法G0 STOP与后续单独批准的A26GR1不是同一次执行，不能因目前R1在跑就改写原STOP。

此前所有A27/A26/A25及更早review、NequIP与Green Context、C16 Stage A和AWMA独立authority均维持原范围；完整记录从本页顶部固定历史快照进入。

## 4. 后续任务选择和边界

T/N现已独立关闭，无需返工、续派CPU任务或抢占GPU。M完成后按原合同提交exact commit、原始证据与receipt，再做独立科学审查；没有正式报告前不宣布其完成或负结果。

筛选中心：**观察到什么、最接近方案已解决什么、剩下哪种解释、哪一项最小对照值得做。** 目标kernel family、应用覆盖加权和端到端分别评价；固定软件与允许软件重新选优后的资源收益分开。3DGS、MoE、DiT不必最终共用一个机制。

**本轮边界：** 只更新协调研究笔记和导航，0新节点任务、0新模型下载、0新GPU/模拟器/机制授权。T/N的SOURCE_ONLY终态已核验，M正在执行的原合同不受本页更新影响。
