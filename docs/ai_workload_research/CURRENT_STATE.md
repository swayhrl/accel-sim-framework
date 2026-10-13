# AI-ARCH｜当前科研协调状态

**快照日期：2026-10-13。执行者：ChatGPT／AI-ARCH Discovery。**

这是GitHub已发布科研结果的导航，不是节点进程监控，也不是GPU执行授权。AI-ARCH本窗口负责Discovery及总体协调；AWMA由原独立主窗口管理；C16为历史证据。方法遵循[协调协议](COORDINATION_PROTOCOL.md)、[问题图谱](AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md)及[证据索引](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)。

## 最新完成：Round A6｜非LLM强软件路径核实与公开训练实验组审计

**执行者：ChatGPT／AI-ARCH Discovery；本轮没有启动Codex、109 GPU或174模拟器。**

[Round A6报告](literature/AI_ARCH_ROUND_A6_NEQUIP_PATH_AND_PUBLIC_TRAINING_2026-10-13_V1.md)，初始发布提交 `d4d07272871cd15a29258df1b4aa83956eb907e0`。

| 研究项 | 已核对的新事实 | 当前结论与边界 |
|---|---|---|
| 非LLM原生路径 | 固定NequIP源码含OEQ、GPU alchemiops邻居后端、能量/力/应力；ase固定单帧，batch另有编译目标 | 不必先适配Sobek；源码支持不等于4080运行资格 |
| 静态结构问题 | 既有Si帧可作为静态结构输入；连续时间仍未认证 | 缺连续索引限制跨帧复用/重建频率，不应阻断静态结构评估设计；不宣称统计独立 |
| 拟议有限观察 | 同32个预选结构，CPU构图B2与GPU构图B2/4/8，保持输出与模型 | `SOURCE_PATH_SUPPORTED / MEASUREMENT_DESIGN_READY_FOR_REVIEW`；设计尚未执行，也不表示硬件余量成立 |
| 公开训练例子 | TorchTitan v3明确C4英文数据、Llama tokenizer与分组配置；源码可核token生成、分片和状态恢复 | 可作为新训练设计起点，不能冒充已复现论文原token流或H100集群；非标准H100峰值不外推 |
| 强软件近邻 | SimpleFSDP及2026 CPU activation offload资料 | 保存/重算/迁移及通信重叠已有软件能力，容量改善不自动等于时间收益；没有新增训练任务 |

## Lane与独立项目状态

| 工作线 | 固定已审来源 | 当前状态 |
|---|---|---|
| Lane T | [A4训练源审@a1a70180736499687435b1e2d99984d4ebba4c53](https://github.com/swayhrl/accel-sim-framework/blob/a1a70180736499687435b1e2d99984d4ebba4c53/docs/ai_workload_research/reviews/AI_ARCH_A4_TRAINING_SOURCE_REVIEW_174NEW_V1.md) | 原任务完成/STOP；A5接受有限未准入判断。不追加352B调查 |
| Lane N | [V1@e355f096eeac44328d7463ef3256cc649ec9cb03](https://github.com/swayhrl/accel-sim-framework/blob/e355f096eeac44328d7463ef3256cc649ec9cb03/docs/ai_workload_research/reviews/AI_ARCH_A4_NONLLM_SOURCE_REVIEW_174NEW_V1.md) | A5确认文本丢失，整体文档仍PARTIAL；A6读回该分支仍此HEAD，未声称V2修复。历史源审STOP不变 |
| C16 | [Reset@635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f](https://github.com/swayhrl/accel-sim-framework/commit/635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f)；[Stage A@ccd6928bfb420d1e4c554ec0e377bb8fbe377501](https://github.com/swayhrl/accel-sim-framework/commit/ccd6928bfb420d1e4c554ec0e377bb8fbe377501) | 历史Stage A TERMINAL_PARTIAL、Reset关闭；不恢复Observer、Tier1或旧holdout |
| AWMA R27R3 | [独立review@d6e9bbfb562814bcd5dc5adb444d3c572e7f446b](https://github.com/swayhrl/accel-sim-framework/blob/d6e9bbfb562814bcd5dc5adb444d3c572e7f446b/docs/vm_tlb/literature_notes/awma/empirical/R27R3_B0_REFERENCE_REPEATABILITY_REVIEW_2026-10-13.md)；[协调同步](R27R3_INDEPENDENT_REVIEW_SYNC_2026-10-13.md) | 保持B0_REFERENCE_NOT_REPEATABLE、COMPLETE/STOP，不推断C1/S2、容量或根因；AWMA后续状态仍以原窗口最新已审权威为准 |
| AWMA其它证据 | [C16/AWMA证据索引](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md) | Pre-L1有范围模拟结果、R23G局部软件结果、R26重复输入容量与R27R2资格失败分别保留，不由本窗口更改 |

Lane的Git HEAD不证明其本地进程状态。109共享GPU锁、174分析角色及164大raw权威不变；没有任何新GPU、模拟器、权重下载、训练或机制授权。

## 下一轮：Round A7｜收敛一份非LLM发现性观察合同

**执行者：ChatGPT／AI-ARCH Discovery；Codex暂不新增Goal。**

围绕A6四条件设计，明确模型包元数据、版本组合、数值/边集合判据、完整时间边界、实际执行预算与STOP。区分能在源码中确认的项目和必须在未来GPU canary确认的项目。不再重复广泛论文筛选，不开发Sobek适配器，也不建MD平台。

若形成可执行合同，将GPU所需模型获取、设备编译与观察单独明确列出，交用户审阅后才运行。发现性诊断不要求提前证明完整硬件收益；机制晋升仍要求强基线、实际代价、因果和独立验证。训练新例保留研究，不用单卡代理冒充原多GPU实验。

## 历史轮次与证据导航

本次将原来逐轮追加的导航整理为当前汇总，**没有重写历史报告或实验结论**。A1–A5完整旧导航保存在[CURRENT_STATE@3d0a959d3d6b77de67fdf9cc3f891d4adcc5416b](https://github.com/swayhrl/accel-sim-framework/blob/3d0a959d3d6b77de67fdf9cc3f891d4adcc5416b/docs/ai_workload_research/CURRENT_STATE.md)，避免旧“尚未启动”快照与后续已完成状态混淆。

- [A1论文实验组](literature/AI_ARCH_P01_P13_EXPERIMENT_GROUP_AUDIT_2026-10-13_V1.md)；[A1资源/调度因果精读](literature/AI_ARCH_P01_P13_RESOURCE_MODEL_CAUSAL_READING_2026-10-13_V1.md)。
- [A2执行资源近邻](literature/AI_ARCH_P01_P13_ROUND_A2_EXECUTION_RESOURCE_BOUNDARIES_2026-10-13_V1.md)。
- [A3历史证据与准入](literature/AI_ARCH_ROUND_A3_HISTORICAL_EVIDENCE_CLOSURE_AND_CANDIDATE_ADMISSION_2026-10-13_V1.md)。
- [A4三family与并行安排](literature/AI_ARCH_ROUND_A4_NATURAL_WORKLOAD_PARALLEL_DISCOVERY_2026-10-13_V1.md)。
- [A5联合独立审查](reviews/AI_ARCH_ROUND_A5_LANE_T_N_INDEPENDENT_REVIEW_2026-10-13_V1.md)。

工具候选Skill只采用方法，不安装、自动加载或合并候选分支。尚未直接读取的节点raw一律不宣称本窗口已重新验证。
