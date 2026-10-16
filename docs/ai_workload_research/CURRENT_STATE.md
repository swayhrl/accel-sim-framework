# AI-ARCH｜当前科研协调状态

**最新快照：2026-10-16 / Round A74。A73的W/H已完成并独立审查；W合法STOP，H仅保留一个有条件的来源级硬件资源取舍问题，暂未获原生/模拟器资格。** 新A74-C单窗口CPU/source准入Goal已发布且远端独立分支准备完毕，状态`READY_FOR_USER_DISPATCH`，尚未收到启动回执。A70四线此前全部0候选的科学边界仍保留。

旧导航固定保存：[A73派发状态@a838c13](https://github.com/swayhrl/accel-sim-framework/blob/a838c13af9d0dc94d1aa1714aeb449fd23c51e7f/docs/ai_workload_research/CURRENT_STATE.md)、[A72四线收口@adf6ab9](https://github.com/swayhrl/accel-sim-framework/blob/adf6ab9467887f74b0b509c105977128663707a5/docs/ai_workload_research/CURRENT_STATE.md)。历史执行分支、原始报告和终态不修改。

## 1. A73原始结果及Round A74审查

| Lane | final commit/tree | 科学原状态 | 独立审查后的位置 |
|---|---|---|---|
| **W / 109：真实聊天与Agent自然工作量** | `e7f2438aec9ee5c3ab677027c48a08dcd40c75b0` / `ba20263794bd7b9b94f0050b4e985347578ae7ad` | `SOURCE_INCOMPLETE / STOP`，23条证据，两个真实场景资格卡，1个WQ01 PARKED，0个晋升 | 接受合法STOP。TraceLab仅提供去标识化cache/会话/工具计数，shape replay用合成prompt，**不是原目标Qwen同token内容**；官方SWE-chat需另获访问与隐藏模板核验。不得基于provider缓存计数生成硬件性能结论。 |
| **H / 174-new：GPU资源反事实** | `06b17a72f683316a4088292a4b424c9d97c7437c` / `0e53a3747c069f82322eea003f045c1b54ac1804` | `SOURCE_QUESTION_READY_FOR_CROSS_REVIEW / STOP`，初筛12、深审6，唯一H73-Q1 | **HYPOTHESIS_RETAINED / NATIVE_NOT_ADMITTED。** 固定area/power预算下TC资源与exp/SFU/片上服务交换，并逐硬件点重调FA4/cuDNN，完整Qwen3-8B Prefill净效益未知；不是已证硬件瓶颈。 |

GitHub连接器独立复核两条final的parent为共同A73固定Goal `9afcdf6faa5b8351b56c9cbbefd3530c19c89537`，各ahead1且只增自身4交付，final→相应执行HEAD identical、tree与回执一致。W23条15列、H14条20列证据记录结构正确、ID各自唯一。本轮没有实时SSH复跑或逐项重算全部执行者私有下载SHA。

**核心独审：[Round A74 W/H科研裁决](reviews/AI_ARCH_A74_A73_W_H_INDEPENDENT_SCIENTIFIC_REVIEW_2026-10-16_V1.md)**，审查初次发布commit `db29506ac0adfce419989977b587729ce99f3a13`。该报告补入两项直接近邻：

- **FA4已正式发表于MLSys 2026**（H已读的arXiv v1并非唯一公开版本），官方论文/最新源码差异要另审，不得用过时cuDNN9.13断言最强。
- **NVIDIA Blackwell Ultra/GB300已实际提高exp SFU吞吐约2倍**，并在特定FP8注意力前向给出性能结果。此为真实硬件先例而非固定iso-area比较；“更多SFU使Softmax更快”不是新机制。保留的问题仅是明确固定面积/功耗、真实完整模型机会成本和软件重新调优的资源Pareto点。

审查另独立复算Qwen3-8B理想因果QK/PV与完整投影+FFN矩阵MAC份额，4K/8K/16K时分别约8.0%/14.8%/25.8%，**不是时间份额**。真实Attention wall占比、exp暴露成本、资源替代PPA和强软件合法dispatch尚UNKNOWN；B200物理单元数不能靠软件修改，租用B200只可测原生机会门，不能直接证明iso-area资源交易。H原tile 4/3仅无面积约束的理论下界，不是性能收益。

## 2. 下一轮仅准备一条有针对性的CPU资格任务

**A74-C Goal：[SM100硬件近邻与固定预算资源取舍准入审计](goals/AI_ARCH_A74_C_ISO_PPA_RESOURCE_ADMISSION_CPU_SOURCE_109_V1.md)。**

| 字段 | 固定值 |
|---|---|
| 宿主建议 | node109独立新Codex窗口 |
| 执行branch | `hrl/aiarch-a74c-iso-resource-admission-109-v1` |
| **唯一固定启动HEAD** | `f5ac43b4eb6adc29d040bdf65993cbd7de063db5` |
| 科学目标 | 只核FA4正式版/最新合法source、B200↔B300硬件近邻、Qwen完整Prefill资源分母、可用面积/功耗与SM100模拟器语义；给出是否有**可实现、可证伪**的固定预算资源反事实。不得重复H的宽泛12篇筛选。 |
| 资源 | CPU/source-only、1个CPU工具worker、RSS≤2GiB、公开资料≤64MiB、新盘≤128MiB、60分钟收口；GPU/CUDA/模型权重/数据/安装/模拟器运行及清理全部0。 |
| 输出 | REPORT.md、PRIOR_AND_FEASIBILITY.tsv、DECISION.json、RECEIPT.json；可能正常结论是PARKED、DUPLICATE_NO_GO，不强求GO。 |
| 实际状态 | **READY_FOR_USER_DISPATCH，未启动。** 文档与分支创建不构成执行授权。 |

该任务之后，若硬件建模/PPA方法无法独立校准，不因论文动机强就启动B200或旧Accel-Sim；若确有必要的具体资源变量，再独立设计低成本原生机会门，并另批GPU/数据/Profiler/模型资产。W因缺同语义输入仍PARKED，不为保持双Lane并行虚增同质工作。

## 3. 冻结边界与协调方式

A70 M/N/O/P全部`NO_SURVIVOR_IN_SEARCH_SCOPE`但仅SOURCE_ONLY，原综述与Git审查见[A72](reviews/AI_ARCH_A72_A70_M_AND_FOUR_LANE_DISCOVERY_SYNTHESIS_2026-10-16_V1.md)。A61/A65/A67 GNN、A69 ScanNet/Q-S、C16、AWMA、ISCAS所有科学和资源合同原样保持。109共享GPU锁继续遵守，本轮无GPU操作。164没有访问任务；H/W本次STOP后不自动重启。协调分支只归档研究，不合并执行HEAD。

**本项目当前没有正在执行的新GPU/Codex作业回执；只有A74-C等待用户派发。**
