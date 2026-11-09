# AI-ARCH｜当前科研协调状态

**最新导航：2026-11-09，Q1 已完成且有限结论获科学窗口接受。** Q1 执行固定于 `5787826ca21f7af958e6e1c1f828d62fd58a1ec4`，完整交接固定于 `00abf55d44ad02a18d529eb0afe4d02dc0ceadfe`，独立审阅固定于 `06355f73caaa6f38697d9acac94ac81a47c27e62`。科学窗口接受的是晚期原生窗口、20 样本独立复算及已声明的有限收据范围；不升级完整训练质量或硬件因果。新 [状态供给反事实 Main 报告](https://github.com/swayhrl/accel-sim-framework/blob/be7fe374c1402498eeab3d3f3be97a9eb01667ab/docs/ai_workload_research/reviews/AI_ARCH_Q1_STATE_SUPPLY_COUNTERFACTUAL_MAIN_V1/REPORT.md) **待科学窗口审查**，尚未执行新 GPU 实验。当前仍为 `NO_GPU_PROBE_READY / NO_HARDWARE_CANDIDATE_PROMOTED`。

协调分支是科研导航，不是统一实验代码主干。此次只选择性登记已接受 authority 和研究决策，没有合并历史执行分支，没有改写 raw、数值 FAIL、旧 STOP 或其它项目合同。分支存在不表示任务在运行。

## 当前研究组合

| 优先级 | 对象与科学状态 | 下一步及边界 |
|---|---|---|
| PRIMARY | 3DGS GS-Scale/Rubble；Q1 完成，有限晚期 T16 窗口已获独审及科学窗口接受 | 当前 CPU-only 状态供给研究已由 Main 发布、待科学窗口审查；`shN` 驻留仅为一个未执行的判别方案，不自动启动 GPU |
| SECONDARY | 动态 KV/Hybrid State；A70N SOURCE_ONLY，NO_SURVIVOR_IN_SEARCH_SCOPE，审查范围 STOP | 真实模型、自然会话、运行时与质量资格仍缺；资格调查不自动成为下一首选 |
| CONDITIONAL | MoE A30T：SOURCE_QUALIFIED_PROBE_CANDIDATE / H200_SM90A_CONDITIONAL；A70O 源范围 NO_SURVIVOR | H200 与真实同格式 FP8/natural route/强软件都需资格；109 SM89 不替代，没有设备预约 |
| PARKED | Qwen V8–V11 已完成，V11 NO_HARDWARE_CANDIDATE_PROMOTED | 成熟负载分析基点；保留真实性能、机制计数、局部因果边界和原数值负例，不自动 V12 |
| PARKED | Low-bit A81、VLM、DiT、GNN 储备、source serving/iso-PPA/RL | 各自 source/native/条件/STOP 范围不变；不凭模型已下载或旧工程投入自动复开 |

完整固定来源见 [authority 索引](AI_ARCH_RESEARCH_AUTHORITY_INDEX_V2.md)；[已接受组合包](https://github.com/swayhrl/accel-sim-framework/tree/f88e40123f4060328aa50a16d22fa328cee51cfe/docs/ai_workload_research/discovery/AI_ARCH_NEXT_STAGE_PORTFOLIO_REVIEW_V1)。

## Qwen：已完成的 native 证据与不可外推处

最终执行 authority：339559f6972f25ac1aec78fb3577b7bd2640410e，tree c8c8391a6a0c83294ae4b6441e8c8d130180ffd2。[V11 报告](https://github.com/swayhrl/accel-sim-framework/blob/339559f6972f25ac1aec78fb3577b7bd2640410e/docs/ai_workload_research/runs/QWEN_DENSE_MEMORY_MECHANISM_CONVERGENCE_109_V11/FINAL_REPORT.md)。

V9 有18点90 formal，B1/B2约10.125/10.448ms每额外 token，R约1.0318448。V10/V11 测得对应 Dense 节点实际读取接近一份权重 payload，B2并未翻倍；不能把节点乘层数叫整应用 DRAM，也不能把条件191.31GB模型当 counter。V11局部只读数据状态反事实仅部分归因 B2；B1 reuse 失败、写驱逐混杂、共享桌面遥测和 trace 覆盖限制均保留。

原 logprob 阈值 FAIL 不改成 PASS；V8分离数值敏感性与性能有效性，LP_NONE不能标作数值通过。altered eager 的边界不等于 native 最早分歧层。最终 NO_HARDWARE_CANDIDATE_PROMOTED，不新增硬件机制。

## 3DGS：真实证据与接续条件

**2026-11-09 当前更新。** Q1 `5787826c` 已从真实连续生产取得 C_D、C_V、C_FINAL，完成 8 个预热、20 个正式样本、T8/T16 OFF/ON 分池和自然 camera 独立验证并 STOP。独立审阅 `06355f73` 的有限结论已获科学窗口接受：T16 相对 T8 的两个闭合窗口时延分别低 `12.1397%/12.1350%`，但 T16 本来就是原基线；ON 主线程 CPU Adam 加参数转发约占窗口 `75%`，不能替代 OFF 归因。状态末端保留下一步 pending；数值敏感、共享资源和终止 RSS 缺口保留。新 Main `be7fe374` 将 `shN` 驻留列为唯一待判别方案，但容量、GPU 新增工作、完整 OFF 收益与数值资格均未实测，待科学窗口审查。

以下 A26GR1 和 Q1 执行前缺状态／规划说明是**2026-11-06 历史导航**，固定旧报告保持原义；不能再作为当前 Q1 未执行判断。

执行 authority cf80f6ec07a31eccdaff264c3bce64e0511179f8，tree c66008a9da553d06a00195c8c133c3e7ec16692d。[报告](https://github.com/swayhrl/accel-sim-framework/blob/cf80f6ec07a31eccdaff264c3bce64e0511179f8/docs/ai_workload_research/runs/AI_ARCH_A26GR1_GSSCALE_RUBBLE_109_V1/FINAL_REPORT.md)。两次真实 Rubble 从零至15200步，不同 Gaussian 轨迹不能当配对速度试验，未证明长期收敛。

A44已将旧跨线程30.871/32.128ms收窄为主线程候选并集14.084/14.746ms，不能当纯GPU等待或硬件加速上界。A45H/A46是已接受 CPU/source 反证，不是新训练。OMP16不是作者64线程性能复现；实际Torch、OMP、cpuset与P/E/SMT需在获准执行内核验。

当时现存 splat-only 不具有完整 optimizer/counter/RNG/camera/deferred-state 恢复资格；后续 Q1 已按独立合同实际生产完整 late state，详见本节当前更新。旧 A26GR1 终态不变。

历史 sampled RSS约24.53GiB，累计持锁3734.497s覆盖两次推进及其它步骤；Qwen16GiB/30分钟草案不能直接套用。历史48GiB也不是新授权。新的主机、存储、连续GPU窗口和CPU placement申请以独立Q1合同为准。

## 历史入口与负结果保留

- **[A80 原始完整快照（固定 commit，不变）](https://github.com/swayhrl/accel-sim-framework/blob/ed365741b230718f6ffc1ccbed125fc2566aac15/docs/ai_workload_research/CURRENT_STATE.md)**。其中“新 native=0”和“主问题仍为Qwen”只代表2026-10-26状态，已被后续执行更新，不能覆盖 V8–V11。
- A79 final 1ad28dbe2fe7280aea46a24f6ba9a97c021b08b7 / tree9ed5906e445923e6ac8ee600093c23acbf0b987b：CPU预资格通过，唯一非阻塞锁冲突，GPU_RESOURCE_DEFERRED / STOP，formal0；A80独立接受。**不是性能负例**，也不证明今天GPU占用或空闲。
- [A80独立审查](reviews/AI_ARCH_A80_A79_GPU_LOCK_DEFERRED_INDEPENDENT_REVIEW_2026-10-26_V1.md)、[A78 Native↔Sim NO_GO](reviews/AI_ARCH_A78_A77_W_S_RESOURCE_PAIRING_INDEPENDENT_REVIEW_2026-10-16_V1.md)保留；A77资源轴0、Native↔Simulator未配对不变。
- A70 M/N/O/P、A73 W/H、A74-C、A75 R/D 的 source STOP；A30T条件设计；A81 NO_REAL_TENSOR_AUTHORITY；GNN A61数值STOP、A65 compiled不对齐、A67/A68 scoped eager FULL软件反证和后续 PARKED_BY_USER，详见索引。
- C16 Stage A TERMINAL_PARTIAL、四DQ不完整、B4/Observer旧STOP与AWMA原数值/复现负例全部不变。协调更新不覆盖独立项目 authority。

## 权限与运行状态

EP-L2、DTC-L1、AWMA、C16活动任务均 **NOT_QUERIED**。本轮不查询GPU活动raw、不访问164、不操作Image-Lab，不作实时空闲断言。本导航和Q1合同发布都不自动授权GPU、训练、Profiler、下载、安装、时钟/功率更改、模拟器、RTL或旧Goal恢复。完成本轮Git回读后STOP。
