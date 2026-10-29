# M/T机会、缺口与最小验证

本交付只复用15个Main已封存接受端点的小JSON；逐一回读bundle、point、archive和DONE的SHA。没有Trace/raw正文扫描、模型启动、注册表/Git写入，也不重新授予旧端点科学资格。精确来源与整数在MT_OPPORTUNITY_AND_GAPS.json。本表不是35/42/96全体覆盖；全体由Agent A/Main统一表维护。

## 结论与候选优先级

**PROVEN**：Vector6M efced2c… F有1,500,000个accepted RO requester、375,109个事务、1,124,891个live merge（74.9927%）。普通line-MSHR峰0与RO issued-not-ready独立line峰70/slice并存，前者不能解释为没有访存并发。Vector4M ddf26d…是另一个输入，不能以其时间线或sector复用直接填Vector6M。

**PROVEN**：SGEMM有1,135,915个accepted RO requester、81,582事务、1,054,333个live merge（92.8179%）；S每地址32限制有1,738次重复head检查、55个首次受阻UID。Conv S普通line-MSHR峰128，6,499次检查、696个UID；F仍有2,986次检查、337个UID。这表明M的独立line容量机会与同址merge限制应分别设计，不能统一用扩容line-MSHR解决所有情况。原因等待只到first-known-clear（ANY例外），不称独占GPU stall。

**PROVEN**：Vector4M32×4实际detach27；Conv16×8实际237、32×4实际1,141。对应F均慢于同几何S，仍**UNKNOWN** T自身收益。当前REF四pilot heavy全部OFF，LIFE_WIRE=SUMMARY_STAGE不提供完整NEW-at-R或Tag寿命。现有MS TAG_SET_PENDING不是生产TagFAIL。Source78旧timeline Conv-S的289 firstNEW-at-R8/42,717 preview是另一个开启observer的接受点；本文不把它塞进当前REF的联合格。

**UNKNOWN**：live merge里多少发生于本请求所需sector未ready、多少只是ready/draining；有多少事务首次merge置reuse_seen；正常与RO同时独立地址并集；同一新UID、同Set、同刻R==ways且结构eligible的机会。不能把RO merge边际和S满路边际相乘。RO pending峰、descriptor峰均为各slice最大值，不相加成GPU同步峰。

**HYPOTHESIS**：对Conv先判断独立line-MSHR等待是否实质改善，再考虑M资源；对SGEMM应先检查每地址merge与ready-only drain，不能从92.8%live merge推断严格Fill前复用；对Vector6M不优先增加普通line-MSHR，因为F已绕过它且现有数据未证明该处饱和。高merge对reuse_seen保护的限制只作假说，尚无同事件共现。

**建议**：总体先W/V（由Agent B交付）；M/T不启动新大矩阵。若用户审查后只批准一个T因果点，首选Conv16×8同Source78/ELF的F_MINUS_T，用已有合法F母点控制，保留完整硬件与证书。可验证T cycles贡献且不需要先造新collector。第二候选Vector4M32×4，Conv32×4仅作为更强压力备选，不为了detach继续缩容。新mode host/native/geometry资格尚未闭合，表中每行都是0授权候选，不自动累计成3次预算。WV=M0/T0不等于F_MINUS_T=M1/T0；无需为T单项控制另跑S。

## 最小新增计量工程：设计与纯参考，不接生产

新增指标的价值必须对应选定策略，不能先实现全功能地址分析器。建议分两档：

1. **T-only小钩子**：现有first-head/preview快照里读出真实UID、generation、目标set、R、结构候选数，结构谓词独立于T位；记录firstNEW、ever-full、repeat checks、真实Tag拒绝distinct ticks、head→admission和right-censor。guard不变，不新增probe/目录/银行动作。由已有RO mutation维护结构候选shadow，不能为观察周期扫way或复用含T开关的can_detach。必须审查attached、owner/generation、reuse_seen、required-not-ready、pin与实际协议保护的完整对应。
2. **仅若M策略需要**：真实push的parent/sector child身份、queue_enter、first-head分开。读到达前required-sector ready及issued状态，分别报requested-not-ready、issued-not-ready、ready-only-drain、line其他sector pending；normal/RO独立地址用事件refcount并集，overflow使exact失效。不能扫描FIFO倒推ingress，也不需要先做全地址reuse距离表。S不运行RO，静态membership只能绑定本输入已资格证书，禁止使用其可能指向Vector4M的dormant配置。

`mt_contract_reference.py`及13项测试是**纯计量语义参考**，已在本地Windows/Python3.12.10执行；没有链接任何Core/ELF/.a、没有生产hook，也没有宣称本地执行等于174 native资格。测试覆盖defaultOFF、边界去重、后继先到、firstNEW与everfull、T关闭仍有结构事件、结构UNKNOWN、generation/epoch保留、跨clock拒绝相减、同tick多child、overflow失效、部分sector ready、地址并集、同人口分母。未覆盖真实parent-child闭合、ROP/texture、生产mutation/生命周期/顺序和应用NI。

参考代码中的Python字典、set与线性遍历不是最终低开销实现，不允许接入生产。生产C++候选仍NOT_IMPLEMENTED、没有新Core/ELF。新hooks每路径CPU正确性、真实sizeof/对齐/输出上界和应用OFF/ON均NOT_QUALIFIED；≤16MiB状态、≤8MiBcompact、≤5%host overhead均为未测目标，不能用13项纯测试背书。

## NI与点数

先冻结实际启用路径：只采head的方案不用承诺ingress；不用V/RO的S不被迫做全部F/WV测试。若采集Conv/Scan-S需求、Conv/Vector6M-F实际M/T、FWT-WV的实际路径，则每一个启用模式分别需要CPU路径和同新ELF/同输入/同硬件/同模式OFF/ON控制。S不能覆盖F/WV，FWT不自动换RO-F。旧Source78 Vector4M ETNI只资格旧observer，不覆盖本参考或新hook。

新采集点数=N_ON+N_missing_exact_OFF；不能直接说4ON+1OFF足够。如新ELF四候选各一模式且无任何同ELF OFF控制，则四对=8点只是条件算例，非计划预算；如果只实现T-only，可收缩为一个合法F的2点OFF/ON，再另审因果F_MINUS_T/F。collecting NI和性能因果是两件事，若复用同一模式ON点，必须精确冻结共同配置/资格后才能合并计数。Stage C/D正式预算由Main另列、用户审查，本文无任何新增启动授权。

## 工程与旧资产边界

可复用科学底：Core78f4b59…/FW9dd1ee57…/ELF78d4e96…，完整Source5见JSON。主机写入V3的800纯协议+10生产CPU不等于native应用资格；MSHR64、native/merge-aware T候选各保留独立工程身份，均不自动集成。新源码不得链接旧.a冒称生产正确性。大Trace和永久raw继续真164，本文只有小型派生文档和参考代码。
