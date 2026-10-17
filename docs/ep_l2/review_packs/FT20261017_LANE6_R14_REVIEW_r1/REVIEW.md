# r14 ISCAS reviewer audit: mechanism, evidence and manuscript

判定：核心命题已清楚——在固定resident Tag、payload和bank预算下，通过dirty resident→WB ownership转移消除copy，并检验容量与copy两种因素。**当前可证的是源级协议与预算，不是性能、生产正确性或物理PPA。** 0 CURRENT_ACCEPTED，不能形成实测投稿结论。EN-v3的主要问题是资格时态、资源生命周期与某些图位承诺超出现有可执行接口；本次作定点逻辑修订形成EN-v4，不重写全文或新增科学实验。

精确审查对象：Lane6 d99195b5800de404b0f31c9c43742612428a168d 的EN-v3与成本账；官方Core c948184504d82b80e23eb3f4ff6cdfd328ba9355，生产Framework3ab150b3e99ff3ed759b8cdc5154cfb5744042a7。r14 d962f847cbf7ba6d525bbb23964fee392bd8a69f与原COMMON_CONTRACT为科学裁决。SOURCE_ANCHORS给19组实际源码摘录/准确行；SOURCE_MANIFEST给完整blob摘要。候选分支存在不等于官方整合。

按优先级排序的审稿问题与补强：

| 优先级/ID | 段落、风险及源码证据 | 本轮修订/可证边界 | 可执行补强与依赖 |
|---|---|---|---|
| P0/R1 | §III-B“Directed tests exercise/cover”容易读成当前修复版已验证；最新Lane1 binary=null、21项NOT_RUN，Lane5无当前资格 | 改为qualification requires，明确尚未运行；摘要/结果保留pending | Lane1唯一官方producer21（A18）→Lane5独立replay/11gate→新full-identity pairs。此链未完成前不宣称已验证正确性或speedup |
| P1/R2 | §I把“All roles share”写成通用动态bypass集成；c948 preview_free可让resident/WB跨分区分配，但reserve_bypass仍固定1024+id，git grep无生产reserve/assign_bypass调用（A1–3） | 改为当前resident/WB借用，明确没有证明并发动态bypass服务。不是宣布源码bug，而是限制可证贡献 | 若要通用bypass共存主张，需明确真实生产入口/landing与退尽测试和独立资格；本轮不新增bypass实验/trace |
| P1/R3 | §II-A bank公平只有总量还不够；16是WB数据quota，不能另赠无限WB控制或把U控制也锁16 | 补共同128 WAD/control边界；保留4×292、1op/bank/physical-cycle、同latch、固定Tag1024；U landing保持tag bank class（A3/4/6/9） | 既定physical-clock offset0/4096、warm hit及host identity生产定向；每bank逐周期断言/事件资格。总grants≤cycles只是必要条件，不证明每周期上限 |
| P1/R4 | §II-B缺descriptor/Line-MSHR释放说明，容易把Tag、response、WB完成混为一体 | 补tracked read descriptor/pin保持至L2→ICNT接收/内部response消费；Line-MSHR最后requester退休；pending sectors独立；WAD在set_done后释放（A10–14） | 既定held-response/backpressure、sector/late-generation、终态drain；不把所有store都说成同一种read-descriptor路径 |
| P1/R5 | §II/IV将reservation failure和rollback当作完全没有工作；copy流水和WAD/landing token可跨bank retry保留（A6–8） | 区分precheck拒绝、持有reservation的bank retry、最终commit失败rollback；指出物理工作不能撤销 | Lane1/Lane5既定rollback与same-bank路径检查。统计必须包括回滚前真实copy/操作，不能只按最终WB数乘3/1 |
| P1/R6 | Fig2b原承诺独立source/destination/send物理计数；源码WB_READOUT兼含copy+send，RESIDENT_WRITE兼含copy目的写+实际写；C7d记logical op，FT staging_reads记成功send grant（A7/9/15–17） | Fig2b改用已发出的completed copy transfers、send-read grants和WB totals；logical classes分列；精确physical分类须另有审计映射 | 原五对可提供这些native指标；不得直接减两个不同口径counter得到“物理copy reads”。需要细分时由producer新增最小类型事件并独立验口径，不阻塞首个周期配对 |
| P1/R7 | Fig4强静态对照只有方案：1024/112/32不可由当前8/16 WBUF接口表达；直接WBUF32会变1184而不是1168，且被合法性检查拒绝（A1/2/5） | 正文明确实现/资格缺口；将它保留为容量贡献主张的强对照义务 | 代表点出现capacity证据后，由原机制owner实现准确角色预算/拒绝/端口/配置身份，经科学边界裁决与Lane5资格再运行；本Lane不改配置或启动。否则只能报告相对冻结B16的总体效应，不能声称胜过最佳静态划分 |
| P1/R8 | Fig3 causal归因可能混logical ops、physical grants、attempts、等待总和及有重叠kernel delta | 保留图位；详细单位/窗口与缺项规则见FIGURE_READINESS | 只读同一accepted pair的scope=application/window=application_cumulative；不要把overlap kernel_shared_delta再求和；WAD/data容量分离。缺细粒度时不填零、不作唯一因果论断 |
| P1/R9 | Fig4 WBUF8与Ideal不能套用当前主配对接收器：native intake硬检查1168×64（A19），理想诊断还需自己的同binary B16 | 新入口明确仅B16/U_WB16；没有伪装成所有图的通用已完成接收 | WBUF8需独立1160范围适配与资格；Ideal需官方R1.1/repair+ideal资格/同binary baseline及原18格。缺任何项维持pending；不恢复旧1.721× |
| P2/R10 | §II-C TVD/RO设计用现在时易被误读为已通过当前生产验证；独立候选分别ab413/5ae8，非c948官方binary；Ideal亦为8ff5源候选 | 段首明确独立未编译/未合格source candidates，主比较OFF；附maturity表 | Lane1未来R2整合、Lane5独立资格；RO保持whole-commandlist oracle和+lookup/流量代价。不能用只含U_WB的binary替代 |
| P2/R11 | PPA字段bit表示可能被误读成增量面积，或把软件sidecar/指针当硬件；下层data carrier在ta后仍需真实存储 | 原账未发现伪造物理值，保留原九字段/六场景；本次PPA_REVIEW明确共同/差分/物理未知与下层驻留 | 先定G/K/age/queue深度/端口/rollback实现，再同工艺宏、RTL综合与STA/活动功耗；若无则维持源级成本估计，不能称面积/能量优势 |
| P2/R12 | 负对照sad被称low-pressure可能被误读为当前已经观测；五开发负载无外推保证 | 改为预先指定negative-control且pressure待检验；旧sad全撤回，不能据旧值确认本轮低压 | 五对全接受后保留sad/slowdown并验压力；btree/dwt2d在policy固定后按原计划验证，scan独占，不能择优完成子集均值 |

标题/摘要保留：in-place writeback是准确的当前研究对象；abstract已明确无实测speedup/area/energy。相关工作已承认V-Way/存储统一/MiCache/DL-MSHR先例，本轮不增加“首次”新颖性宣称，也不重复外部全文审读。新的验证优先级不是新增矩阵授权。

本轮只执行文稿排版、准确源码阅读、一次成功V2 authority观察和元数据核验；没有生产编译/测试/模拟。旧原生authority fetch超时45s并正确拒绝输出；后以有界exact-commit transport读取同分支HEAD并通过原生bind_manifest/withdrawal/proof与最终freshness检查。未用缓存PASS降级。
