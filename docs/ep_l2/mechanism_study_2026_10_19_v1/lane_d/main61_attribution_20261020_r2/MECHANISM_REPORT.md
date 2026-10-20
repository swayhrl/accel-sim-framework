# Conv main61定量机制归因 r2

**本配对证明复制服务消失、真实RO准入/合并/MSHR分配避免发生；未证明明显的下层流量节省、成功Tag detach或广泛victim直接读取。** S/F整体GPU时间改善0.50194%，但各模块边际cycles与关键路径归因仍UNKNOWN。先行短报已独立发布 `d1cf657f77e7a4cd85b2088cc70bab723462b82e`，本版补完整表、图和候选审查。

## 准确证据与比较边界

E2 fetch HEAD `498426c672739bb0ff681287374e49df74dc0361`；正式配对 `V2_MAIN_convolutionSeparable_S_F_MAIN61`，S `E010_1108e4d2` / F `E009_76e25c1e`。F使用E重新验证的COMPLETE_VALID回执，旧FAILED回执保留，不覆盖。正式资格S `73d2efae3c7fc445ae4179c720e87c149a2fc7a3fb9de686f62de78e9074a4f6` / F `9c9683f57610b15ef9a880767085f50692a507bf8720031d773db6203c61c57e`，两者绑定同一runtime，各自当前无资格HOLD。

- binary `61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5`；Core `d010911e3174a3764791183cd108fe4664ba8731`；Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`；vendor `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`。
- 输入 `620f80f945d8ddbcef639e7e374fd2cb7122f8b07f239c82ccd32a2c4d90e79f`，Conv size3072，全2kernel、714,547,200指令；完整host预热与命令顺序保留。
- S config `c580439cf91da7adcd5b4e6989b357800584a74810ff8000ec5673d4dd1cdd6d`，run-key `103ad56f222a51f1d6ac6a7d8adaf3690e1b368e0a5c36eb9eab6e7bbba08560`；F config `02fa921fbda91774ca32a9a246966cf944efa60ea869b1c6abf3feb17a8b5427`，run-key `164a20a271de78137093686e162eb2023f0eb8b3e62b8b1f2b6b4ef7c17b6e98`。
- E确认nonresearch配置一致，4bank/P1、1168payload、128共享WAD/TVD、512descriptor、128line-MSHR及32per-address不变；两端无理想化豁免；F固定W/V/T/M全开，不逐应用选择子方案。
- S raw SHA `104cb7245fae11f55d8932e4db1ebd7debe95898e46078e4f84cd7637fafb44a`；F raw SHA `3f868be10f1261b2441d6b264257c7f27cd6dc9c7c96d89985f7e05456863641`。本轮读取复核其SHA。两端完整输入、正常结束、64slice闭合由E接受；D不重新宣布native正确性。

程序cycles **292,932→291,469，节省1,463**；相对S的周期下降0.49943%，S/F加速0.50194%。下述是全应用累计**最后**64slice记录，绝不把中间kernel累计快照相加。输入/指令匹配不意味着两个时序下L2请求数完全相同：E测得unique_requesters S5,216,912 / F5,211,802，各自exact-once闭合，不能对不同运行的UID建立未经证明的一对一反事实。

## 实际统计：W与物理bank服务

| 指标 | S | F | F−S |
|---|---:|---:|---:|
| 逻辑copy read | 546,865 | 0 | −546,865 |
| 逻辑copy write | 546,865 | 0 | −546,865 |
| 真实物理bank grants | 9,217,033 | 8,118,075 | −1,098,958（−11.9231%） |
| WB创建＝真实lower接受＝完成 | 546,865 | 546,813 | −52 |
| lower read次数 | 2,359,526 | 2,359,460 | −66 |
| lower read bytes | 75,504,832 | 75,502,720 | −2,112 |
| lower WB bytes | 69,787,264 | 69,826,496 | +39,232 |

实际每bank累计授权（全64slice，各物理bank编号）：S `[2880914,2118622,2109347,2108150]`，F `[2013820,2018155,2041331,2044769]`。逐slice/bank原记录及raw行号见BANK_SERVICES_512_ROWS.csv；两端分别与总grants相符。服务落点更均匀是实测事件分布，不是每bank利用率、同时峰值或bank关键路径占比。

**源码推导**：冻结ft-cache.inc中phase0 COPY_READ、phase1 COPY_WRITE均调用实际bank request；本配对诊断豁免均0，正常完成的复制走付费物理P1服务。W消除的逻辑服务为1,093,730次；物理总授权差还包含其他路径随时序变化的事件，不能把总授权差全归为W独立贡献。源函数及行号/原blob哈希在EXACT_CORE_COUNTER_SOURCE.json。

**实测可得**：下层read+WB合计145,292,096→145,329,216B，净**增加37,120B（约0.02555%）**；不能把copy消失解释为大幅减少DRAM流量。这里的lower接受边界是MissQ选中的请求通过lower_ready后执行m_memport->push并调用lower_accepted，**不是DRAM控制器已服务或外部显存物理带宽**，也不是DRAM总线饱和、延迟或GPU等待的直接测量。

## 实际统计：V读取、promotion、保留与额外目录成本

S V关闭，无V原生记录，表中S为UNKNOWN/OFF而不是伪造实测0。F：

| 指标 | 实测F |
|---|---:|
| 直接victim读响应 / dirty pending-inflight转发 | 36 / 0 |
| 服务sector / bytes | 36 / 1,152 |
| promotion | 1,152 |
| clean安装 / dirty安装 | 499,725 / 546,813 |
| clean保留slot-cycles | 495,404,215 |
| dirty在途/完成态保留slot-cycles | 1,778,784,962 |
| 两类保留总slot-cycles | 2,274,189,177 |
| frontend目录CAM查询 / completion CAM查询 | 1,181,110 / 546,813 |
| indexed WB accept / rollback | 546,813 / 0 |
| native install commit / promotion commit | 1,045,985 / 1,152 |
| 查询等待 / WB等待 / bank等待 / icnt等待计数 | 1,181,110 / 538,426 / 2 / 0 |

**源码推导**：read_responses仅计已实际commit的直接victim读，dirty_forward是其中pending/inflight转发子集；promotion迁回resident后的后续普通命中不在此列，因此“36”不等于整个V机制所有潜在复用收益。安装计数含dirty promotion创建的新WB，native install commit与其统计scope不同，不强迫两者相等，也不把安装次数当唯一地址数。retention_slot_cycles仅累加WB_INFLIGHT/WB_COMPLETE，clean单列，均是容量驻留积分，不是请求停顿或命中数。最后仍保留128可选TVD条目/slice是有效缓存状态，E硬件闭合要求的是无mandatory/WAD/请求/返回/瞬态，不要求清空所有有效缓存line。

V frontend及completion各1个已计预算CAM查询端口；frontend至少1个物理GPU周期查询延迟；indexed控制读视图/更新lane为3/3，WB UID字段32bit，extra packet identity bits0。这些是准确源码/终端声明的控制成本，**综合面积、功耗、时序闭合UNKNOWN**；旧R3不能当作完整设计PPA。completion/native indexed计数由本工具从E接受且SHA一致的raw最后记录投影，未建立新验收器。

**结论限制**：本Conv直接读取复用证据很小，不能以保留积分大就声称V高命中或节省下层流量；也不能仅凭36次shortcut响应就排除promotion改变后续resident行为。需要原矩阵F_MINUS_V/F对照后才能量化边际程序时间。

## 实际统计：RO准入、MSHR绕过、detach、merge及lower

| 指标 | 实测F |
|---|---:|
| 接受global reads / oracle候选 / 实际RO准入 | 2,852,506 / 1,386,184 / 1,251,551 |
| 新RO事务 / merge / RO响应 | 371,495 / 880,056 / 1,251,551 |
| 避免line-MSHR分配 / RO正常line分配 | 371,495 / 0 |
| 开启detach / 成功detached事件 | 每slice为1 / 全应用0 |
| 实际RO lower sectors / bytes | 1,179,774 / 37,752,768 |
| 同时重复lower sectors / bytes | 0 / 0 |
| 真实RO bank fill / response操作 | 1,179,774 / 1,251,551 |
| RO查询 / 查询等待 / 端口拒绝attempts | 1,251,627 / 1,251,627 / 0 |
| 单slice RO事务峰值范围 | 63–88 |
| 单slice shared descriptor峰值范围 | 127–326（预算512） |
| 单slice RO issued-not-returned lower事务峰值范围 | 63–74 |

**源码推导与范围**：RO实际准入约占接受global reads的43.8755%；merge占RO准入约70.3172%，是同一RO事务上的实际waiter合并，不证明“相对S少发880,056次lower”。避免line分配只在新RO事务bypass时加1，371,495不等于避免了同量阻塞，也不是GPU周期。attached Tag命中/普通resident hits可解释候选与RO准入不是同一集合，但各fallback原因的精确分解在此UNKNOWN，不凭差额发明归因。

RO duplicate仅检测同line其它活事务已有issued的相同sector；0只说明此统计域没有同时重复，不能宣称整个trace没有重复读取。37,752,768B已包含在F所有lower read bytes内，不能再加一次。RO peak以各slice峰值最小/最大表示，绝不把不同时刻的64个峰值相加成同时全局峰值；同时全局峰值UNKNOWN。

查询端口每slice1、物理GPU周期延迟1。query_count与实际准入略有差别，查询是事件计数，不是程序停顿。T配置ON而detached0，说明该输入此运行未发生成功脱离，不能由RO整体准入宣称Tag解耦获得收益。0成功detach不证明其它输入没有机会。

## 实际统计：等待、bank与queue变化

| 原因 | S首次阻塞请求 / 请求等待cycle和 / max | F首次阻塞请求 / 请求等待cycle和 / max |
|---|---:|---:|
| COPY_PIPELINE | 546865 / 546865 / 1 | 0 / 0 / 0 |
| WB_DATA_SPACE | 33572 / 848913 / 293 | 0 / 0 / 0 |
| DATA_SERVICE | 394444 / 433239 / 8 | 326935 / 357749 / 3 |
| MISS_QUEUE_FULL | 97090 / 180063 / 51 | 98263 / 590686 / 62 |
| LINE_MSHR_FULL | 1824 / 40088 / 302 | 6058 / 150118 / 346 |
| SAME_ADDRESS_WB | 925 / 638854 / 2332 | 749 / 538426 / 2402 |
| BANK_COMPATIBLE_LANDING | 0 / 0 / 0 | 10442 / 81928 / 531 |
| WAD_FULL | 0 / 0 / 0 | 207 / 5987 / 192 |
| VICTIM_LOOKUP | 0 / 0 / 0 | 1181110 / 1181110 / 1 |
| READONLY_LOOKUP | 0 / 0 / 0 | 1251627 / 1251627 / 1 |

TAG_SET_PENDING、DESCRIPTOR_FULL、PER_LINE_CAP、PINNED_PAYLOAD、FRONTEND_TRANSACTION、RESPONSE_QUEUE_FULL本两端观察均0，不外推所有输入。所有原因全表保留在MECHANISM_MEASUREMENTS.csv。F另有2次unclassified refusal观察，不假定已完成穷尽原因分解。

**必须保持的单位边界**：不同请求的时间区间会重叠；同请求不同原因会交替或重叠；不同slice并行。原因wait和不能相加成为GPU程序停顿，也不能把S−F各项和解释为1,463cycles。Observer的reason sum是首次阻塞至该原因解除的请求时间，不必等于该原因每次retry/观察数；ANY_FIRST_BLOCK_TO_ADMISSION只给首阻塞至准入的请求跨度，仍不是GPU关键路径。V内部WB538,426与frontend SAME_ADDRESS_WB同来源；RO query_wait与READONLY_LOOKUP、V lookup_wait与VICTIM_LOOKUP是同一事件的不同投影，不能重复算成本。

## 因果假设与下一步实验决策

C独立的S-only审查（提交 `1eb8f5254c5e4bc12e4519476a997a6e11a97ec4`）补足机会定位：当前Conv S单slice line-MSHR峰值128，descriptor峰值425；真实同set reserved Tag最大7，小于16way，TAG_SET_PENDING观察0。说明**存在实际M资源压力证据，但尚无已观察到的T满set瓶颈**；早期guard可能遮蔽后续检查，不能证明生产中T机会不可达。哪些已认证RO请求与1824个line-MSHR首次阻塞请求重合仍UNKNOWN。

**源码事实**：sticky reuse_seen在成功merge后置true，普通128B parent的sector siblings和跨parent复用都可能置位；detach要求T开启、attached、!reuse_seen且仍有未ready sector，并由真实set压力触发。**假设而非实测**：siblings保护可能抑制Conv T。现有输入模型不提供L2 parent/到达顺序，未测sibling比例，不能用该推导解释全部detached=0或擅自放松guard。

M已避免371495个RO line分配，而全F LINE_MSHR_FULL等待仍从40088增至150118，这并不矛盾：native/non-RO流量、时序和W/V背景也变化，缺少UID/时间交集及同背景M-OFF对照。不能把“避免分配”改写为“避免同量全局阻塞”。B独立W/V画像 `78e69a54` 与C独立T/M画像均已接收；排序只采用它们的S/输入模型字段，详见候选报告。

**假设H1**：少copy服务降低本地竞争，但原来复制未必位于应用关键路径，故11.92%服务下降只产生约0.5%程序收益。**H2**：新增1周期V/RO查询、bank兼容landing与更高MissQ/MSHR请求等待可能抵消局部收益。**H3**：Conv保留很多payload却直接读取少，是V复用机会或保留策略不足的候选解释；真实reuse-distance/地址级阴影证据未具备。这三条均不能当已量化因果结论。

优先增量接收E原计划FWT配对，比较输入压力/真实触发/服务需求和总cycles四层是否对应；然后才按已登记矩阵审查同binary F_MINUS_W/V/R或T/M factorial的独立资格，用实测边际cycles检验假设。当前这些控制尚未获资格，D不创建应用任务。候选选择依据和原七/新增分组在CANDIDATE_DECISION.md，不按可见F加速筛选。

## 增量接收与图表接口

复用full_v2_analysis.py：直接消费E accepted_pairs/accepted_results及每端准确qualification，支持同runtime不同parser/资格revision；保留当前资格撤回、输入HOLD、exact SHA与七输入共同binary检查。无E可选display binding时从明确profile投影，不要求E增加第二台账或验收流程。拒绝模糊同条件多配对，不按cycle最优选择。

输出MAIN_SEVEN_S_F.pdf/png、convolutionSeparable_MECHANISMS.pdf/png、14格覆盖/27比较、MECHANISM_MEASUREMENTS.csv。未测格保持UNKNOWN；Btree仍HOLD；新探索不进入七输入均值。主图仅同main61的一对实测，7/7均值UNKNOWN。母稿EN-v20未改。本轮无GPU/原生模拟/编译、无原五输入或DWT重扫。
