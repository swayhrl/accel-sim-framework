# Lane O 现有数据支持范围与缺口报告

结论：现有已验收小汇总足以支持W/V/M/T的多项正负Observation，当前缺口集中在**地址及时间的联合分布**，不是再跑一轮完整性能矩阵。优先复用mandatory MS/B0/FT/RO/TVD统计和历史复用分析；本阶段新增仿真、构建和生产Core修改均为0。

## 固定快照与覆盖

全负载状态使用北京时间**2026-10-28 18:30:57**的小型投影，18:31:56复制固定。Main仍在推进，其后的结果不自动进入本报告。

| 人口 | 数量 | 含义 |
|---|---:|---|
| authoritative42 |42|35个冻结代表输入、7个身份未解程序，保留全部覆盖行 |
| 注册点 / consumed starts |227 /218|都不等于有效完成 |
| CLOSED_ACCEPTED |214|210个Source78、4个Source92；不同ELF分层 |
| CLOSED_UNACCEPTED / consumed-before-fork |2 /2|失败与未fork费用保留 |
| 未启动注册点 |9|不是已有数据 |
| accepted profile pairs |106|不是106个workload |
| REF S/F输入配对 |22|21个程序，含不同的Vector4M/6M |
| 主35已有接受结果 |25|不是25个完整F对照；辅助Vector4M另列 |
| 本轮W提取 |48端点|25 S、23 F，25程序，包含未配对端点 |
| 本轮M复用子集 |44端点|2816个slice记录、16个RO适用端点，较早固定子集 |
| 本轮V提取 |30端点|23 F、7 WV，25精确输入/24程序；13个正响应端点、17个零 |

完整42行及输入SHA见 [coverage.csv](agents/coverage.csv)，状态与身份审计见 [COVERAGE.md](agents/COVERAGE.md)。主35尚无accepted结果的10输入为bfs、cutcp、histo、hybridsort、lavamd、mri-q、myocyte、particlefilter_naive、sad、SYRK；不能因此重开补跑。7个身份未解为backprop、cfd、kmeans、nn、nw、pathfinder、streamcluster。CFD现有5-kernel诊断不解除完整timestep身份缺口；历史SAD/CFD诊断另表保留。

全部106配对关闭四个optional pressure/lifetime/event诊断，LIFE_WIRE=SUMMARY_STAGE。它不表示mandatory统计关闭：48个W参考端点MS observer均ON，已保留独立首次阻塞、重复观察、65桶first-wait、WB占用；Source78 RO与TVD总结也可用。只在S64/MS0等独立背景把MS指标列未观测。

## 实际模型与来源

本轮主要reference为64 slices、32 channels、32sets×8ways、128B line/4×32B sectors、D512/M128/address cap32、fixed DRAM latency100。每slice物理模型1168个line payload槽=1024 resident+128历史bypass区+16 WB，S固定角色、F可按约束借用。32×8实际Tag覆盖256line/slice，全芯片2MiB地址数据覆盖，与物理payload9.125MiB不能混称容量。

Source78：Core `78f4b59e865b136eede74df74c44c210f5b4ca04`；Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`；ELF `78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a`。Source92及main61/r4/r5/11c历史观察分别保留，不跨ELF构成性能pair。

阅读依据包括总体架构、project_spec蓝图/characterization/claim合同、Main接管和最新full-workload报告、timeline最终报告、历史Motivation/Streaming/M0b审查及当前Source78的FT/TVD/RO/Tag/WAD/observer实现。历史架构中的1152槽和64×16意图、旧merge4、D256等都不能代替实际运行配置。Source78源码根为 `/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/core/src/gpgpu-sim`，精确文件行号见各Agent附件。

## W 写回

[W完整审计与代码口径](agents/W.md)，[48端点计数与bundle身份](agents/W_reference_metrics.json)。

- 全部25个S端点copy read=copy write=WB created；Conv720,834次，scan5,310,331次，srad5,752,820次，stencil1,504,136次。它们的copy RAM-op占比约11–14%；10个S端点WB=0。
- scan WBUF均值10.661、峰16；WB_DATA_SPACE有1,737,618个独立首次受阻请求、49,938,625次检查。Conv同类49,161个独立请求。WAD128与WBUF16是不同资源，不能互相替代。
- Conv SAME_ADDRESS_WB有16,791个独立请求/3,736,508次检查；scan390/215,979；srad65,753/21,602,967。窄B0 native precheck可为0，而更广MS入口为正，不能拿前者否定后者。
- 已有WAD lifetime每slice均值/p95/max、MS等待分布、WB占用面积和Bank操作/冲突/等待。FT staging lifetime也已实现，但S与pooled起点不同，compact bundle不一定投影此字段。

缺口是所有有效victim分母、统一起点的WB阶段时间分布、同址R/W/A×WB年龄/状态、copy/WB专属Bank等待。先把已有FT终端字段纳入Main的单次解析投影，不重复扫描raw或重新开发已有first-wait。

## V 替换与复用

[V完整审计](agents/V.md)，[30端点实际服务与验收身份](agents/V_ACCEPTED_REFERENCE_COUNTERS.json)。

当前F真实V响应：stencil4,930,616，3MM1,147,507，GEMM586,844，Conv44,974，scan5,584。当前FWT WV有88,069响应/3,312次dirty-forward；scan F有296次dirty-forward。Vector4M/6M、2DCONV/3DCONV、sgemm存在安装但响应0。响应只在实际Bank服务及enqueue成功后增加；directory_queries、installs均不能作可靠读命中率分母，也不能把响应一比一变成避免的DRAM请求。

**历史reuse数据不是空白。** Motivation审查状态DATA/SEMANTICS PASS、packaging待闭合，10程序已有line stack-distance与post-eviction再访。Streaming prefinal有sector temporal分布和空间/时间区分，但仍有final promotion、provenance、multi-sector tie证明等边界。原小CSV/精确输入manifest本轮未定位核验，因此报告保留审查约数与原状态，不能当当前Source78全负载的新测量。详见V附件“历史复用统计”。

当前缺口是精确输入下同址gap、post-eviction next-touch分布、对象年龄、clean/WB_STAGED/WB_INFLIGHT/WB_COMPLETE服务细分、保留窗口适配。先追回历史小CSV/manifest/final-delta，再决定哪些输入确需新采集。line重复必须拆出32B sector空间触达与真正时间重访。

## M 只读与并发

[M完整审计、16个RO端点与bundle来源](agents/M.md)。

- Vector4M：1,000,000个RO requester=250,087事务+749,913 merges；Vector6M：1,500,000=375,109+1,124,891。SGEMM当前F有81,582事务/1,054,333 merges，不能沿用旧r4“事务0”的概括。
- Conv S line-MSHR峰128，6,499次检查/696个distinct first-block；F2,986/337。SGEMM S per-line cap1,738次/55个distinct。既有44端点D512 full为0，其它负例保留。
- 已有RO issued-not-ready独立line峰、普通MSHR占用、descriptor/合并限制、mandatory first-wait；不能把ordinary MSHR和RO transaction峰直接相加。

RO候选/accepted global reads是已有可靠比例，未必是all-L2 demand比例；静态认证line数、动态候选请求、实际RO事务是不同人口。live merge可发生在ready/draining，不能称严格fill前重访率。BlackScholes/Transpose等有正认证候选但事务0，不能称无RO数据。

缺口是first-arrival全部请求类型/资格分母、同址RO间隔、strict before-fill与ready-only重入、normal+RO未完成地址并集分布。利用现有line/RO索引和有界refcount补统计即可，不需要逐请求日志。

## T Tag占用与释放

[T完整审计、timeline和detach验收来源](agents/T.md)。

已验收timeline覆盖8程序/9端点，同Source78/32×8/latency100。Conv首次NEW-at-R8为289，重复preview失败42,717；CFD诊断分别1和11；actual-access TagFAIL0，因为这些请求先被Frontend拒绝。Vector32×8有RO但NEW-at-R8=0，detach0；S模式RO/T不适用，不能补0成为T负例。

较晚Vector4M 32×4已验收F端点detach27，archive与两次native恢复已核对；32×8和16×8为0。它不含完整optional Tag lifetime，因此该点缺失的TagFAIL/寿命仍UNKNOWN，不为补细节立即重跑。

**同一冻结接受快照还包含两组Conv缩容F正例**：16×8实际detach **237**，匹配S/F为**360,380/367,152** cycles；32×4实际detach **1,141**，匹配S/F为**395,820/425,074** cycles。二者均为Source78，不能只以Vector27概括“当前实际detach”。这些数据证明T确实发生、数量随配置变化；但F均慢于匹配S且没有同背景F−T/F，不能据此断定T自身有害或有益。该组缩容点的可选Tag寿命/满路联合数据缺失仍是UNKNOWN。

已有每set Reserved时间面积/episode寿命、首NEW占用分布、preview→actual→detach漏斗及有限快照。但LIFE的NEW_UNIQUE是首次NEW暴露，非后来曾遇满路的全部请求；WAIT是首NEW→commit总准入延迟，非Tag-only。cached eligible还包含T开关，T-OFF为0不能表示结构上无机会。

最小缺口是ever-full独立请求、真实Tag拒绝等待、同NEW∧满路∧structural可释放RO联合。现有NEW_WITH_PENDING和NEW_WITH_ELIGIBLE是边际，不能相乘。无需新Tag probe或全Set周期扫描。

## S基线特征与F机制结果的分层（V1R1补充）

以**S完整参考模型**观察脏写回、独立请求重访、普通MSHR及Tag需求；必要时新增被动历史/ghost统计，但不能把S没有RO事务或Victim服务记为语义零。以**F/WV模式**观察真正进入RO事务的requester、Victim成功服务、RO/Tag资源联合以及detach。S/F差异是全方案对照，不自动等于W/V/M/T中某个机制的独立贡献。

因此四组论文观察首先陈述请求与资源现象；只有在Source/ELF、输入、几何、观察器及其它资源完全匹配的对照中，才讨论机制性能收益。不同模式/历史谱系不直接混合人口。详见METRICS与COLLECTION_PLAN。

## 统计解释与可靠性约定

每原因MS等待是首次blocked→首次已知clear；若仍阻塞到准入，才在准入关闭。仅ANY_FIRST_BLOCK_TO_ADMISSION必然截至admission。unknown检查、head change、unfinished/censor必须保留；不是累计每次间歇阻塞或独占GPU停顿。

输入按完整ordered commandlist内容、memcpy、kernel及精确SHA对齐。接受点/validation旧字段可能仍为PENDING，需和冻结CLOSED_ACCEPTED及独立archive receipt外连接；不改写原状态。原始capture完整性与GPU数值输出仍UNKNOWN，观察限于trace-defined完整声明命令序列与模型协议。

本轮只读取源码、文档、现有小汇总及validation bundle，没有读取Trace正文或重新解压大raw。早期定位时的父目录AGENTS文件名搜索已取消；后续按已知路径定向读取，无持续扫描任务。所有写入仅在Lane O独立目录；没有修改Main、生产Core、冻结规格或正式账本。

后续见 [最小采集计划](COLLECTION_PLAN.md) 和 [Observation草案](OBSERVATIONS.md)。目前应审查指标与缺口优先级，不启动新的完整GPU仿真。
