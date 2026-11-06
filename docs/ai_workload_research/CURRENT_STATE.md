# AI-ARCH｜当前科研协调状态

**最新导航：2026-11-06，Q1 3DGS 主线接续。** 用户已接受研究组合包 f88e40123f4060328aa50a16d22fa328cee51cfe（tree 03274c2ddb7c45aff4bd7ad1f7d48fca94e4a48f）及其更新提案，授权本次协调导航更新与一次性 Q1 Goal 定稿。**本轮 CPU-only；没有新 GPU 授权、GPU 初始化或取锁。** 组合审查结论仍为 **NO_GPU_PROBE_READY**，Q1 合同需新的明确资源批准后才能执行。

协调分支是科研导航，不是统一实验代码主干。此次只选择性登记已接受 authority 和研究决策，没有合并历史执行分支，没有改写 raw、数值 FAIL、旧 STOP 或其它项目合同。分支存在不表示任务在运行。

## 当前研究组合

| 优先级 | 对象与科学状态 | 下一步及边界 |
|---|---|---|
| PRIMARY | 3DGS GS-Scale/Rubble，A26GR1 真实训练和 A44/A45H/A46 限定解释；旧 Goal 已完成 STOP | 一份连续 Q1 Goal：合法完整 state 检查；没有则在未来获准窗口从真实初始状态连续推进并建立 checkpoint/恢复资格；同状态线程/流水、observer OFF/ON、完整更新及 drain、独立 camera 验证。不是本轮训练授权 |
| SECONDARY | 动态 KV/Hybrid State；A70N SOURCE_ONLY，NO_SURVIVOR_IN_SEARCH_SCOPE，审查范围 STOP | 缺真实自然会话、完整模型/运行时/质量资格，不因 config 或代码存在恢复 |
| CONDITIONAL | MoE A30T：SOURCE_QUALIFIED_PROBE_CANDIDATE / H200_SM90A_CONDITIONAL；A70O 源范围 NO_SURVIVOR | H200 与真实同格式 FP8/natural route/强软件都需资格；109 SM89 不替代，没有设备预约 |
| PARKED | Qwen V8–V11 已完成，V11 NO_HARDWARE_CANDIDATE_PROMOTED | 成熟负载分析基点；保留真实性能、机制计数、局部因果边界和原数值负例，不自动 V12 |
| PARKED | Low-bit A81、VLM、DiT、GNN 储备、source serving/iso-PPA/RL | 各自 source/native/条件/STOP 范围不变；不凭模型已下载或旧工程投入自动复开 |

完整固定来源见 [authority 索引](AI_ARCH_RESEARCH_AUTHORITY_INDEX_V2.md)；[已接受组合包](https://github.com/swayhrl/accel-sim-framework/tree/f88e40123f4060328aa50a16d22fa328cee51cfe/docs/ai_workload_research/discovery/AI_ARCH_NEXT_STAGE_PORTFOLIO_REVIEW_V1)。

## Qwen：已完成的 native 证据与不可外推处

最终执行 authority：339559f6972f25ac1aec78fb3577b7bd2640410e，tree c8c8391a6a0c83294ae4b6441e8c8d130180ffd2。[V11 报告](https://github.com/swayhrl/accel-sim-framework/blob/339559f6972f25ac1aec78fb3577b7bd2640410e/docs/ai_workload_research/runs/QWEN_DENSE_MEMORY_MECHANISM_CONVERGENCE_109_V11/FINAL_REPORT.md)。

V9 有18点90 formal，B1/B2约10.125/10.448ms每额外 token，R约1.0318448。V10/V11 测得对应 Dense 节点实际读取接近一份权重 payload，B2并未翻倍；不能把节点乘层数叫整应用 DRAM，也不能把条件191.31GB模型当 counter。V11局部只读数据状态反事实仅部分归因 B2；B1 reuse 失败、写驱逐混杂、共享桌面遥测和 trace 覆盖限制均保留。

原 logprob 阈值 FAIL 不改成 PASS；V8分离数值敏感性与性能有效性，LP_NONE不能标作数值通过。altered eager 的边界不等于 native 最早分歧层。最终 NO_HARDWARE_CANDIDATE_PROMOTED，不新增硬件机制。

## 3DGS：真实证据与接续条件

执行 authority cf80f6ec07a31eccdaff264c3bce64e0511179f8，tree c66008a9da553d06a00195c8c133c3e7ec16692d。[报告](https://github.com/swayhrl/accel-sim-framework/blob/cf80f6ec07a31eccdaff264c3bce64e0511179f8/docs/ai_workload_research/runs/AI_ARCH_A26GR1_GSSCALE_RUBBLE_109_V1/FINAL_REPORT.md)。两次真实 Rubble 从零至15200步，不同 Gaussian 轨迹不能当配对速度试验，未证明长期收敛。

A44已将旧跨线程30.871/32.128ms收窄为主线程候选并集14.084/14.746ms，不能当纯GPU等待或硬件加速上界。A45H/A46是已接受 CPU/source 反证，不是新训练。OMP16不是作者64线程性能复现；实际Torch、OMP、cpuset与P/E/SMT需在获准执行内核验。

现存 splat-only 不具有完整 optimizer/counter/RNG/camera/deferred-state 恢复资格。新用户指令明确允许把“无完整状态时从合法初始状态连续推进到晚期”纳入**未来一次性 Goal 的待批准分支**，更新上一版仅缺状态即停的规划，不改变旧 A26GR1 终态。完整状态生产、恢复验证和实验不再人为拆成小 Goal。

历史 sampled RSS约24.53GiB，累计持锁3734.497s覆盖两次推进及其它步骤；Qwen16GiB/30分钟草案不能直接套用。历史48GiB也不是新授权。新的主机、存储、连续GPU窗口和CPU placement申请以独立Q1合同为准。

## 历史入口与负结果保留

- **[A80 原始完整快照（固定 commit，不变）](https://github.com/swayhrl/accel-sim-framework/blob/ed365741b230718f6ffc1ccbed125fc2566aac15/docs/ai_workload_research/CURRENT_STATE.md)**。其中“新 native=0”和“主问题仍为Qwen”只代表2026-10-26状态，已被后续执行更新，不能覆盖 V8–V11。
- A79 final 1ad28dbe2fe7280aea46a24f6ba9a97c021b08b7 / tree9ed5906e445923e6ac8ee600093c23acbf0b987b：CPU预资格通过，唯一非阻塞锁冲突，GPU_RESOURCE_DEFERRED / STOP，formal0；A80独立接受。**不是性能负例**，也不证明今天GPU占用或空闲。
- [A80独立审查](reviews/AI_ARCH_A80_A79_GPU_LOCK_DEFERRED_INDEPENDENT_REVIEW_2026-10-26_V1.md)、[A78 Native↔Sim NO_GO](reviews/AI_ARCH_A78_A77_W_S_RESOURCE_PAIRING_INDEPENDENT_REVIEW_2026-10-16_V1.md)保留；A77资源轴0、Native↔Simulator未配对不变。
- A70 M/N/O/P、A73 W/H、A74-C、A75 R/D 的 source STOP；A30T条件设计；A81 NO_REAL_TENSOR_AUTHORITY；GNN A61数值STOP、A65 compiled不对齐、A67/A68 scoped eager FULL软件反证和后续 PARKED_BY_USER，详见索引。
- C16 Stage A TERMINAL_PARTIAL、四DQ不完整、B4/Observer旧STOP与AWMA原数值/复现负例全部不变。协调更新不覆盖独立项目 authority。

## 权限与运行状态

EP-L2、DTC-L1、AWMA、C16活动任务均 **NOT_QUERIED**。本轮不查询GPU活动raw、不访问164、不操作Image-Lab，不作实时空闲断言。本导航和Q1合同发布都不自动授权GPU、训练、Profiler、下载、安装、时钟/功率更改、模拟器、RTL或旧Goal恢复。完成本轮Git回读后STOP。
