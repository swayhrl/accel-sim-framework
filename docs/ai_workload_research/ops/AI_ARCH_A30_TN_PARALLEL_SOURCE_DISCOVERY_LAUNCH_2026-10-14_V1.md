# Round A30｜MoE／DiT双Lane并行Source Discovery启动记录

**记录者：ChatGPT／AI-ARCH Discovery；日期：2026-10-14；协调分支：`hrl/ai-workload-research-coordination`。**

**用户明确批准：** 在本窗口A29完成3DGS硬件热度核验和非3DGS组合后，用户回复“我完全同意，并行做起来吧”。批准对象严格限定于A29第7节的两条独立CPU/source/paper-only科研核查：Lane T完整MoE解码粒度与Lane N优化后DiT资源组织。并不授予新的109 GPU、174模拟器、weight下载、模型执行、机制实现或holdout。

## 科学主线与边界

- 统一P01/P13：真实AI工作粒度、执行阶段与强软件变化之后，GPU的瓶颈和资源配比如何迁移；不把AI-ARCH缩窄为3DGS或某单一cache/TLB。
- **Lane M／109：** 用户报告已在执行A26GR1 Rubble／GS-Scale，完全由原独立合同控制。A30不打断、不重发启动、不检查GPU锁、不改预算/数据/模型/scene/代码、不重启，不推断实时完成状态。
- **Lane T／174-new：** 独立CPU/source-only，完整MoE operator的执行粒度和强软件最近邻。不得以旧C16 shard结果推断完整operator时间。
- **Lane N／174-new：** 独立CPU/source-only，一个实际图像DiT部署在已有稀疏/复用优化之后的资源失配。不得直接设计新跨步缓存或偷换质量目标。
- 第三储备CPU–GPU协同MoE仅由ChatGPT继续公开论文阅读；没有额外Codex任务或节点权限。AWMA独立项目和C16冻结边界不变。

## 两份已发布的独立Goal

| Lane | 独立任务分支 | Goal固定HEAD | 任务入口 |
|---|---|---|---|
| T / 174-new | `hrl/aiarch-a30t-moe-complete-op-source-174new-v1` | `6f4cd8bc1e2c9623cbc70053eba607d8c0484ec3` | [A30T](https://github.com/swayhrl/accel-sim-framework/blob/6f4cd8bc1e2c9623cbc70053eba607d8c0484ec3/docs/ai_workload_research/goals/AI_ARCH_A30T_MOE_COMPLETE_OPERATOR_SOURCE_DISCOVERY_174NEW_V1.md) |
| N / 174-new | `hrl/aiarch-a30n-dit-postopt-resource-174new-v1` | `cfdad590390f75ff56d7e263c233f7b1bcd4a554` | [A30N](https://github.com/swayhrl/accel-sim-framework/blob/cfdad590390f75ff56d7e263c233f7b1bcd4a554/docs/ai_workload_research/goals/AI_ARCH_A30N_DIT_POSTOPT_RESOURCE_DISCOVERY_174NEW_V1.md) |

两条branch**都从**已固定A29协调提交`b806777afb33be0985ec7678e69f320578eefa43`独立分出。它们彼此不merge，不能共写`CURRENT_STATE.md`。Goal写入与commit SHA已远端读取，compare相对b806均为`ahead_by=1, behind_by=0`，变更文件只含该Lane自己的Goal。**新Codex窗口尚待用户实际发送启动指令：`AUTHORIZED_READY_FOR_CODEX / EXECUTION_NOT_OBSERVED`，不能宣称已启动。**

## CPU资源上限与并行调度

- 每Lane有效CPU workers≤2、RSS≤4GiB、新增文献/临时/输出总≤100MiB，PDF总≤40MiB且单篇≤20MiB、单Goal建议≤6小时STOP；两Lane最大合计为CPU4、RSS8GiB、新增200MiB，而不是每条Lane都可以重复使用整个174。
- 两边先自行只读检查174 CPU负载、swap、overlay余量、IO与其它任务。**如果旧Lane或AWMA仍占资源，主动减少同时workers或`RESOURCE_DEFERRED`；不终止它们，不清理用户文件，不能以追求并行为由挤占其它任务。**
- 各自新worktree、文件、tmp、receipt及Git分支；只读共享公开论文和协调源，不访问109/164，不用GPU/模拟器、Torch/CUDA、NSYS/NCU/NVBit、不下载模型权重、不开C16/AWMA旧任务。
- 普通URL/manifest/UTF-8/包装问题有界solve-and-continue。关键science input、exact身份、数值/claim、权限或预算变化才STOP。
- 最终每Lane只交付一张具体`ONE_PROBE_OR_STOP`研究问题卡，写清真实工作对象、最强能力、单个资源解释、最低诊断、反证及平台资格。论文热度、source推导和本机native结论不能混用。
- 完成者先独立commit/push/readback并STOP，后由ChatGPT本窗口独立审查，决定是否统一申请**一个**最有价值的GPU发现性probe；不自动发布GPU Goal。

## 状态与回收

2026-10-14：两个Goal均`AUTHORIZED_READY_FOR_CODEX`、`EXECUTION_NOT_OBSERVED`。**A26GR1仍按用户最后报告处于Lane M执行中，非本窗口远端确认。** 本记录仅发布研究分工和准入上限。

下一次接收两个Lane结果：逐份核fixed source、原文实验组、强baseline/平台、恰当质量、资源账、最小反证、blob和branch HEAD；没有证据的部分保留UNKNOWN。独立审查后才修改协调科学决定。