# AI-ARCH｜当前科研协调状态

**最新快照：2026-10-16 / Round A76：A75 R/D双线Discovery全部完成并独立审查，均`SOFTWARE_NEARBY_NO_SURVIVOR / STOP`。** 两线没有本机native或GPU模拟结果；合计0个推荐/备选，不表示RL后训练、视频DiT体系结构headroom被测负。A76最新科研建议：停止重复宽泛source-only“寻找新API”，下一次投入应考虑**真实主流AI负载的GPU资源饱和和反事实characterization**，首先制定科学输入/模拟器资格方案，而非自动启动GPU。

**历史快照**：[A75准备期CURRENT_STATE](https://github.com/swayhrl/accel-sim-framework/blob/cba17023e7a86454936e881515384e785c4b9d53/docs/ai_workload_research/CURRENT_STATE.md)、[A74-C已完成](https://github.com/swayhrl/accel-sim-framework/blob/05c1722066bda6a079d92fdfca34bdd28249a72f/docs/ai_workload_research/CURRENT_STATE.md)；所有旧Goal/运行raw/原报告/原STOP保持不变，不合并两条执行分支HEAD。

## 1. R-A75和D-A75固定科研权威

| Lane | 固定Git final/tree及原始报告 | 科学边界 |
|---|---|---|
| **R-A75／109** | [R原报告](https://github.com/swayhrl/accel-sim-framework/blob/8e53641295068cdef653362d0f8d7f441c636b11/docs/ai_workload_research/discovery/A75_R_RL_POSTTRAIN/REPORT.md)，commit`8e53641295068cdef653362d0f8d7f441c636b11`、tree`8861ec3174330260b8faaa205e80efca80183f69` | `SOFTWARE_NEARBY_NO_SURVIVOR`。NeMo Qwen3-8B的完整同步RL step有作者32GB200 native阶段时间；有EAGLE-3后Generation仍Think/Zero分别63.3%/52.7%，但是合法GRPO complete-group、RolloutPipe CGP/FGD、NeMo同步TQ/推测、Libra弹性等已有软件近邻。尚未证明活动GPU上的不同硬件需求，reward没有独立作者计时行，235B收益是作者模拟，不能外推。 |
| **D-A75／174-new** | [D原报告](https://github.com/swayhrl/accel-sim-framework/blob/6421e6768ff3df2ec20cddd87b3aa28b932c113a/docs/ai_workload_research/discovery/A75_D_WAN_VIDEO_DIT/REPORT.md)，commit`6421e6768ff3df2ec20cddd87b3aa28b932c113a`、tree`f10bb08891193d01b5ad98534f4514610df48eb3` | `SOFTWARE_NEARBY_NO_SURVIVOR`。Wan2.2 TI2V-5B官方121帧/720P、50步、双CFG、30层；A14B按噪声阈值单次切高/低专家，不等于token级MoE。TeaCache、BWCache、STA等近似质量-速度方法及Cache-DiT双expert/CFG缓存是直接近邻；没有同视频、同质量、同求解器和强后端后的独立硬件归因。 |

A75共同Goal起点`1eb14b0395bc898c3707ba850c36f17a9ec07b4e`。GitHub独立审查：每条从Goal→final各ahead1，仅新增本Lane四份文件；final→各自远端branch HEAD`identical`；Git-data commit parent/tree与用户回执相同。R证据27条14列，D证据18条17列、ID各自唯一、TSV字段数全部正确，二者`QUESTION_CARDS.json=[]`。

**[Round A76完整独立审查](reviews/AI_ARCH_A76_A75_R_D_INDEPENDENT_REVIEW_AND_DISCOVERY_METHOD_PIVOT_2026-10-16_V1.md)**；首次commit`53005a9d3562b57873cfac65f32f98cca3c17539`。控制端重新复核NeMo训练步4组守恒、Wan2.2固定配置/生成/Cache-DiT固定源码和5B 27,280token的纯几何算术；这不是本地GPU性能、视频峰值或最终质量试验。原执行者fetch-back blob/SHA/clean按原RECEIPT存留，本审查只核Git/source identity，不自称完成原Lane的节点动作。

## 2. 当前科学排序和方法调整

1. **A70主流LLM混合服务、GDN、MoE、VLM四线**：限定源码已知直接近邻，无native性能负证据；[A72独立综合](reviews/AI_ARCH_A72_A70_M_AND_FOUR_LANE_DISCOVERY_SYNTHESIS_2026-10-16_V1.md)冻结。
2. **A73 W**：provider cache计数无法恢复真实model-facing prompt，`SOURCE_INCOMPLETE`；**A73 H/A74-C**：TC↔SFU fixed area/power假说因SM100模型/同工艺PPA不足`PARKED`，不能申请B200的“同面积”机制证据。[A74-C结果](https://github.com/swayhrl/accel-sim-framework/blob/d2530b3bb8a2743b716ec58e6a3113d18b66c71f/docs/ai_workload_research/discovery/A74_C_ISO_RESOURCE_ADMISSION/REPORT.md)冻结。
3. **A75 R/D**：本次真实主流后训练与视频生成路径科学源审成功、硬件候选为0；现有直接近邻不等于全部应用都没有片上限制。
4. **建议A77研究方法变换（`PROPOSAL_ONLY`）**：一次有界CPU静态characterization设计，先核现有accepted真实AI模型/输入和原生平台及Accel-Sim资格，不下载模型或操作164；之后如科学合同闭合，可用最小实际自然GPU workload在强软件下探查资源饱和、计算/访存/issue、片上容量/服务以及独立验证，再有界进行资源反事实。两条互补准备Lane可分别核workload authority与simulator/原生标定，**不是再派四个并行论文搜索**。任何GPU/模拟器/新硬件必须单独获批，旧C16/AWMA既有任务与authority不自动转移。
5. **不重开A75 R/D原生作业或权重/视频下载**：R作者32GB200强对象无法用10916GB等价复现，D官方5B 720P单卡配置≥24GB；没有具备强软件与合法质量门的原生新问题则不为完成任务租卡。

## 3. 当前执行状态与跨项目冻结

用户报告R、D两个Codex窗口均STOP，任务CPU/source-only。109/174-new/164没有本轮新增GPU或模拟器授权，不得自动重启；未核实时进程，本文只记用户回执。旧GNN A61/A65/A67、Q-S/ScanNet A69、3DGS A26、C16、AWMA、ISCAS的科学STOP、repo分支、数据及资源边界保持不变。共享GPU锁沿用原协议但本轮无GPU作业。

**A76终态：R/D各合法STOP、独立审查完成；尚未创建A77 Goal或派发新Codex，真实资源characterization为下一方法建议。**
