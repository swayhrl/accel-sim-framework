# Codex Goal｜Lane F / node109｜R20活跃world资格与Native合并轮 V1

日期：2026-10-01。用户已批准，连续solve-and-continue到科学STOP。**本文件授权节点执行；ChatGPT发布文档不表示节点已启动。**

Repository：`swayhrl/accel-sim-framework`
Execution branch：`hrl/awma-r20-active-world-native-109-v1`
Design parent：`fb0da17a135f5f8485871abe1fbab66640fa8dcf`
Stage：`AWMA_R20_ACTIVE_WORLD_NATIVE_109_V1`

## 0. 一个问题、一个主生产者

问题：MuJoCo Warp已有done-mask、device条件图和相关solver优化之后，活动world集合缩小是否仍有可避免的完整物理step执行成本？

Lane F/109是唯一生产者；Lane E、G继续STOP。约束容量只复用同一数据记账，不另做allocator、容量扫描或第二环境。

本轮是具身学习环境计算，不是LLM推理、策略训练或微架构模拟。允许一个有界软件诊断用于问题发现；不授权硬件/Accel-Sim/trace。

## 1. 资源、authority与执行边界

所有CUDA上下文创建、JIT、capture、physics step、计时、NSYS/NCU先取得：
`/data/c16/locks/c16_gpu_campaign.lock`

先查设备、显存、CPU、内存、磁盘与node164通路；不打断其他campaign，不kill别人的进程。CPU下载/源码/解析可以并行；本轮GPU正式样本严格串行，不能以增加并发提高计时噪声。

- 109隔离worktree/env/cache/output，建议置于`/data/c16/awma/r20_active_world_native_v1/`下，先核实际可写空间。
- Durable建议根：`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r20_active_world_native_109_v1/`。109使用已有publisher/SSH通道，不假定该绝对路径已挂载本机。
- 大资产、状态与raw不入Git，不经174本地临时盘中转；复用已合格发布链，不重新搭平台或重跑旧大canary。
- 源码固定MuJoCo Warp `3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5`。依赖从该commit的lock/pyproject解析并冻结；不一边测一边更新main。
- 新instrumentation、candidate开关独立opt-in，默认OFF。OFF必须恢复本轮固定B0。

## 2. G0｜源码、依赖与小canary，合格后立即继续

先读本目录SOURCE_BINDINGS，复核关键blob；无需全仓库逐文件审计。优先最小环境与本scene所需依赖，不安装训练/渲染框架。

记录MuJoCo/Warp/Python、实际CUDA构建/JIT/runtime、GPU UUID/SM、驱动、包或wheel哈希。固定源码pyproject声明的最低版本不是某个已验证wheel组合；优先复用兼容exact环境，否则隔离安装。允许两个有记录的依赖/构建修复尝试；仍需更换solver源码/硬件才可运行则STOP，不偷偷降到旧弱基线。

使用同一scene的B=16工程canary，不将其计入科学性能矩阵。验证：
- NPZ与资产可加载，step有限且无丢数据的容量overflow；
- 图捕获/replay成功，device条件节点真实生效；
- 暂无条件图时可用于排障，但不得成为正式强B0；
- 支持源生done-mask、实际启用的incremental/stable-state/sparse/compact等不被删除；
- 无逐迭代host标量取回，graph没有每step重建；
- JIT/capture单列，任何canary对状态的改变随后恢复。

没有合法runtime：`R20_RUNTIME_NOT_QUALIFIED`。可运行但无法建立强conditional graph路径：`R20_GRAPH_EXECUTION_NOT_QUALIFIED`。两者都不是问题不存在。

## 3. G1｜唯一真实输入和工作点

### 3.1 场景与控制

固定：
- `benchmarks/unitree_g1/scene_hfield.xml`；
- 同目录`unitree_g1_mjlab.xml`、`hfield.png`、`shuffle_dance.npz`；
- benchmark descriptor指定的Menagerie revision `affef0836947b64cc06c4ab1cbf0152835693374`及必要资产。

核所有include与实际load文件，发布哈希。不生成随机qpos/qvel，不训练policy，不改flat scene作为科学fallback。缺包装可由固定源确定性重建并标DERIVED；真正缺NPZ/关键identity且无合格副本则`R20_INPUT_OR_BASELINE_NOT_QUALIFIED`。

沿用固定cli.py原`load_trajectory`初始化与`_ctrl_noise`：noise_std=0.01、noise_rate=0.1、原Halton/worldid/step规则、原控制平滑与clip。给原runner和新runner一个短同输入对照，验证生成ctrl一致；不把NPZ控制中心直接当最终ctrl。

输入分类：`AUTHOR_BENCHMARK_REPLAY_WITH_DETERMINISTIC_CONTROL_PERTURBATION`。这是作者公开benchmark工作负载，不称真实RL策略rollout分布。若没有活动异质性，本轮STOP，不改扰动强度、挑相位或困难状态来找positive。

### 3.2 固定配置与容量资格

作者XML的timestep=0.005、iterations=10、ls_iterations=20、implicitfast、eulerdamp disable保持。实际solver/cone/tolerance/Jacobian由load后dump冻结，不通过换CG/Newton/降低容差改变问题。支持的graph_conditional显式开启并验收；其它已有默认优化保持。

科学B优先1024，仅在allocation/capture峰值无法保留至少20%设备显存余量或确实OOM时单向尝试512、256。只采内存canary，不先看速度再选B；最终只保留一个B，失败点仅是平台receipt。小canary B16不冒充第二科学shape。

nconmax=48、njmax=192起步，naconmax/njmax_nnz/nccdmax等实际默认全部记入。只在真正容量overflow时允许一次安全修复：对受影响的容量项上调到原值2倍，重建Data/capture并从原输入重新资格化。若需要更多容量轮次，STOP审查。禁止缩容、忽略overflow、截断接触、丢约束。

ITERATIONS/LS_ITERATIONS属于停止/精度边界，单列计数；它们不是自动等同于缓冲溢出，也不因此放宽容差或迭代上限。上限终止不能写成收敛；若本轮几乎只观察到上限终止，应保留censored解释。

### 3.3 窗口事前冻结

NPZ控制长度为L。若L<64，输入不足以支持本合同，STOP，不换文件。

令W=min(L,512)，K=min(32,floor(W/8))。
- 从t=0按原driver连续生成输入与状态；
- 发现窗口D=[floor(W/4), floor(W/4)+K)；
- 留出窗口H=[floor(3W/4), floor(3W/4)+K)。

上述索引0-based，均按长度选择，不按solver分布/耗时选择。发现前为真实轨迹前缀，不是性能warmup。H的performance/solver分布不能用于挑方案；可登记hash与索引，只有第8节允许后才运行H验证。H是同scene的未参与调试时间窗口，不称独立机器人/独立训练分布。

## 4. G2｜恢复、数值与观察工具先过小检查

### 4.1 状态恢复

每个formal repeat均恢复同一发现窗口入口，随后按时间顺序执行K个step；不能循环执行修改后的状态却当相同样本。

至少核qpos/qvel/act/qacc_warmstart/ctrl/time及实际程序跨step读取的mocap、外力、eq_active、plugin/user、sleep/awake与solver缓存状态。**清单是审计起点，不是断言这些字段全部存在或全部必需。**由源码依赖证明哪些是authority状态，哪些scratch能在正式step内部完整覆写。不能只复制qpos/qvel就假定全状态恢复。

允许调用已有状态API或snapshot GPU arrays；若重新生成derived状态，需要证明next-step结果/控制/停止签名重现。不能把应计入step的工作搬到restore之后、timer之前来变快。恢复/输入发布是共同测试准备，计时排除并单列成本；不能把GPU缓存状态恢复到某个理论值。

用5次B0同入口重放核可重复性：物理状态、控制、有效约束、各world停止原因/迭代数。若逐bit确定，候选保持相同；若基线因合法原子/归约非确定，则先保存baseline envelope，并在看candidate数值/速度前冻结field-wise门槛及solver残差要求。不能仅因baseline波动就无限扩大容差；无法给出有物理依据的可接受范围则STOP。

### 4.2 观察分离

优先复用solver_niter/nefc/overflow等已有字段。需要逐迭代active计数时，在独立observer图写GPU数组，退出测量后一次取回，不每轮同步CPU。记录entry-active数、completed-by-tolerance和limit-stopped数；不能只取最终nsolving=0说全部收敛。

新增observer ON/OFF做小型语义中性检查。正式性能图关闭新增重型observer；观察图的wall/event时间不作为formal值。源码已有event_scope/EventTracer可以用于粗定位，但嵌套区间不能累加重复算时间。

## 5. G3｜轻量现象与容量账本，同一批数据完成

对完整发现窗口、全部world记录：
- 每world/step solver_niter、停止原因、有效约束数、实际active DOF（若该路径具备）、相关overflow；
- 每迭代入口未完成world数A_j及对应最大solver轮数；
- 完整物理step时间、整个solver/少量主要substage时间；
- 实际全world launch维度与done处理入口。

结构量可报告sum_j(A_j)/(B*J)，J为该step实际发起轮数，J=0记N/A。它不是SM利用率、浪费周期或speedup ceiling；不同world每轮成本不同，禁止把它的倒数当理论加速。

容量账本共用同一发现数据：nconmax/naconmax/njmax语义、实际nefc/contact分布、alias去重后的持久数组/solver临时工作区字节、哪些路径会触碰这些数组。unknown bytes/traffic单列。**不做容量A/B，不缩njmax，不新建ragged allocator，不从allocated bytes估DRAM流量。**

如果所有world在每轮始终同进同出，或没有相关多轮求解，结果为`R20_TARGET_HETEROGENEITY_NOT_OBSERVED`，仅限该输入/窗口。若都被上限截断、无法回答真正收敛差异，报告censored/UNKNOWN并用MIXED，不武断称无异质性。

有活动集合收缩时，不要求先证明>=5%理想headroom才允许小原型。下一节只在存在具体被mask但仍发射的执行入口、且改动有界时继续。没有实际干预的资料，不足以声称“强软件已彻底解决”。

## 6. G4｜只允许一个在线活跃world执行诊断

### 6.1 先冻结小patch计划，随后自主实现

在本轮pack写一页`DIAGNOSTIC_CONTRACT.md`：选定的完整solver子阶段、涉及函数/输入输出、已有近邻能力、B0/S1差异、列表维护/映射/同步成本、正确性规则。

选择范围：**一个完整、连续的迭代子阶段**（例如实际路径中的gradient/search更新族），或只有当改动同样小才能覆盖整个迭代体；不重新设计碰撞检测、线性代数算法、integrator、contact model或RL调度。

第一选择为在线active-world ID列表/有限worker执行。列表由本轮真实ctx.done等当前状态生成，整个过程中保留原world数据布局，逻辑ID不变；必要时有限重映射作为显式成本。不用离线k_i/未来完成时间/后续step状态，不按未来难度排序。

只有一个固定candidate配置。最多两次局部correctness/liveness修复；需要第二套候选、重写整个solver或换数值合同才能继续时，以`R20_ACTIVE_WORLD_DIAGNOSTIC_NOT_QUALIFIED`收口。记录可行性与阻碍，不说问题无性能空间。

### 6.2 不能伪装动态发射能力

capture后的kernel grid不会因为Python里的nsolving变小就自动改变。S1必须使用实际支持的device执行路径，例如固定有限worker grid按GPU上的active_count/ID列表取任务，保留每world内部线程/归约组织；或另一个可验证的公开runtime机制。

不得把active_count拷回host重发kernel，再把新增host控制排除计时；不得把max-capacity grid改个索引数组就宣称CTA发射量已下降。明确分别报告active工作量、实际发射量、worker循环/检查量。

需要任务counter/列表reset、compaction/scan、间接索引、同步、publish/scatter的全部成本计入S1。不得遗漏终结恢复、对已完成world合法的清零/恢复写入或下一step必读状态。ctx.done与nsolving不能被候选调度改写成不同的solver停止判据。

按原world ID读取模型参数及modulo/broadcast字段，不能按compact slot误配物理参数。保持world内原方程和必要归约；不移除算术、减少迭代或只保留易收敛world。

### 6.3 Directed qualification

用同源有效状态/低成本fixture验证：全部active、一个active、全部done、交错ID/尾部、不同停止轮次、连续K step和完全reset。fixture只做正确性，不产生主性能结果。

C0身份映射/all-active路径应与B0匹配，用于排除重映射实现错误。正式主对照为B0对S1，收益解释为**在线列表维护+有限worker组织的净作用**，不是纯compaction或纯跳过成本。

不改每world初始值、控制序列、容量与停止规则。输出/有效约束/停止签名必须符合预冻结合同；若baseline确定，则iteration count和停止原因也要求精确。若baseline自身抖动，则使用预注册envelope，不能仅验证qpos close却忽略系统性更早停止。

## 7. G5｜正式配对计时

B0=固定成熟conditional-graph路径。
S1=同配置、同输入、同容量，仅启用上述一个有界软件调度诊断。

两个图均在warmup前捕获，建立相同输入/状态恢复协议；source/JIT/launch identity记录。S1编译、graph setup和一次性准备单列，逐step列表工作计入，不能把不支持的不同算法称相同consumer。

3 paired groups；每臂每组2次warmup、5次formal repeat；组间交换先后顺序。每个repeat重放完整K-step发现窗口，全部world共同推进，不让先完成world提前进入下一个policy动作。保存全部sample和组中位数、MAD。

三个时间口径分开：
1. R_step：当前step所有world的状态与实际ctrl已在GPU就绪 → step全部结果提交；所有solver迭代、终结和integrator都在内。
2. R_solver/selected-stage：次级定位区间，observer与正式样本分开，不把局部百分比冒充全step。
3. R_window：自然控制生成/发布加K个step的完整窗口墙钟；与sum(R_step)不同，不混分母。

ctrl路径B0/S1一致。允许预分配原driver每step重复创建的控制buffer并做原值一致检查，这是共同baseline工程复用；不能只给S1。

同时保存未插桩wall与合法CUDA-event时间。两者不应被机械相减并全部叫host成本。正式timing不包含hash、CPU统计或NSYS。

如果重新捕获、逐iteration host读、资源竞争或clock/温度漂移导致主要差异，应先做一次共同runner修复再重测受影响pair；不能删除不利样本而保持“稳定”标签。无法排除则MIXED，保存所有版本。

## 8. G6｜最多一次定向profile，有响应才做封存窗口

整个Goal至多1次新增NSYS，覆盖B0/S1短匹配区间。它可用于验证conditional/launch行为或解释net响应，不要求每个gate都采一次。若单个kernel仍需区分compute/memory，只允许从有效timeline选择1个NCU目标，先query SM89实际metrics；不以大stall百分比单独构造positive。profile可不触发。

进入H的默认投入筛选：
- 数值、停止/coverage、source/graph身份均合格；
- 发现窗口完整R_step聚合中位净改善>=5%；
- 三组paired相同正方向，聚合差大于两臂较大MAD的3倍；
- R_window方向不出现无法解释的相反结果，且增量不是第一次JIT/输入复制/算法工作变化。

5%是本轮投入门槛，不是普适真理或统计显著性证明。局部substage明显改善而完整step不足5%：记录`R20_LOCAL_RESPONSE_NOT_MATERIAL_AT_STEP_BOUNDARY`并STOP，不换batch寻找positive。

无稳定净改善：`R20_ACTIVE_WORLD_NO_MATERIAL_RESPONSE_IN_SCOPE`，只说明这个候选和窗口，不证明所有动态调度均无用。

满足筛选后，冻结patch/config/解释，从原B0轨迹继续生成此前未查性能的H入口；不得从S1已漂移的状态构造H。只运行同B0/S1、同B、同scene与同协议，不调参。比较全窗口及每step方向；验证阶段不再新选profile目标。

H在相同正确性规则下复现完整step>=5%、组方向与噪声余量：`R20_ACTIVE_WORLD_SOFTWARE_RESPONSE_PRESENT`。这只是值得审查的Native软件响应，**不是新颖性证明或硬件准入**。

H不复现、只在部分事后挑选step有效、或数值/终止行为不稳定：`R20_RESULT_MIXED_NEEDS_REVIEW`，不重开H调参。

## 9. 合法终点与解释

| 最终标签 | 中文结论 |
|---|---|
| R20_RUNTIME_NOT_QUALIFIED | 运行依赖或SM89能力未闭合，没有科学性能结论 |
| R20_GRAPH_EXECUTION_NOT_QUALIFIED | 无法建立所需强device条件图路径，不把弱host路径当基线 |
| R20_INPUT_OR_BASELINE_NOT_QUALIFIED | 真实输入、容量/恢复或物理数值基线未通过 |
| R20_TARGET_HETEROGENEITY_NOT_OBSERVED | 本次固定输入没有观察到目标活动集合变化；不外推全部物理仿真 |
| R20_ACTIVE_WORLD_DIAGNOSTIC_NOT_QUALIFIED | 有结构现象，但同语义有界干预无法完成；不是零成本结论 |
| R20_ACTIVE_WORLD_NO_MATERIAL_RESPONSE_IN_SCOPE | 已测候选无稳定完整step净响应 |
| R20_LOCAL_RESPONSE_NOT_MATERIAL_AT_STEP_BOUNDARY | 局部响应存在但没有达到完整step投入门槛 |
| R20_ACTIVE_WORLD_SOFTWARE_RESPONSE_PRESENT | 发现及留出窗口复现软件组织净响应，等待审查，不自动硬件化 |
| R20_RESULT_MIXED_NEEDS_REVIEW | 证据不一致、明显censored或预算停止后的未解决问题 |

只选一个最终标签，phase/admission状态另外记录。中文报告先说明观察和含义，不以PASS数量代替科研结果。

## 10. 发布物：必要即可，不另建管理系统

Review pack：`docs/vm_tlb/review_packs/AWMA_R20_ACTIVE_WORLD_NATIVE_109_V1/`
实现建议：`util/vm_tlb/awma/r20_active_world/`；上游源码补丁单独保存，不污染共享安装。

至少交付：
- `README.md`、`FINAL_DECISION.md`；
- `AUTHORITY_AND_FROZEN_CONTRACT.json`：source/package、GPU、scene/input、batch、solver/容量、窗口、图/状态/数值冻结字段；
- `STATE_AND_NUMERICAL_QUALIFICATION.md`：恢复清单、baseline重复性、停止规则、observer中性；
- `ACTIVITY_AND_CAPACITY.tsv`：全部发现step汇总及指向per-world raw的索引；
- `NATIVE_TIMING.tsv`：所有实际计时样本、明确region/arm/group/repeat；没有formal则不伪造表；
- `DIAGNOSTIC_CONTRACT.md`和exact patch、directed结果，仅在触发时；
- `HOLDOUT_RESULT.md`、`PROFILE_RECEIPT.md`，仅在触发时；
- `RUN_RECEIPTS.json`、`RAW_DATA_INDEX.tsv`、`SHA256SUMS`，复用既有通用schema。

真实payload、完整状态、NPZ、网格、raw与大日志进入node164；git只放代码/小型表/receipts。派生包装缺失先按P1/P2/P3/P4分级，由accepted authority可确定性重建的直接修复并标RECONSTRUCTED，不伪造历史hash。

## 11. 终止与排除范围

完成对应终点后释放锁、退出本轮GPU进程，提交/push/fetch-back验证exact SHA和tree，worktree clean，STOP。只报告实际运行到的阶段和未触发阶段，不靠预写状态冒充执行。

禁止：第二scene、第二科学batch、参数/solver扫点、额外phase挑样、policy训练、RL端到端收益、render、multi-GPU、容量A/B或ragged allocator、硬件机制、NVBit/SASS、Accel-Sim/174新任务、R19/R53等旧方向重开。

科学正确性不明、需要扩大模型/算法/数值合同、或实现变成大规模solver重写时STOP并交付已有证据，不等待用户回应再保持占锁。正常工程小修尽量合并本轮；剩余空闲时间不授权新问题。
