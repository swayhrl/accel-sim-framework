# AI-ARCH｜当前科研协调状态

**快照日期：2026-10-13。执行者：ChatGPT／AI-ARCH Discovery。**

这是GitHub已发布科研结果的导航，不是节点进程监控，也不是GPU执行授权。AI-ARCH本窗口负责Discovery及总体协调；AWMA由原独立主窗口管理；C16为历史证据。方法遵循[协调协议](COORDINATION_PROTOCOL.md)、[问题图谱](AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md)及[证据索引](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)。

## 最新完成：Round A7｜非LLM发现性观察完整合同与执行前审查

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

## 下一阶段：Round A8｜109静态结构有限观察（待明确GPU审批）

**拟执行者：Codex Lane N／109独立新worktree；科学审查：ChatGPT／AI-ARCH Discovery。**

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
