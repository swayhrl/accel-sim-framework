# 机会表：观察、竞争解释、受控对照、范围

观察时点的current authority为Lane5 generation47，publication `a86aa6589316680d7ce051c7a85232b90c6ba24e`；精确snapshot SHA、raw/review及输入绑定见`derived/AUTHORITY.json`与`SOURCE_INPUT_MANIFEST.json`。退出前另做currentness复查。表中“未证实”不表示次数为0。

| 机会/约束 | 已实测 | 源码可构造 | 尚未证实/所需受控对照 |
|---|---|---|---|
| MQ2：WB队头bank受拒、第二项安全独立读被挡 | 代表输入有bank contention、MissQ/lower压力；aggregate `bank_block`不区分head-WB/copy/frontend。无完整MQ2联合见证 | `baseline_cache::cycle`只取front；`lower_ready`仅L2_WRBK增加本地bank read。可构造不同line普通读位于第二项的顺序，但需真实请求ordering证明 | Lane1真实队列小case与OFF/MQ2；测safe_second与真实bypass；head恢复优先、不重复lower enqueue；应用触发/收益null |
| RG1：held消费者非bank不ready，另有ready、全cycle bank空转 | 银行logical_ops=grants的终态闭合、已有retry/wait计数已测；不记录held消费者ready、空转原因或替代client | arbiter保留未消费m_granted；response受ICNT gate、WB受memport gate而可能不再调用；另一个请求可被旧selection挡住 | 合法生产队列empty-service见证尚未收到；不能把裸store artificial enqueue当真实复现。Lane1先复现再实施；保留oldREADY公平、同cycle状态变化与P1 |
| frontend pending HOL | 上一revision frozen7b8小case已实际证明：pending dirty replacement挡住不同bank独立hit，后续可完成，B/U各一次；未重跑 | `ft_access`对`m_ft_pending.request!=mf`拒绝，保护victim/预留资源/回滚 | 没有代表应用pending-other-request计数，关键路径贡献未知；不是MQ2 MissQ case，也不能靠删锁推出合格优化 |
| pin-aware victim / pool landing | 原H0五输入10行pin_block=pool_full=0；本次46有限行也均0 | source有pin/pending-sector guard、same-bank free slot申请 | 本批counter未激活，不证明所有frontend阻塞都被覆盖；本轮不优先开发、不随意跨bank landing |
| WAD容量full | H0 Conv B/S64/U_CAP16/U分别0/1892/0/2706；Q4 Conv B/U55645/54516，WAD256_Q4降为0/0 | dirty replacement需WAD entry；容量独立于本地WB payload释放 | 属实测metadata压力；不能等同同地址排序、MQ2被挡读或RG1消费者不ready。WAD256_Q4同背景控制保留，不能提前清WAD |
| same-address WAD hazard | H0 FWT B/S64/U_CAP16/U分别276421/302684/279383/309144；CFD B/U9841/13400；H0 Conv均0 | 同line旧WB直到真实set_done保护排序 | 合法顺序等待，不是可免费绕过机会；不与WAD-full计数相加当独占stall，待比较是否被新服务调度间接改变 |
| 下游与frontend预检 | Conv/FWT H0有MissQ-full、frontend伴随lower-full及真实DRAM scheduler-full attempts；明细见raw表 | response先ICNT gate、lower-WB先memport gate，影响实际bank retry消费者 | 旧`c7d_l2_to_dram_full_block`不是精确head-drain被挡次数。M0/L2CHAR专用记录未输出，不能补0。实际ready/空转联合事件仍缺 |
| 强静态与Unified容量边际 | 同combined source四模式已接受：S64相对B16两个样本都稍慢；U_CAP16→U Conv快1019cycles、FWT仅34cycles | local cap限制与统一组织不同于静态copy/分区 | U_CAP16有大量refusal不等于大性能边际；B16→U_CAP16不隔离纯copy；新MQ2/RG1须三架构共同ON并同binary OFF |

MQ2源码位置（Core9bd）：`gpu-cache.cc:1576–1595`、`ep-l2-ft-cache.inc:393–405`。RG1：`gpu-cache.h:2437–2534`、`l2cache.cc:1173–1212`及lower drain/frontend phase。frontend pending：`ep-l2-ft-cache.inc:175–368`；WAD/lower计数：`l2cache.cc:1394–1448`。这些是审查引用，精确excerpt见SOURCE_AUDIT；不是新执行结果。

原frontend小case证据：publication `f3d89e77de0fbac16a05df42bd84f02f54dbc890`，pack `FT20261017_LANE3_MECHANISM_ANALYSIS_AND_MINVAL_r1`，`ACTUAL_NEW_CHECKS.json`及frontend日志；Core7b8生产cache路径、显式真实bank contender、未使用非法私有状态。其scope只到局部控制因果，不升级为MQ2/RG1/新combined release资格。

竞争解释：bank落点、静态copy的两次RAM服务、WAD排序、MissQ/ICNT/DRAM背压可能同时变化。重试减少、bank占用改变与GPU完成时间的关系需要受控端点，不能由累计计数反推。旧正负性能、未触发、missing和资格失败分别保留，不取最佳点。

受控对照：使用同候选正式binary的Conv/FWT × B16/S64/Unified × OFF/MQ2/RG1；先合法生产小case和独立资格，后Lane5在原安全窗口/预算执行。若两侧等幅加快且S_EP不扩大，记作通用服务优化和更强基线；若出现相对交互，也只对准确配置/输入成立。没有新增结果时不填ratio，不长期等待。
