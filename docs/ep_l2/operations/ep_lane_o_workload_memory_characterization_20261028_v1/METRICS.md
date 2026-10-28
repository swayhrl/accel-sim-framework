# Lane O W V M T 访存特征指标表

状态：指标合同与现有覆盖审计，未新增仿真。详细数据与代码定位见 [W](agents/W.md)、[V](agents/V.md)、[M](agents/M.md)、[T](agents/T.md) 和 [覆盖表](agents/coverage.csv)。

`已有` 表示至少一个明确人口的已验收产物可回答，并非全42覆盖。参考模型 Source78 的当前几何为64 slices、32 sets×8 ways、128B line/4 sectors、D512/M128、固定DRAM latency100；其它几何及 Source92 分层。老架构意图中的64×16、1152 payload 不能代替实际1168槽与本轮配置。

## S与F的观察分层（V1R1补充）

| 观察背景 | 主要回答的问题 | 不应直接得出的结论 |
|---|---|---|
| **静态参考S** | 请求类型、同址访问/复用距离、真实脏替换及写回等待、普通MSHR/Tag压力；如需V潜在机会，可做不改变行为的淘汰后再访观察 | S无RO事务不代表程序没有只读请求；S无V读响应不是“无淘汰后复用” |
| **完整F或合法W/V** | 实际Victim读取与对象年龄、RO候选/准入/合并、可Detach RO和目标Set新请求的联合、实际机制状态与服务 | F的实际读服务、Detach和资源占用不是独立于机制的程序固有特征，也不能直接证明净加速 |
| **同源同背景对照** | 单独评估W、V、M、T的性能增量及新观察器不干扰性 | 不以S的Tag压力与另一F配置的RO数量拼成同时机会；T需同背景F−T/F |

第一批统一基线特征以**S参考模型**为主；F指标优先从已接受的F数据提取，确实缺联合机会时再由Main安排必要的F补充。历史证据必须核对输入身份与几何后单列。新增采集不要求每个输入都无条件补跑S和F；以缺口为依据。RO静态证书是模型范围下的资格信息，不等同于S实际产生RO事务。

| 类别与指标 | 定义及分母 | 记录与推荐统计 | 现有覆盖与可靠边界 | 最小补采成本 |
|---|---|---|---|---|
| W dirty replacement / WB | 实际 dirty-victim 提交与 WB 创建；有 demand 分母时另报每千 demand | create、lower_accept、true set_done；完成闭合 | 已有 FT/WAD，Source78参考 S/F 48端点可提取；不能把程序 store 等同 dirty eviction | 0，先解析 |
| W 写回持续时间 | victim选择→copy→lower_accept→set_done分段；每个WB一次 | count/sum/max、log2时间分布、未完成删失 | WAD lifetime 已有均值/分位摘要；FT staging_lifetime 在 S 与 pooled 模式起点不同，不能直接当同一个WB延迟 | 现有对象附时间戳；不保存事件流 |
| W WBUF/WAD占用 | 分开统计物理WB staging和地址目录；时间加权occupancy/full ticks | area、observed ticks、hist、peak、unique blocked | 已有WAD高水位、全满/同址检查、B0部分first-wait；attempts不等于独立请求或GPU停顿；WBUF与WAD不可互换 | 增量状态面积及现有live first-wait复用 |
| W 写回中同址再访问 | WB生存区间首次见独立R/W/A；按对应WB和demand分别归一 | WB阶段×请求类型；unique、repeat attempts、等待 | MS已有SAME_ADDRESS_WB独立first-block/等待分布；WAD窄域hazard与TVD dirty-forward另有人口；缺R/W/A和WB年龄关联 | 复用现有UID/WB索引，仅加分类和小直方图 |
| W copy与Bank等待 | copy read/write、WB readout按真实逻辑op；wait按同一op首次创建至grant | op/attempt/grant/conflict/wait；分类型 | 既有copy/Bank计数可用；不同路径WB readout人口和实际字节不同，不以grant×128B估带宽 | 先解析；缺失分类型延迟才加时间戳 |
| V 同址访问间隔 | 相邻独立requester的cycle差与访问序号差，分别定义 | R/R、R/W等类型；log2间隔、样本/删失 | 现有V命中/RO merge不提供完整间隔分布 | 固定有界历史表，可采样 |
| V 复用距离 | 两次访问间不同128B line数；32B sector时间复用单列，不等于中间请求数 | 短距离bounded-LRU histogram；超界另列 | 历史Motivation已有10程序line stack统计（DATA/SEMANTICS PASS、packaging待收尾）；Streaming sector结果为prefinal；当前输入映射未核验 | 先恢复小CSV/manifest，参考旧profiler；确需时在线短栈；全局精确距离不列入最小计划 |
| V 淘汰后再访 | eviction→下次requester；按clean/dirty/WB阶段 | 首次再访CDF、读写、结束/回收/表溢出删失 | 历史Motivation已有再访比例/平均gap；当前已有TVD服务/retention，未覆盖当前全输入的再访时间分布 | 先复用历史证据；必要时≤128或采样历史项/slice，复用hook |
| V 保留潜力与实际服务 | shadow机会须同时满足目录、payload、retention；实际response_commit另列 | installs、read checks、response_commit、dirty-forward；实际与shadow不同表 | 已有30个F/WV参考端点的实际V记录；10/23 F端点有读响应，负例保留；不是命中率 | 0解析；缺失retention曲线才做单一有界shadow |
| M RO比例 | certified独立read requester/all demand；另报RO miss/all miss；证书静态覆盖另列 | checked/eligible/admitted、排除原因与分母 | runtime RO事务/merge计数与资格已有；load≠RO；模式禁用RO不能证明静态RO=0 | 复用已有证书/判定；补统一first-seen分母 |
| M 同址RO间隔与完成前重入 | 同line独立requester到达；分别以fill和最后waiter retire为终点 | gaps、每transaction后续arrival数0/1/2–3…；满足者/所有事务 | 已有merge、reuse_seen与部分历史LIFE；merge可发生在ready/draining，不等于fill前重入 | 现有RO对象附时间戳和小hist |
| M 未完成独立地址数 | 普通MSHR与RO事务地址并集；同址多sector/重复RO只计一地址 | 时间加权hist、max；transaction数另列 | 既有line_mshr occupancy只覆盖普通MSHR；RO transaction peak不是地址并集 | 增量地址refcount或有界sidecar，不全表周期扫描 |
| M MSHR/合并限制 | need、full、per-line cap、descriptor等分别按attempt和独立first-block请求 | mandatory B0已有distinct、first-wait sum/max/hist、resolved/unresolved | 每原因first-block→首次known-clear；仅ANY项→admission，均非独占累计阻塞；分母要匹配入口 | 多数0解析成本；不重复造B0统计 |
| T 每Set Reserved占用 | RESERVED不能混同VALID/MODIFIED或总valid ways；Tag状态变化时间面积 | 每set occupancy hist、time peak、event peak；NEW-at-R分开 | 旧r5/当前timeline已有分布；新全负载optional关闭，很多格未观测 | 在已有状态变化处增量结算，不加probe |
| T 因满路等待 | 首次或之后遇all-reserved的独立NEW；Tag-only first/累计wait与重试分别报 | ever-full unique、attempts、原因wait、censor | 已有Conv/CFD首次NEW∧full与预检attempt；LIFE WAIT是首NEW→commit总准入延迟，非Tag-only | live UID/原因标志，新增少量hist |
| T RO占Tag期间的竞争 | 同一NEW/目标Set/时刻 `R=ways ∧ structural RO eligible`；与policy允许分开 | joint count、eligible ways、blocked unique、relieve/detach→commit | 现有边际NEW_WITH_PENDING/ELIGIBLE不能相乘；T-OFF会令policy eligible=0；Vector32×4实际detach27已验收 | 读取既有preview/RO状态的联合counter；不扫描额外Tag |

统一输出必须带输入内容身份、Source/ELF、模式/feature、几何/资源、observer开关、统计人口/clock、count/sum及缺失状态。Per-slice p95不能平均成全芯片p95；各slice峰值不代表同时峰。周期时间是参考模型条件下的行为；只有精确输入地址覆盖与声明序列的请求类型/重复性可作为更接近程序的证据。

### 缩容T正例的观察范围（V1R1补充）

与Vector4M 32×4的27次实际detach并列，当前Source78的Conv F在16×8已观察到237次detach，在32×4观察到1,141次；同几何S/F分别为360,380/367,152和395,820/425,074 cycles。它们说明实际释放存在且配置敏感，**不证明T的独立性能收益，也不能从更高detach次数推导更快的F**。现有可选Tag lifetime统计在这些缩容点未完整启用，缺失联合人口仍为未观测。
