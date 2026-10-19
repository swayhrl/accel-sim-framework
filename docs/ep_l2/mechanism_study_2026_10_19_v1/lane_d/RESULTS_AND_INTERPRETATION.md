# D：机会、触发、局部结果、完整程序时间

本轮新机制配对尚无E接受项。RESULTS_AND_INTERPRETATION.csv只接本轮E当前接受的完整同源配对；以下全部为明确分组的历史背景，不借用旧预算、不复活旧Goal。EN-v17未修改。

| 机制 | 基线瓶颈 | 实际触发 | 局部服务结果 | 完整时间与边界 |
|---|---|---|---|---|
| W 统一WB | source2309 B16：Conv845097、FWT890294、vectorAdd440161、CFD5、SAD0次WB-data拒绝重试；不同UID/等待分布UNKNOWN | 旧U取消copy，实际WB顺序record峰值Conv55/FWT37；record不是实际WB物理槽占用 | Conv逻辑RAM工作减少1092963；B的546865次copy对应1093730个操作，尚有其他流量差767。不能相减当纯copy反事实 | H0五输入B/U均值1.0016002037656606冻结；CFD为负；新的S_COPY_FREE与本地DATA_FREE尚未运行，不分解或相加成独占GPU周期 |
| V 动态保留淘汰数据 | 全部五输入及新增候选的真实L2序淘汰后可捕获重用UNKNOWN | 本轮实际retained hit未运行，不能写0 | lower读/字节避免、查询成本与mandatory回收UNKNOWN | CLEAN_ONLY与完整dirty版本分开；shadow机会不是真hit；没有应用收益证据 |
| R tag/MSHR | source2309十个H0 B/U端点的tag全pending拒绝均0；Conv line-MSHR B40088/U279404，其余原输入该拒绝0。不同UID/等待分布UNKNOWN | 新T/M detach/bypass未运行；全epoch RO资格尚无 | 有效在途、吞吐、重复同址读/lower字节UNKNOWN | Conv仅是有MSHR压力的候选，受阻请求是否属于可认证只读子集仍UNKNOWN；tag零计数只约束旧source/该输入，不能解释为所有工作负载无机会 |

分类YES/NO/UNKNOWN见OPPORTUNITY_TABLE.csv。NO仅表示该完整观测scope的对应计数为0，不是机制普遍无效。重试、bank/slice累计等待、WAD lifetime、记录占用与全程序cycles为不同口径；重叠原因不求和，64slice时间不相加。

## 输入选择：先于本轮新机制性能

2026-10-19T12:54:24.303578Z冻结两个核心诊断：convolutionSeparable(size3072，2kernels，714547200完整指令)和FWT(logK7/logD21，19kernels，791609344指令)。选择依据是传统WB/copy压力与合同默认，未按新机制speedup替换。

新增btree(mil+command，2kernels，444467849历史完整指令，809709439B trace)和dwt2d(1024x1024/f-5/l3，10kernels，148684429指令，423214689B trace)。command list新读hash匹配已提交清单，所有列出的body存在且字节数匹配；未重复完整body hash，E在运行前独立绑定。历史capture声明CUDA9.1及实际trace头binary version70分别记录，不从目录名猜工具链；应用源revision仍UNKNOWN。

旧C7e B0-Legacy(Coreece1a3a7/Frameworkf08d2ce8)只作传统输入压力背景，预算1152/256与本轮1168/512不同，不能当新baseline或继承资格。btree tag/MSHR-full0、per-address-cap674、scheduler0，适合作为较低压力的查询对照，不能以读指令多认证全epoch只读。dwt2d WAD-full74044、scheduler281249、tag/MSHR-full0，提供不同控制/下游压力；二者的victim机会均UNKNOWN。btree两kernel之间有host HtoD更新，C须按真实epoch处理，不能全应用白名单沿用。

完整候选包括spmv、scan、sgemm。spmv为因真实资格/完整性失败时的第一备选(34.5MB、旧descriptor压力361635)；scan有旧tag/descriptor压力但5.329GB/33kernels及更高运行成本；sgemm2.216GB/1.659B指令，literal capture script未找到。它们未被偷换成零机会，也不自动加入预算。dwt192x192是同应用规模，不另算workload。不重抓trace或复制大输入。

## 四模式、R19与旧MQ2/RG1：保留负结果和未运行

HISTORICAL_FOUR_MODE.csv仅含同binaryfb67的8端点。Conv B16/S64/U_CAP16/U=292932/293258/292544/291525；FWT=493189/494627/491696/491662。S64没有在这两输入更快；U_CAP16/B16仍有placement/组织差别，不能叫pure-copy。即使f0与fb数字相同，也不跨binary补对照。

HISTORICAL_R19_COMPLETE_10_PAIRS.csv保留独立审阅的十完整配对/20接受应用，21/24历史starts含失败重试，剩余3次不重启。HISTORICAL_H0_R19_PAIRS.csv为原Lane3的18历史参考配对，与十R19表有重叠，不能重复计入均值。减压和上游干预有正有负，WAD-control和本地WB-data生命周期分开，不能据重试总量决定关键路径。

HISTORICAL_MICROOPT_MATRIX_18.csv保留f0同binary17/18接受端点及FWT Unified RG1 NOT_RUN。六MQ2配对均cycles不变，64slice记录的MQ2 bypass均0，表明目标机会在这些应用未触发，不等于生产实现无效。Conv RG1 B16快609cycles，S64慢1386，U慢1592；FWT B16/S64持平，U未运行。五个已接受RG1 ON端点的256 bank-slice recovered_grants均0；不能把609cycles归因于跳过未ready持有者。旧Lane5明确指出RG1同时改变identity/age/phase与ready调度路径，零target-counter不证明无其他顺序变化。原正负测量保留，不冒称已证明因果，更不能外推新W/V/R机制。

## 本轮逐配对接收

单次读取E canonical registry中本campaign accepted_pairs/accepted_results，保留E路径、SHA、完整身份和接受状态；同source/binary/input与E确认非研究配置一致后计算带符号B/V及绝对cycles差。缺项UNKNOWN，未运行不填0；旧/片段/合成结果不进入新应用表。撤回从当前效果表移出但保留分析history，不覆盖原raw。

运行 util/ep_l2/mechanism_study_lane_d/sync_intake.py 即消费当前事件；无新pair不建后台循环。E若采用不同字段包装，只对原接受来源作确定性适配，不另建资格系统。当前0个新接受pair。D分析工具8项完整性测试通过，仅为工具测试，不是生产或应用结果。

续行接收边界：每pair还保留两端原profile/labels，特别是diagnostic/subset/oracle；复制vendor和E qualification/selection/invariant引用。真实目标计数与成本字典原样保留，即使当前字段名尚未映射四层，缺少映射也为UNKNOWN而非0。E内嵌冻结端点与当前accepted_results引用若不一致则只hold该pair；不能借新指针改写旧配对。E7434cbf09的实际配对构造测试已在临时目录与新版D消费者互操作PASS，未触及中央台账。
