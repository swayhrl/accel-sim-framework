# 提前CH-F256全35匹配：合同与接口审查

## 结论

**现有自动CH_MATCH路径现在不可提前执行。** 原Goal已明确授权必要CH匹配和additive新矩阵；代码中的full35门只约束推荐/推断proposal，并不是registry全入口禁止一切早期CH观测。因此也不应把它夸大为用户的普遍禁令。

但当前已发布阶段没有独立“prospective CH measurement”类型：不能只改phase名、绕recommend直接调用底层journal，就声称已满足当前CH_MATCH合同。若Main决定增加一项明确、单独版本化的前瞻全35测量声明，可保留原E等待、full35推断/挑选/adoption规则不动再做独立资格；该声明必须在登记+35之前冻结同输入/同向量，公开已看见的partial数据，不晋升F256或比较partial-population winner。本轮仅生成条件模板和声明草稿，**不登记、派发、改规则**。如果不另设这一测量阶段，继续等待下述现有门。

## 精确依据

- SCIENCE_AUTHORIZATION.json:5–7：factor-family grants从current registry解析，每个exact admitted spec一次启动；未来矩阵需additive coordinator registration。
- SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json:2–15、54–60：四族扩展授权、350=344fresh+6ref、固定850MHz/10MiB/DTC/35输入；第60行原用户指令明确含“必要CH匹配均已授权”；第58行只加credits，不reset/refund。
- agents/E/ADAPTIVE_SEARCH_CONTRACT.md:1–8说明这是Agent-E proposal规则；31–34写明首轮proposal等所有初轮profile终止；40–41限定formal candidate需全部35 accepted DH后再exact-profile CH；80–98定义uniform moderate/high classes，不能把partial F256当已选class。
- tools/l2_adaptive.py:155–164在初轮未terminal时返回WAIT_INITIAL_TERMINAL且proposals=[]；222–248只从full(P0)和full(profile)候选中选classes并生成CH_MATCH。
- typed_negative_full35_v2/terminal_gate.py:50–60确实过滤proposal，CH_MATCH在56–57行要求full(P0)和full(profile)；其作用域是推荐/推断，不是所有下层registry调用。安装ACK证明已于UTC18:36生效且保同一journal object。
- tools/l2_ops.py:96–97是现有recommend→registry.extend接线；直接另调extend会跳过上述proposal检查。
- tools/l2_registry.py:35–57支持CH从same-input CH-P0克隆并只改L2/FRFCFS，预算/remaining按新增数递增；它没有父人口或候选有效性门，不能拿“技术能写”作为科学准许。
- registry_journal_v1/l2_registry_journal.py:63–105准备精确新spec与旧authority快照，108–162对账且保spent，193–199只做未闭journal finalization；它不替代full35 scientific inference门。实际ACK为REGISTERED_SOLE_OWNER_REGISTRY_JOURNAL_AND_FINAL_GUARD。
- 未找到独立同名SEARCH_RULES文件；实际规则是上述冻结E合同/CONTRACT与已安装typed full35层，不能杜撰一个缺失的例外文件。

## 当前与模板

读取时原request budget=344、remaining=46、consumed=298；matrix仍350/revision0，history没有新proposal，CH-F256 admitted=0。V4 UTC2026-10-27T21:59:28.917840+00:00中DH-P0 accepted=28/35、DH-F256 accepted=30/35（有效配对27），均未满足full35。

CH_F256_FROZEN35_CONDITIONAL_TEMPLATE.json已纯配置生成35个同输入CH点：entries192/merge4/miss_queue32/FRFCFS256，全部固定850MHz、10MiB、原CH DTC/hash/build/input；shared credits为447/controller、private仍2，非等面积结论。无按收益挑输入；重复身份必须核exact配置/输入/build再dedup。模板未写生产configs/specs。

按现有自动路线释放模板，需初轮全terminal、DH-P0与DH-F256都full35 accepted，且F256由未改class规则实际选中再生成CH_MATCH；不是只要F256 full就自动成为high-resource/winner。已核typed scanM16 negative可作terminal但不提供性能、不改GM，也不恢复旧spent。

若Main另立prospective测量阶段：先发布PROSPECTIVE_DECLARATION_DRAFT的正式版本，冻结全35/vector/已有数据/目的/排除规则，然后同一个owner与现有journal精确新增35（若届时仍全未注册）。当前示例budget344→379，remaining46→81，原consumed/UUID与所有receipt保留；6refs不增启动，原350 membership不变。current矩阵虽可增至385，原350统计要按冻结SCOPE另分层，新35为独立matching层，未来R2另层，不把其结果混入旧DH单因素GM。不要新增owner或重启模型。

该prospective声明是测量时序/范围的显式增补，不是宣称现有CH_MATCH门已通过；本审查不自行批准或实施它，也不修改原科学推断规则。
