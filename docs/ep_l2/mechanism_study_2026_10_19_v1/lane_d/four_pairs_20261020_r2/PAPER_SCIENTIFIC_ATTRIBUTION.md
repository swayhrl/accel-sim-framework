# 四对正式结果的论文级科学归因 r2

**目前证据支持“服务/流量优化与GPU关键路径收益脱钩”，不支持“各模块触发即可带来相同比例加速”。** 四对已接受main61结果包含CFD近中性负向、DWT明确退化和SAD零V/RO直接触发仍变快。新增逐kernel定位排除了若干简单解释：DWT总landing/RO等待不能直接解释后段退化；SAD的大部分加速出现在复制尚未发生的prefix，不能归为copy消除。

本报告延续首版 `f96aca61f045c1877b4be323a24d2c8d236a4a67`；所有不利数据及旧Conv包保留。下文将实际统计、源码事实与因果假设分列；没有重跑模拟器、扫描trace正文或改EN-v20。

## 1. 正式数据与统计分母

E2准确权威提交 `13718839b515542f332eca6a845701a8dbb9a922`；三份完整D_MECHANISM_DETAIL_NOTICE与中央当前接受声明完全匹配，四对八端均由E独立接受。主binary `61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5`；Core `d010911e3174a3764791183cd108fe4664ba8731`、Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`、vendor `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`。四bank/P1、1168payload、128共享WAD/TVD、512descriptor、128line-MSHR及32per-address均保持；所有理想化/MQ2/RG1为OFF。F始终W/V/T/M全开，不逐应用选子方案。

| 输入 | S / F attempt | S cycles | F cycles | S/F−1 | F−S真实elapsed cycles |
|---|---|---:|---:|---:|---:|
| Conv | E010_1108e4d2 / E009_76e25c1e | 292932 | 291469 | +0.501940% | −1463 |
| CFD | E015_4cad4ae9 / E016_776b0d99 | 79093 | 79157 | −0.080852% | +64 |
| DWT2D | E017_2bc62654 / E018_67a874f4 | 166519 | 167643 | −0.670472% | +1124 |
| SAD | E019_f73a396e / E020_6fd11ee2 | 110773 | 109754 | +0.928440% | −1019 |

四对**临时、非完整原七输入**几何均值为 `1.001679474465`（+0.167947%）。这是等权四个S/F比值的几何均值，不是周期合并比、不含缺失应用补1，也不是旧H0五应用0.16%结论的重述/替换。原七应用分母仍7；FWT两端INCOMPLETE、Vector F资源终止、Btree输入HOLD，因此完整七输入GM仍UNKNOWN。SAD当前E019/E020来自main61，未使用旧已撤回sad证据。

八端准确config/trace/qualification/run-key/receipt SHA见首版CURRENT_ACCEPTED_PERFORMANCE.csv；逐raw观察身份见本版ACCEPTED_OBSERVATION_IDENTITIES.json。五项不同E qualification revision均为同source runtime、仅支持S/F；E_QUALIFICATION_IDENTITY_INDEX.json保留其当前引用及无HOLD状态。Conv F沿用E重验证的COMPLETE_VALID回执，未覆盖原FAILED文件。

## 2. 观察方法和可相加边界

继续用full_v2_analysis.py消费E accepted_pairs/accepted_results及资格，不建第二验收器。paper_four_pair_details.py只从已接受且SHA匹配的raw抽取原生gpu_sim_cycle、gpu_tot_sim_cycle和累计counter快照。没有读trace/SQLite或运行native路径。

**可以重建的elapsed时间**：每个命名kernel阶段的gpu_sim_cycle与最终剩余，在这八端逐一相加等于E接受的全程序cycles；对应F−S也精确相加。它定位“差异发生在哪个报告阶段”，不是新增关键路径因果分析。

**不能相加成程序stall的量**：请求首次等待和、slice观察数、不同原因、V/RO内部计数。不同请求与slice并行、原因可重叠；目录query_wait和frontend同原因是重复投影。相邻快照counter差是观察/解除事件的区间增量，不能将跨快照未决请求时间强行归给单个kernel，也不能把64个不同时间峰值相加。max是最大值而非可减累计量。数据缺失仍UNKNOWN；工具补充同时识别MSV1旧原因及MSV2查询原因，实际最终投影已与E接受值逐项一致。

## 3. CFD：49,962次V服务及51,678次M分配避免，为何近零变化

**实际统计**：F V读响应49962（1,598,784B），dirty pending/inflight转发101、promotion5595；RO准入206448，新事务51678、merge154770，避免line分配51678，成功detach0。物理bank服务1,638,275→1,570,678（−4.1261%）；lower reads212308→206462（少5846包），read bytes6,793,856→6,606,784（−2.7535%），WB bytes3,983,744→3,835,136。S line-MSHR-full首次阻塞与请求等待观察均0；不能将避免的51678次分配当成解除同量S阻塞。

**实际时间定位**：

| CFD阶段 | F−S elapsed cycles | F V查询增量 | F RO查询增量 | F V真实读响应增量 |
|---|---:|---:|---:|---:|
| 初始化1 | +14 | 15180 | 0 | 0 |
| 初始化2 | +1 | 15180 | 0 | 0 |
| 初始化3 | +34 | 15180 | 0 | 0 |
| step_factor | +29 | 6072 | 12144 | 0 |
| compute_flux | −14 | 109235 | 194304 | 49962 |

前四阶段真实时间净增加78cycles，最后flux只节省14，合计+64。全部49962次V服务在flux阶段快照增量中；这说明“有很多本地读服务”与“该阶段有巨大elapsed改善”不是同一个量。不能把该表的查询数换算为78或14cycles。

**源码事实**：目录miss/HIT路径与resident缓存状态、promotion、L1过滤及request到达顺序共同变化；F的V响应UID不能一对一对应S中的lower miss。一次V直接读与一次RO事务避免line分配也不是同一单位。V/RO查询各按实际一周期管线计费，V在RO前处理普通tag miss；配对所见所有请求的criticalness未知。

**受支持结论**：CFD确实少了bank服务和lower流量，但没有观察到S的line记录满瓶颈，且局部服务节省与新增阶段时间相抵。不能声称V命中无效，也不能声称M获得了实测关键路径收益。

**因果假设**：V/RO查询和队列时序抵消部分局部收益；S/F缓存与请求合并差异使49962次F服务只对应5846次净lower减少。该假设与数据相容但未由counter证明，需同背景WV/F或W/WV控制。CFD额外WV点作为有限后续备选，不因近零结果无限扩矩阵。

## 4. DWT：服务和流量明显下降，退化在何处

**实际统计**：V读23305（745760B）、dirty转发943、promotion0；RO准入39836、新事务9965、merge29871、避免line分配9965、成功detach0。bank服务2,522,456→2,173,230（少349226，−13.8447%）；lower reads388844→367166（少21678），read bytes12,443,008→11,749,312（少693696B，−5.5750%）；WB bytes均20,971,520。S没有观察到line-MSHR-full阻塞。

F新增BANK_COMPATIBLE_LANDING首次阻塞5099请求，请求等待和148372、max669；V查询311718，RO查询39836。与此同时COPY等待163840→0、WB空间30282→0、WAD等待41770→34、DATA_SERVICE93039→58897。所有方向均保留；不做等待和收支平衡。

### 更强的阶段证据，限制总量解释

| DWT kernel | F−S elapsed cycles | F landing请求等待和增量 | F V查询增量 | F RO查询增量 | F V读响应增量 |
|---|---:|---:|---:|---:|---:|
| 1 CopySrcToComponents | −151 | 146780 | 117447 | 39836 | 9184 |
| 2 fdwt53 192 | −92 | 535 | 60628 | 0 | 10982 |
| 5 fdwt53 192 | +768 | 718 | 68107 | 0 | 3139 |
| 8 fdwt53 192 | +599 | 339 | 65536 | 0 | 0 |
| 其余6阶段合计 | 0 | 0 | 0 | 0 | 0 |

说明：其余K3/K4/K6/K7/K9/K10真实时间变化为−8/−1/−8/+1/+15/+1，合计0。K1/K2节省243，K5/K8增加1367，最终净增加1124。最后剩余两端均0。完整10阶段表见PAIRED_KERNEL_TIMING_AND_SNAPSHOT_DELTAS.csv。

**关键新发现**：146780/148372≈98.927%的landing等待增量在反而更快的K1；主要退化K5/K8只有718/339的landing请求时间增量，相邻快照的请求数与等待和增量分别为718/718、339/339，平均约1个请求周期；这不是跨slice的GPU停顿时长。RO查询与9965次M分配避免全部在K1区间，此后的主要退化阶段没有新增RO查询。这排除了“把总landing等待或总RO查询量直接当后段退化周期”的解释。K8没有V直接读、没有RO查询、lower读字节仍4,194,304→4,194,304，却多599cycles；同时减少约65068次bank服务并新增65536次V查询，是最有辨识力的阶段证据。

**准确源码含义**：BANK_COMPATIBLE_LANDING来自dirty或无live victim的miss无法preview_free(RESIDENT,index%4)。它是**与所选Tag相容的物理payload槽位/生命周期容量条件**，不同于P1 bank服务端口冲突。真实ft_access会尝试回收同bank的可回收CLEAN或WB_COMPLETE；pending/inflight/pinned不可回收。全应用服务总数下降不保证请求到来时恰有同bank可用landing。源行号、回收及query顺序在FROZEN_SOURCE_PATH_AND_COUNTER_SCOPE.json。

**优先因果假设**：K5/K8仍付费V lookup、optional retention影响landing/替换状态，可能使关键请求变慢；早期RO准入也可能通过后续cache/payload状态产生间接影响。直接RO查询延迟不发生在K5/K8，但不能由此排除R的历史状态效应。现有统计没有UID等待区间到SM关键依赖的映射，也不能确认669最大请求就是关键warp。无论149k请求等待还是31万查询，都不能直接解释1124程序周期。

可证伪路径是完整epoch S→W_ONLY→WV(T/M OFF)→F：若WV与F的K5/K8都慢，R直接存在不是该退化的必要条件；若WV后段不慢，则调查早期R状态对后段的间接作用。W_ONLY与WV相差的是加入V后的净作用，仍包含查询、保留、服务与相互作用，不能把差值单独叫查询延迟。

## 5. SAD：零V读、零RO准入、零detach却加速，不能简单归W-copy

**实际统计**：V读/dirty转发/promotion/RO准入/RO事务/M避免/detach全部0；RO候选6272但查询0，说明实际RO新事务路径没有被执行，不能用离线396条ROline宣称RO服务收益。lower read bytes均12768，WB bytes均508800。复制读、写各3975→0；bank服务483611→475649，少7962（−1.6464%），接近但不等于7950次复制服务。F仍有69511次V查询和396次clean保留安装。

| SAD阶段 | S cycles | F cycles | F−S | S copy read累计快照增量 | F V查询增量 |
|---|---:|---:|---:|---:|---:|
| mb_sad_calc | 84641 | 83652 | −989 | **0** | 27127 |
| larger_sad_8 | 15076 | 15046 | −30 | **0** | 33908 |
| larger_sad_16 | 10957 | 10937 | −20 | 3975 | 8476 |
| 最后剩余 | 99 | 119 | +20 | 不作为kernel归因 | 不作为kernel归因 |

**必须修正首版粗假说的范围**：主要989cycles改善发生时，两端尚没有任何已计复制操作，lower read和WB发出也均0；该prefix只有12次物理bank授权差。复制事件后续才出现，不能倒因解释已发生的prefix改善。因此**“动态copy消除解释全部SAD加速”不成立**；这不等于排除W组织模式在首个WB前改变控制/landing身份的可能。

三条待检验假设：

- H_S-W：unified组织/原生控制路径，即使尚无WB，也改变landing/identity或调度时序。W_ONLY若复现首kernel改善支持该组织净作用；否则该解释不足。请A2先静态审查有无实际timed差异，不能把更多C++函数调用的host开销当GPU周期。
- H_S-V：V miss查询/保留改变请求节奏、到达/返回排序或缓存状态，可能改善部分关键warp的重叠，即使没有任何V直接命中。W_ONLY去掉V后若丢失改善，才支持“加入V的净作用”需要分析；仍不能证明单独查询有利，因它同时关掉保留等行为。
- H_S-interaction：R未准入仍有源级检查/epoch身份路径，或其他未隔离的状态相互作用。RO查询为0，只可排除实际RO查询/直接服务作为已触发收益，不能无需source/profile审查就断言所有R开启与关闭cycle等价。无重复配对方差证据，亦不主张统计显著性。

SAD W_ONLY是最小一条件证伪。可选后续S_COPY_FREE预计在zero-copy首prefix不会改变S的复制路径计费；若单独copy-free被用作诊断，须新profile资格/新config身份，不能作为正式W完整方案。当前不申请自动执行此额外点。

## 6. 四组Tag detach=0的统计边界及论文措辞

四组F各64slice均配置detach=1；全应用最后累计stats.detached和均0，本轮各中间完整快照也均0。Conv/CFD/DWT已有RO事务371495/51678/9965，SAD为0。即：并非RO完全没运行，也不是将T关闭后的零事件；是当前四个开启T的完整运行中**没有成功执行Tag detach握手**。

冻结transactions.h在确认T开启、attached、!reuse_seen、仍有未ready sector并通过tag identity核查后，先执行tag_detach再将stats.detached加1。merge会使reuse_seen sticky，sector sibling与跨parent重用都可能保护Tag；真实relief还依赖set拥塞。当前counter缺少relief尝试/被保护候选的UID分解，不能从成功0反推尝试0、机会0或生产不可达。也不证明T无检查/管线成本。

论文应将“主方案同时启用T/M”与“哪个机制在应用中实际触发并有时间收益”分开。**不得声称这四组性能提升来自成功Tag脱离、由M避免分配证明T有效、或T提高了实际Tag可用性。** 可主张M路径在三应用实际避免line分配，但关键等待收益尚待控制；V在CFD/DWT实际服务本地读并减少部分流量，净应用时间可近零或退化。T的应用性能贡献目前未获证实。PAPER_CLAIM_CORRECTIONS.md给出可直接供作者审阅的英文替代句，未修改EN-v20。

## 7. 最小控制及当前合法边界

CONTROL_INFORMATION_VALUE.csv按可识别性排序，JSON请求发E2/A2：SAD W_ONLY一项；DWT W_ONLY、F_MINUS_R两项；Conv原矩阵F_MINUS_R、WV_M两项。后者检验有实测S-MSHR压力时M的净作用，并可与既有F比较T添加的净作用。只使用已预登记输入，不以F加速挑新workload。

最小5条件中3项超原32矩阵，需明确科学范围/内部预算替换批准。当前20/40、剩余20仍对应原20格，不是自由加实验额度；原控制器STOPPED，无ready合格队列。所有新profile当前都未获精确独立资格，不能沿用S/F资格自动启动。A2先做静态prefix和landing/查询审查及准确overlay/受影响生产检查；E2独立资格、资源准入及决定合法执行子集。若涉及runtime代码变化，保留新source/binary身份并重新审视配对，不跨binary沿用main61基线。D不改台账、二进制或原论文。

## 8. 论文图表交付与复核

首版包含四个原生机制图、四对正式性能图、原七位置主图及全身份表；本版增加PAIRED_KERNEL_TIMING.pdf/png、DWT_STAGE_MECHANISMS.pdf/png、FOUR_PAIR_MECHANISM_SUMMARY.csv及24个阶段/剩余行、原始快照行号、资格索引、源码片段和control需求。每个负向结果保留。补充抽取不是native正确性证明；最终counter与E投影、elapsed重建一致性由ARTIFACT_VALIDATION.json记录。

没有将未知延迟、资源峰值或关键路径补0；没有新模拟、trace正文扫描、第二验收器或等待器。当前结论限于E接受的四个main61完整输入，原七GM和各模块精确因果周期仍UNKNOWN。
