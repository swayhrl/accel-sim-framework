# B16 / S64 / Unified × OFF / MQ2 / RG1

`derived/matched_endpoints_TEMPLATE.json`列出Conv/FWT × 三架构 × 三单因素，共18个逻辑端点；`derived/matched_effect_comparison_TEMPLATE.csv`列出六行比较。全部新候选cycles为null、NOT_RUN；旧combined OFF只在`four_mode_OFF_context.csv`，没有填作新source锚点。producer先交MQ2时只接收相应OFF/MQ2子集；RG1未合法复现可保持未证实，不凑满18点。

Lane5已在原中央campaign登记`FINITE_SERVICE_MICROOPT_V1`阶段（03:03:55Z），18个pending logical cells、0个qualified runtime cells、0/24 stage starts，原campaign28/72。`LANE5_CELL_MAPPING.csv`将本分析标签准确映射到已存在的`MOPT_CONV/FWT_...` logical ID；`SERVICE_OFF/MQ2/RG1`是registry条件标签，本表H0是共同实验背景，二者不能混淆。Lane3不另建ledger、不登记重复cell；当前执行状态以中央registry为准。Lane5的live receipt与实际资源快照单独归档，不能据此升级科学acceptance。

每个workload的同源比较必须绑定准确Core、Framework、binary、完整输入trace内容身份、whole-commandlist/all epochs、计时/终止合同、instructions、H0背景、candidate发布及独立资格。不能因旧OFF cycles相同跨binary拼数。保留每点完整config SHA及effective dump；另审计一个移除“架构差异+所比较机制开关”后的背景projection，必须相同，移除的键和值逐项由Lane1/Lane5声明，不能宽泛忽略queue/clock/latency/WAD/ordering参数。三模式共享相同优化开关，不只给Unified用ON。

固定成本：总1168 payload/slice、四bank、P1每bank/physical-cycle一op。B16为1024 resident+128 bypass+16WB，S64为1024+80+64，Unified仍1168动态角色；S64不额外增48行。copy latch、WAD、lower/ICNT FIFO、额外selector/ready/token寄存器与时序由producer清楚列账。U_CAP16属于既有四模式归因，不是本轮第四个新增全应用维度。

令o∈{OFF,MQ2,RG1}，对同一workload和候选发行：

- `S_EP(o)=C_B(o)/C_U(o)`；`S_static(o)=C_S64(o)/C_U(o)`。
- `interaction_EP(o)=S_EP(o)/S_EP(OFF)`；`interaction_static(o)=S_static(o)/S_static(OFF)`。
- `absolute_speedup_A(o)=C_A(OFF)/C_A(o)`，A分别为B16/S64/Unified。
- 同时报原始cycles及差值；小于1、无触发、正常近零、资格失败、预算/空间未跑均原样保留。不能只取各模式最佳点再比较。

`util/ep_l2/service_opportunity_v1/effects.py`是很小的算术器：模板直接输入得到六行PENDING。填充导出须先由Lane5绑定最新immutable acceptance与独立review，再标记`LANE5_CURRENT_ACCEPTED_EXPORT`；算术器会拒绝源/输入/背景/接受generation不匹配，输出始终标为ARITHMETIC_ONLY，不能充当独立资格器。每次结果事件都重新核对current pointer/撤回，不常驻监听。

联合MQ2+RG1只在单因素完成、真实ready/等待证据支持、原剩余starts和deadline允许时提出；不能本轮自行启动。原预算72 starts、最多24新增full starts含锚点/重试、全局16GiB结果、deadline `2026-10-18T11:30:14.500719Z`，正式资源workspace≥48GiB、Share≥40GiB、availableRAM≥64GiB、4sim/8CPU/32GiB预约不变。只由Lane5登记/运行。

## 中文结论填充模板

观察：在[精确release/binary/trace]上，[case/应用]的[MQ2安全第二项机会/RG1完整cycle空转见证]为[N，分母和单位]；B/S64/U OFF→o的绝对cycles为[三对值]，S_EP为[x→y]，S_static为[p→q]，interaction为[j]。

竞争解释：下游full、同地址WAD排序、不同bank落点、frontend pending与机制可重叠；降低重试次数本身不确定GPU关键路径。若两侧同幅加快且interaction≈1，解释为通用有限服务优化；若相对差扩大，也仅在该同源输入/预算范围声称EP交互，不能拿B(OFF)对U(ON)。

受控对照：比较同binary的三模式OFF/MQ2/RG1及共同H0背景，检查ordering、P1、head恢复、oldREADY公平、ICNT背压、partial fill、UID/generation、WAD/drain。缺一个锚点或资格撤回则该ratio留空。

结论范围：正/零/负性能均保留；生产小case通过只证明合法触发及局部行为，两个开发输入不足以证明普适。没有真实时序见证时，只能说源码结构可构造，不能报告机会覆盖率、saved GPU stall或EP独有收益。

## English insertion template

On the same qualified candidate binary and input, [MQ2/RG1] changes the B16, S64, and Unified cycle counts from [OFF values] to [enabled values]. The corresponding EP and strong-static ratios are [values], with an OFF-normalized interaction of [value]. [Witness count and denominator] establishes activation of the local service mechanism; it does not identify exclusive GPU stall time. A common absolute improvement with an unchanged EP ratio strengthens the baseline rather than establishing a benefit unique to elastic capacity. Missing, withdrawn, inactive, and negative endpoints remain visible. These conclusions apply to the disclosed configurations and inputs only.
