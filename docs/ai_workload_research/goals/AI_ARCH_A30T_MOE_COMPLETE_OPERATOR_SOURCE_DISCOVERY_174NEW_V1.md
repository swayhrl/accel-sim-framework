# Round A30T｜MoE完整解码区域的执行粒度与强软件剩余：174-new CPU-only Goal

**授权来源：** 用户2026-10-14对[Round A29](../literature/AI_ARCH_A29_3DGS_HARDWARE_HOTSPOT_AND_PARALLEL_NON3DGS_PORTFOLIO_2026-10-14_V1.md)的T/N并行source-only方案明确回复“我完全同意，并行做起来吧”。**本Goal只授权当前这次有界的CPU/source/paper研究，不能转为109 GPU、174模拟器或新机制执行。**

**执行者：** 新的、独立的Codex窗口／174-new，标识Lane T (A30T)。**Goal入口：** 本文件。若旧Lane T仍运行，只能另开独立窗口/worktree，不能接管其进程或工作区；当前资源不足则`RESOURCE_DEFERRED`，不强制并发。

**Git输入固定：** repository `swayhrl/accel-sim-framework`，独立任务branch `hrl/aiarch-a30t-moe-complete-op-source-174new-v1`，创建起点协调commit `b806777afb33be0985ec7678e69f320578eefa43`。不要merge另一Lane或协调分支的新提交来改变科学输入；不修改已冻结的C16、AWMA或A26GR1 authority。

## 0. 核心问题与完成条件

**Q-A30T：** 在自然route、精度、结果合同和完整routed-MoE边界固定时，少token/expert的decode区域，在强适用软件实现之后，是否存在**非必然权重读取、非弱后端造成的**有用工作与硬件执行资源失配？如果存在，用哪一个最小的受控native发现实验区分它和软件/布局/带宽解释？

本轮优先形成`一张可以否定的完整operator问题卡`，不是寻找“MoE必然低效”的论据；不得先宣布新fusion、Gaussian式缓存、dequant cache或专用硬件机制。可能的合法终态包括`SOURCE_QUALIFIED_PROBE_CANDIDATE`、`PRIOR_ART_COVERS`、`PLATFORM_NOT_QUALIFIED`和`EVIDENCE_INSUFFICIENT`；负结果同样是正常科研产物。

至少将以下三种成本分开：必要权重字节/带宽、tile或工作粒度浪费、router/dispatch/combine与跨阶段组织。**结构利用率不是性能headroom；局部kernel时间不是完整operator wall。**

## 1. 阅读顺序和authorities

依次阅读并遵守：
1. `docs/ai_workload_research/CURRENT_STATE.md`（仅导航，不表示节点实时状态）；
2. `docs/ai_workload_research/COORDINATION_PROTOCOL.md`、`AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md`（P01/P05/P13）；
3. `docs/ai_workload_research/literature/AI_ARCH_A29_3DGS_HARDWARE_HOTSPOT_AND_PARALLEL_NON3DGS_PORTFOLIO_2026-10-14_V1.md`的``3–4、7–9``；
4. `AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md`及固定C16历史研究相关Git small reports（只读）。不要以旧C16自然route与均衡route相近的一组观察，等同完整MoE operator已经资格通过。

优先核公开原文/固定源码，最多4个直接关键近邻（必要时加1个实现文档）：
- [MonoMoE，arXiv 2609.04244](https://arxiv.org/abs/2609.04244)：作者摘要提出weight-major persistent operator及其融合范围；尽力获取正文实际实验组。若只获得摘要，严格标`ABSTRACT_ONLY`，不自行补作者实验表。
- [SonicMoE，arXiv 2512.14080](https://arxiv.org/abs/2512.14080)：实际workload、padding/tiling、训练与推理区别，不能把训练token rounding视为自然decode的等价优化。
- [FlashInfer官方fused_moe API](https://docs.flashinfer.ai/api/fused_moe.html)：MonoMoE/其调用路径的GPU/SM、精度、block size和可运行限制；区分公开API与论文自己实验的实现。
- 必要时 [MegaBlocks，arXiv 2211.15841](https://arxiv.org/abs/2211.15841) 或一个更直接、经核实的强近邻，用于证明不同执行规模/route的有效对照。
- 关联既有Qwen3-30B-A3B、DeepSeek/OLMoE的accepted semantic evidence，但不是重开C16 Stage A；不把仅有SASS shards视为operator wall authority。

逐个实验组记录`版本/页节表号、真实模型或算子配置、输入来源（自然route或合成）、top-k/专家数/有效token形状、数值格式、强软件基线、GPU型号、改动变量、完整operator还是局部kernel、实机/模拟/估算、作者明确理由、未披露`。作者事实、我们的推导、尚未验证的推测分列。

## 2. 同一个Goal内连续完成的四项科学工作

**G0｜资源和隔离预检：** 确认新worktree不覆盖任何旧Lane；检查实际CPU load/RSS/swap/文件系统余量/I/O。不干预正在运行的Lane M或任何AWMA/C16任务。资源不足则保留小receipt并STOP；不得kill他人进程、清理用户目录或为了准备而启动109/164访问。

**G1｜最强最近邻与平台矩阵：** 对完整边界`router→dispatch→专家两次projection/activation→combine`，核对上述论文/强后端到底融合或吸收了哪些成本。必须写明H200/SM90a等路径与目标Ada/SM89的差异。不能拿不可运行的H200软件当4080 native结果，也不能把4080的naive torch逐expert baseline当当前最强软件的公平替身。若作者未公开必要源码或实现细节，只记已知能力与未核之处。

**G2｜最小有用工作—资源账：** 从固定、可溯源的模型config/source或accepted小型identity报告选择一个实际MoE家族作为`future probe`对象；只推导可核的`M token数、E experts、top-k、自然selected expert集合、每expert tokens（仅accepted可见数据）、有用MAC、预测tile有效/无效工作、dispatcher/reduction可能字节、权重最小读取量`。任何执行tile形状必须找到确切后端源码/配置，找不到就`UNKNOWN`；用公式给出条件范围，不把理论MAC、权重bytes或源码调用行变成测得吞吐/等待。不下载或加载模型，不构造假route。

**G3｜设计一个真正能分辨解释的最小DISCOVERY_PROBE（设计而非执行）：**
- 冻结一个完整routed operator对象，最多3个预选有效token规模；自然route为应用基准，人工route只能独立标成诊断。
- 需要一个适用于目标平台/格式的合法强软件对照，并列一个`如果没有同平台强对照怎么办`的降级路径，不能偷换精度或解释。
- 用`native uninstrumented complete-op latency + precise source/census ledger + select NCU only when appropriate`设定观察量；说明必须包含哪些route/dispatch/expert/combine开销，哪些在明确边界外。
- 明确两个竞争解释和能够否定硬件机会的结果，例如强后端已吸收、容量只受必读权重约束、自然结果没有目标范围、剩余由软件组织解决。
- 未来才考虑target family→workload weighted→完整请求三层效果；不要预报speedup或把padding比例当性能增益。
- 仅提出一项最小GPU请求和预冻结输入/数值/holdout建议；**本次不运行。**

**G4｜一个提交中闭环：** 一份报告，含来源矩阵、最近邻collision、operator账、`PROBE_OR_STOP`判定、科学边界与资源receipt；严格UTF-8、引用和路径一致性自检、commit/push、远端fetch-back exact commit/tree/blob核验后STOP。出版方/作者不可合法取得的正文记`NOT_VERIFIED`而不是编造，普通链接、路径、小包装问题同一Goal中有界solve-and-continue。

## 3. 唯一科学交付与预算

在上述独立branch**只新增**：

`docs/ai_workload_research/reviews/AI_ARCH_A30T_MOE_OPERATOR_RESOURCE_DISCOVERY_174NEW_V1.md`

建议报告300行内（有证据必要可略超），至少含：
`SOURCE_AND_EXPERIMENT_GROUPS`、`STRONG_BASELINE_AND_SM89_GAP`、`USEFUL_WORK_RESOURCE_LEDGER`、`ONE_PROBE_OR_STOP`、`RESULT_AND_LIMITATIONS`、`CLOSEOUT_RECEIPT`。该文件是可追溯评审材料，**不覆盖`CURRENT_STATE.md`、图谱、任何旧A21–A29/C16/AWMA文件**。小型脚本若确有必要，限定本任务目录，无工具框架开发。

单Lane累计资源上限：CPU ≤2有效workers，最大RSS ≤4GiB，新增文件/临时下载合计≤100MiB；其中文献PDF合计≤40MiB、单PDF≤20MiB，所有其它模型/权重/数据/依赖下载=0；建议同一任务≤6小时主动STOP。两条174 lane总预算为各自上限之和；实际可并行需先检查剩余资源；174本地存储高压时优先无下载的远端只读源码/论文。

**绝对禁止：** GPU/CUDA/Torch import、模型forward、JIT、编译、模拟器/RTL、NSYS/NCU/NVBit、109/164 SSH、额外模型下载、所有GPU共享锁操作、与其它branch共享可变文件、重启/调整A26GR1、恢复C16/AWMA冻结任务、修改已有scientific contracts、设计并实现硬件机制、真实holdout执行。不得自行创建后续GPU Goal并宣称已授权。

只有G4 remote readback后可报告`A30T_COMPLETE_SOURCE_ONLY`；本文件提交成功只表示`A30T_AUTHORIZED_READY_FOR_CODEX`，不表示Codex已执行。