# Codex Goal｜Lane F / node109｜R20R1 solver入口数值资格与条件性诊断

日期：2026-10-01。用户已批准。连续solve-and-continue；先资格，只有通过才实施一个有界candidate。ChatGPT发布handoff不代表节点已启动。

Repository：`swayhrl/accel-sim-framework`
Execution branch：`hrl/awma-r20r1-solver-entry-local-contract-109-v1`
Scientific parent：`50f8608898ec37a7e265bf3761d7bb236cdb3e88`
Stage：`AWMA_R20R1_SOLVER_ENTRY_LOCAL_CONTRACT_109_V1`
Review pack：`docs/vm_tlb/review_packs/AWMA_R20R1_SOLVER_ENTRY_LOCAL_CONTRACT_109_V1/`

## 0. 这不是重跑R20

R20的完整32步数值资格失败保留原样。本轮改变测量与正确性边界：真实碰撞/约束构造已经完成、即将调用`solver.solve(m,d)`的完整输入 → 本次完整solver输出提交。

先在一个入口做五次B0重复性检查，不写active-world candidate，不修确定性碰撞管线。局部合同若仍无法资格化，立即收口。通过后扩到事前指定的少量入口，再允许唯一一个在线active-world执行诊断。局部speedup不能冒充完整step或RL收益。

## 1. 复用、身份与硬边界

- MuJoCo Warp源码：`3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5`，基线只读。
- 环境沿用parent lock-derived组合（parent记录MuJoCo `3.13.1.dev984848064`、Warp `1.15.0`）；核实际receipt，不升级main、不全套重装。
- G1 hfield、shuffle_dance.npz、Menagerie `affef0836947b64cc06c4ab1cbf0152835693374`、原Halton/worldid/step控制生成与平滑/clip全部保持。
- B=1024、parent实际solver/cone/稀疏/compact/conditional分支、warmstart、timestep、iterations=10、ls_iterations=20及容差保持。不得换场景、batch、求解器或精度。
- 既有t128物理step入口：`DISCOVERY_ENTRY_FULL_DATA.npz`，SHA256 `17f59a5ebbedff9e544eb7c35cede114c3f9ec97b9b26d0ddfd363370bbcf6e3`。它不是solver-entry，不能改标签直接当作本轮输入。
- parent恢复工具：`util/vm_tlb/awma/r20_active_world/state_utils.py`及discovery/one-step脚本；工具按用途复用，旧输出不可覆盖。
- 所有CUDA初始化、JIT、capture、运行须持有`/data/c16/locks/c16_gpu_campaign.lock`。CPU检查可并行，GPU任务串行。
- 新工具/observer/candidate独立opt-in，默认OFF；OFF恢复本轮冻结B0，不修改共享安装或accepted源码。

缺文件先区分科学payload与可重建包装。派生wrapper可由accepted依据确定性重建并标记DERIVED；真实payload/唯一身份不可恢复才停。普通工程问题并入本轮，不另起修复Goal。

## 2. G0｜捕获一个真实solver入口

### 2.1 第一入口固定为t128

恢复parent t128 step入口，按原规则生成t128实际ctrl，执行原物理step上游，**在真实`solver.solve(m,d)`调用前**冻结状态。通过源码依赖核实调用点，不假定做完`make_constraint`就已拥有全部solver输入。

优先在原图中插入只读GPU snapshot拷贝节点，分别保存solver入口和B0出口见证，随后让原B0完成。也可用最小分段harness，但必须保留全部上游工作、真实分支和控制依赖。捕获仅用于产生输入，时间不作为性能数据。

需明确：这是本轮从accepted状态/原源码生成的**新B0 realization**，不是保证重现parent某次完整轨迹的逐bit历史原件。snapshot拷贝可能影响原子执行顺序；不能因此宣称对32步轨迹逐bit中性。不得挑选多个realization中最稳定/最困难/最快者。

捕获成功的第一个合法realization即冻结。记录源commit、model/options、step/world身份、ctrl、GPU/driver、调用点与完整数组哈希。若原输入存在真正容量丢失、NaN或不可恢复身份，不通过丢world、缩约束或换轨迹修复。

### 2.2 冻结的是数值问题，不只是contact ID

保留实际所有solver读取的Model/Data/嵌套数组及别名关系，至少审计：
- contact的实际顺序、world映射、有效几何/物理浮点参数和EFC引用；
- EFC行顺序/type/id、有效J值与稀疏rowadr/rownnz/colind、D、aref、其它实际读取的约束参数；
- M/分解与索引、qfrc_smooth、qacc_smooth、qacc_warmstart以及实际路径的睡眠/compact映射；
- 求解器选项、每world标量和只读model参数。

这是依赖审计清单而非所有字段必存在的断言。对全部Data使用parent的保守snapshot枚举，对Model记录不可变依据；新增或未枚举依赖必须补齐。有效区之外的scratch不凭NaN/uninitialized值判物理错误，但必须证明不会读到。

不排序、正则化、用CPU重建或替换EFC/J数值；分析端可canonicalize辅助比较，但**实际replay必须消费捕获的原字节与原顺序**。相同标签集合不能替代完整有效数值与布局身份。

### 2.3 SolverContext与graph-local scratch

Data中的138项恢复不是全部graph-local状态的证明。审计`_create_solver_context`、`init_context`、nsolving/done、incremental/search缓存及本路径临时区：哪些每次调用初始化、哪些在读取前覆写、哪些只在capture时分配。

正式B0捕获完整`solver.solve`，包含必要初始化、实际compact gather/scatter、最终约束力恢复/Ma刷新等；不得只计`_solver_iteration`。不把本应每次支付的清零、初始化或收尾搬到timer外。

若正确replay必须增加原路径没有的清零/改变solver，则不是普通snapshot包装修复；先报告原路径缺口，不静默修基线并宣称原solver已资格化。只为审计scratch可增加一项小型正确性测试，不能进行确定性算法重写。

### 2.4 入口/出口见证

从该冻结入口，独立捕获同一完整solver的conditional graph；复核无每轮host标量取回、无每次recapture。恢复数据应写回已捕获指针，而不是重新绑定Python数组让graph读旧buffer。

比较原调用的B0出口见证与isolated B0，验证相同有效约束、模式、数值/停止语义。输出至少涵盖qacc、qfrc_constraint、solver_niter、EFC force/Ma以及所有下游实际读取的solver写入字段。不需要在本轮滚动物理integrator32步。

若无法建立真实边界/完整依赖/有效见证：`R20R1_SOLVER_ENTRY_NOT_QUALIFIED`，STOP。

## 3. G1｜五次B0重复性先决定是否继续

对固定t128入口，**每次完整恢复相同输入后单独执行一次solver**，共5次；不是连续调用5次让状态演化。再用一个独立新capture作一次出口见证，限制单图scratch依赖的解释。新图不能单独证明不存在全部隐藏依赖。

重复性检查在正式计时前完成：
- 每次有效solver输入位模式/索引/opts相同；
- 相同world集合、有效约束数/类型/引用覆盖；
- 相同每world solver_niter、已有停止/limit签名；
- 没有新增容量丢失、NaN/Inf或意外model/input修改；
- qacc、qfrc_constraint、EFC有效输出/下游字段的逐bit比较及field-wise误差。

overflow可能含继承的sticky标志：保留入口值，区分新置位与原值。没有精确停止原因时标未知；不得把done或nsolving=0当作全部容差收敛。

### 数值合同只允许两条路线

A. 有效输出与停止签名在B0重复/独立图中逐bit稳定：本轮candidate相对匹配B0要求这些字段逐bit一致。

B. 浮点输出有小幅变化，但有效约束、停止签名/迭代数稳定：在看candidate数值/计时之前，写入`LOCAL_NUMERICAL_CONTRACT.md`。逐字段给出有依据的绝对/相对/归一化误差界与实际solver目标/残差比较规则，引用baseline重复统计及固定源码/测试的适用依据。不能只把观察到的最大误差任意乘系数，不能照搬通用1e-2，也不能把最大迭代终止包装成达到数学最优。

局部合同须仍能识别漏world、漏约束、旧输出、提前停止等显著错误；用离线validator负例验证这点，不改变科学payload。B0自身通过不等于candidate可任意重排world内算术。

若相同入口下迭代/停止签名变化、输入/隐藏状态不能闭合，或无法给出有判别力且有依据的局部数值界：`R20R1_SOLVER_BASELINE_NOT_QUALIFIED`，STOP。不得继续写S1、做性能profile或打开H。

## 4. G2｜少量真实入口；不扩成新的轨迹研究

t128资格通过后，仅增加事前指定的发现入口：**128、136、144、152**，每个仍包含全部1024 world，不按复杂度选world。

这些入口来自同一次原B0源码realization按原控制规则推进的[128,160)轨迹。尽可能在G0捕获t128后继续同一realization并暂存t136/t144/t152输入，先不测其分布；或从保存的同一生成状态继续。若仅能重新生成，先固定一条新realization并对其t128重资格，不把不同来源静默拼成同一次轨迹。

每入口5次B0重复；沿用G1规则。所有四个入口数值/停止签名都须通过后才能写candidate。G1为非bitwise模式时，用B0-only四入口数据定完统一field-wise局部合同再冻结；不能在candidate结果出来后扩容差。任一入口失败则报告全表并停止，不能筛掉失败入口。

记录实际activity、约束分布和停止上限，但不要继承parent的0.3733为本轮replay实测值。新snapshot仅是同作者回放一个realization的局部实例，不称RL训练分布。

如果四入口根本没有目标多轮活动变化，停止为`R20R1_TARGET_NOT_OBSERVED`，不调整原控制/step选择。

## 5. G3｜资格全部通过后，才放行唯一一个在线软件诊断

本轮只允许一个固定配置、一个完整连续solver子阶段的active-world-ID/有限worker执行诊断。以源代码与轻量阶段观察选择子阶段；不要求先证明5%理想headroom。不通过密集参数搜索挑方案。

实现前写一页`DIAGNOSTIC_CONTRACT.md`，记录函数、B0/S1差异、在线信息来源、成本和数值规则。使用当前ctx.done等生成列表，不使用预存niter、未来active轨迹或事后已知完成时间。world ID和原数据布局保留；不变更world内算术、约束、warmstart、收敛条件、迭代上限或solver算法。

CUDA Graph中“active_count位于GPU”不自动意味着launch维度可动态改变。必须说明实际减少了什么：固定worker循环、device条件、grid-stride或其它真实支持路径；不能只换索引仍发射同量任务却宣称消除所有launch成本。队列/list生成、reset、间接寻址、同步、scatter全部计入。

只允许最多两次局部correctness/liveness修复；若需重写solver、第二个算法、确定性碰撞/EFC排序或改变数值合同，则`R20R1_ACTIVE_WORLD_DIAGNOSTIC_NOT_QUALIFIED`，STOP。

OFF恢复B0；observer与candidate开关分开。相同冻结入口的B0/S1须通过已冻结合同，并保持每world迭代/停止签名，不通过提前结束或少做约束获得收益。对zero-active、all-active、no-constraint和迭代上限边界可用小型正确性canary；不计为新科学batch/性能样本。

## 6. G4｜主指标是完整solver，且不伪造应用上下文

候选通过后，对四个入口分别测B0/S1：3个paired groups，每臂每组2次warmup、5次未插桩formal sample，组间交替臂顺序。每个样本均恢复该入口，恢复/输入拷贝在共同边界外，GPU同步与完成判定一致。

主区间：固定solver输入就绪 → 完整solver输出提交。两臂包括初始化、实际条件迭代、candidate全部维护成本和原收尾输出工作。记录wall/event、所有样本与median/MAD，子阶段数据只作解释。

恢复显存数值不能恢复硬件cache/TLB；snapshot拷贝也可能预热。B0/S1采用相同声明的restore/preconditioning策略，不给单侧额外预热，不称“原应用自然cache状态”。编译、capture、首次建立和restore成本单列。

整体发现指标用四入口median时间之和计算相对变化，同时保留各入口结果；不平均挑选有利百分比。发现集同向且有稳定净改善>=5%才进入下一节；这是本轮追加验证投入门槛，不是硬件收益证明。若低于门槛或无收益，报告有界软件诊断结果`R20R1_ACTIVE_WORLD_NO_MATERIAL_GAIN`，不宣称全部调度空间为零。方向不稳或误差与差值不可区分则`R20R1_RESULT_MIXED_NEEDS_REVIEW`。

R20先前step时间是observer-only，只能作背景，不能把solver-only相对变化乘旧占比后宣称完整step提升。本轮不做完整32步B0/S1性能比较。

## 7. G5｜只为survivor使用封存窗口

仅在candidate、局部数值公式/阈值、timing规则全部冻结后，生成H=[384,416)中固定**384、392、400、408**四个原B0 solver入口；输入生成仍用同一scene、原控制与固定源码，不用candidate轨迹生成输入，不按耗时挑选realization。

这是同scene时间留出，不是独立机器人或RL任务。H入口先按冻结规则做B0重复性/依赖资格，不调阈值。baseline失败或candidate数值失败均保留，不替换入口，不再调candidate。数值全部通过后，重复同一B0/S1配对计划。

若未保持稳定方向或>=5%完整solver净改善，使用MIXED并保留发现结果；若通过，`R20R1_ACTIVE_WORLD_SOLVER_RESPONSE_REPRODUCED`，表示真实solver-entry上有可重复Native软件响应，仍STOP等待审阅。没有自动硬件/174准入。

## 8. 范围、profiling与小问题策略

全轮最多1次NSYS：仅在B0数值资格通过后用于选择/核实完整子阶段；若前期已用完，不再为candidate补第二次。无需profile也能闭合时不跑。NCU/NVBit/SASS/Accel-Sim均为0。本轮不是微架构优化。

不下载新scene/模型，不换B或扫描容量，不扩大solver迭代数，不训练policy，不把全部collision/constraint管线改成确定性。环境与source小包装修复可自主完成；真实算法/身份/数值合同变化则STOP。

补充口径直接纳入本轮文档，不另开修正轮：qpos是混合坐标，没有统一米单位；parent的overflow不同可能包含sticky ITERATIONS/LS_ITERATIONS，不能直接称容量丢失；同semantic标签集合也不证明全部数值输入相同。原review pack/raw不改写。

## 9. 交付与STOP

最小交付按实际达到阶段生成，未触发项写NOT_RUN，禁止伪造空表为通过：
- README.md、FINAL_DECISION.md、PARENT_AUTHORITY.json；
- SOLVER_ENTRY_CONTRACT.md、SNAPSHOT_INDEX.tsv、RESTORE_AND_SCRATCH_AUDIT.md；
- B0_REPEATABILITY.tsv、LOCAL_NUMERICAL_CONTRACT.md、同入口in-situ/isolated witness；
- 触发后才有DIAGNOSTIC_CONTRACT.md、NUMERICAL_COMPARISON.tsv、TIMING.tsv、HOLDOUT.tsv与patch；
- RUN_RECEIPTS.json、RAW_DATA_INDEX.tsv、SHA256SUMS。

报告先用中文写：观察什么、数值合同是否成立、干预是否实际执行、结果支持到哪里、是否值得继续。内部label保留但不用PASS数量代替科学判断。

状态/raw沿用node164发布链，新根建议`.../provenance/awma/r20r1_solver_entry_local_contract_109_v1/`，实际路径由既有publisher绑定。109保留活跃副本；不经174本地盘stage大文件，不重做大传输canary。对parent资产引用已有accepted哈希，新增payload才做新闭环。

完成本轮独立commit、push、fetch-back/remote SHA-tree验证、释放GPU锁、退出本轮GPU进程、worktree clean后STOP。HTTPS失败依次用既有HTTP/1.1、SSH、API备用通道发布同一commit，不因传输失败重跑实验或改写科学内容。
