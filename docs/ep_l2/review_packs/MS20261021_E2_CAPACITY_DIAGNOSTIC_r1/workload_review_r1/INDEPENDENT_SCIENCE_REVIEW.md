# E2 workload调查独立科学审查

结论：**未发现最新READINESS将任何新候选错误标为已资格/可启动，未发现需要停止当前Conv ON的科学身份问题。** 现有报告正确保留原五MAIN分母、原七输入缺失、INCOMPLETE/HOLD、负结果以及新capacity诊断独立分母。以下为按影响排序、在下一次候选决策前应修正的P2问题；不是新的运行许可。

范围：只读E的`workload_research_r1/`与`workload_readiness_consolidation_r1/`，以及READINESS精确refs中的A2/D/F八个Git小metadata blob。逐blob先查大小（每个≤128KiB、八个合计125,833B），并核对已有SHA；未读取trace正文、重算大SHA、执行代码/native/应用或修改peer/中央状态。本文不重复源代码/native正确性审查。

## 1. P2：旧调查入口仍把已有SGEMM探索登记说成缺失，机器字段还混入原矩阵身份

证据：

- `workload_research_r1/README.md:12`写“仍缺……正式探索登记”。
- 同目录`DECISION_REPORT.json`的`priority[candidate="SGEMM medium"].run_status`为`NOT_QUALIFIED_OR_REGISTERED_FOR_FORMAL_START`。
- `LOCAL_COVERAGE_INVENTORY.json`的`next_qualification_candidates_max4[candidate="SGEMM medium input qualification review only"].blocking`要求“independent exploration registration”，`coverage`甚至写“eighth original-matrix family”。
- 但`workload_readiness_consolidation_r1/README.md:14`及`READINESS.json:208`已正确确认`E2_EXP_SGEMM_MEDIUM_20261020_r1 / REGISTERED_EXPLORATORY_HOLD_NOT_LAUNCHABLE`。
- F正式包`b81a259a7d3030208dcebbc7693c3ef793c2fde9:docs/ep_l2/review_packs/MS20261021_F_INPUT_PREPARATION_r1/README.md`明确原登记已存在、不得静默替换Btree；其`MISSING.json`的SGEMM-EXECUTION条也不是缺登记。

影响：跨lane或机器消费者若从旧入口开始，会重复要求登记，或误把独立探索集合纳入原七输入矩阵。最新consolidation已纠正，因此不是新的运行门漏洞。

最小修订：保留历史调查原件和采样时间；新增独立勘误/当前决策入口及superseded/current-readiness指针，不覆写r1原文，并在当前机器决策导出中分别列`registration=REGISTERED_EXPLORATORY_HOLD_NOT_LAUNCHABLE`与`qualification=NOT_GRANTED`。删除“original-matrix eighth family”的当前解释，新增探索统计永不改原七分母。

## 2. P2：8–10目标尚无逐机制闭合路径，现有具体清单只能增加到8–9

证据：

- `workload_research_r1/README.md:7`提出8–10，但具体步骤为FWT、SGEMM加1–2项，即当前5+2+1–2=8–9；`DECISION_REPORT.json.suggested_coverage_goal.approach`相同。要达到10仍缺第五个新增distinct family，不能从备用尺寸或多个kernel补足。
- `MECHANISM_COVERAGE_REVIEW.md:5,22,51`将五个F的detach全0明确列为最优先缺口。
- 最新`READINESS.json:189`却准确指出FWT是RO零覆盖、不是T/M-positive目标；SGEMM的RO/真实post-eviction reuse仍UNKNOWN且D将其保留为低tracking压力控制。BFS压力/完整数据也UNKNOWN；已找到Hotspot512/2/2只有1次launch，不提供预期跨kernel ping-pong。
- D正式预冻结`6825d1cd0c87d8b0122e03a9dff5253c873b747b:docs/ep_l2/review_packs/MS20261021_D_WORKLOAD_PREFREEZE_r1/DECISION_REPORT.md`明确FWT/SGEMM优先、BFS条件项、Hotspot备用，并不声称这些输入已证明填补detach性能缺口。

影响：数量目标可能被误读成“再做若干应用就能支撑完整机制泛化”。FWT恢复和SGEMM负控制有独立科学价值，但不能据此承诺T/M正触发或更多有用V读取；即使达到8–9，关键机制仍可能未触发。

最小修订：把当前具体路线写成“先增加2个可闭合候选，条件允许再增加1–2；预期覆盖7–9个，8–10仅远期非承诺目标”。增加一行`Tag detach-positive证据候选=NONE_ESTABLISHED`，把每个候选映射为“恢复/负控制/条件正触发假设”。只按预先冻结的完整来源、中性S/地址/并发画像和成本选择，保留未来detach仍0的结果；不能观察F后不断换候选直至有正收益。

## 3. P2：必须先选择科学runtime与继承范围，不能把93a9完整F缺口强制成所有续行的前提

`READINESS.json`的FWT/SGEMM行重点列新runtime finite-F缺口；`README.md:7–12`也集中描述新source资格。A2正式REPORT的两版矩阵却明确旧main61有准确FWT S/F资格、可在全部身份适用时复用，新93a9完整F不存在资格。汇总下一步应显式并列两条路线，而非默认所有后续应用都换93a9：

- 原FWT恢复若目标是补原main61七输入分母，应先审现有main61 exact Q及原输入身份、当前监护/资源门与单独恢复授权；不因93a9未有F资格而要求先补整套新runtime验证。
- 若另选93a9做新探索，需要其准确finite-F资格与同binary新S锚点；新93a9 FWT对不能直接补旧main61原分母。SGEMM也必须明确所属producer/cohort，禁止跨binary混锚。

同样，F的`MISSING.json`把source_recapture、capture_provenance、numeric_reproduction分别列出。缺原GPU UUID、原scaled源码或数值payload可以限制“复采/数值算法正确”主张，但**不能仅凭这些未知反向撤销已经登记的旧main61 frozen-trace资格**。既有授权trace-model范围与新增数值复现范围须分别决定；新增要求只有在原合同确实要求或科学解释拟变更时才进入对应门。当前READINESS未明确撤销旧Q，但这条区分不够醒目，容易造成无必要的全source迁移或阻塞。

最小修订：新增runtime/cohort决策表及`scope=EXISTING_FROZEN_TRACE_MODEL`/`scope=SOURCE_RECAPTURE_OR_NUMERIC_VALIDATION`列，保持旧r1缺失事实不改，明确哪些是原Q适用复核、哪些只是扩展主张的缺口。先做FWT旧Q恢复适用性和SGEMM独立负对照准备，BFS保留条件项，单kernel Hotspot不优先。实际新启动仍需相应用户批准。

## 4. P2：静态兼容审查被摘要强化为“已经证明无需构建或机制”

证据：

- `workload_readiness_consolidation_r1/README.md:12`写“A2已经证明两种保存输入无需新增opcode、主binary构建或机制”。
- 实际A2正式材料`663fba57b7dc6428d613db443d6ff2f3c99e33d5:docs/ep_l2/review_packs/MS20261021_A2_DF_CANDIDATE_COMPATIBILITY_r1/REPORT.md`的结论是本次静态映射未发现必须修改producer的兼容缺陷；当前93a9完整F资格不存在。其`SUPPORT_GAPS.json`状态为`READONLY_REVIEW_COMPLETE_NOT_QUALIFICATION`。
- E的`READINESS.json.source_qualification_boundary`已经用较准确的“opcode mappings source reachable … not native full F PASS”界定。

影响：即使37/21种opcode均有入口，也不能逻辑上保证后续准确finite-F定向验证/完整输入终验绝不会暴露需producer修复的问题。好在摘要紧接着仍要求E独立资格，当前没有借此放行。

最小修订：改成“A2静态格式/opcode/source映射未发现必须新增机制、opcode或重建的已知缺陷；先复用现有producer和同身份证据，只补真实资格缺口；后续若发现真实正确性缺陷再按producer流程处理。”不为调研自动构建，也不预先承诺永远无需构建。

## 5. P3：物理文件齐全、历史完整grammar证明和当前内容相等应在简表中显式区分

证据：`LOCAL_COVERAGE_INVENTORY.md`表头“本地完整文件=True”来自stat/存在性；其JSON逐文件`content_rehashed:false`。F的正式manifest则准确写`current_content_claim = Saved complete SHA/statistics plus current stat sizes. No fresh full-body content equality assertion.` 最新READINESS也只允许精确decoder绑定后复用属性。

这不是要求再扫大trace：本轮复用历史完整证明是正确的。建议简表改为“所有声明文件存在/大小匹配（本轮未重hash）”，同时列出保存证明的准确trace composite及来源SHA；当前内容验证留给真正受批启动的原身份门。这样不会把“有19个文件”读成来源/数值/oracle/新runtime资格已经完整。

## 本轮确认正确、应保留的边界

- 五distinct仅支撑这五精确输入的受控案例与混合正负结果；没有发现把8–10说成ISCAS统一硬门槛的文本。
- 原五MAIN与同五输入新capacity配对不是十个独立应用；kernel、控制profile和不同尺寸不能填distinct计数；旧失败不因新增成功被替换。
- frozen-trace replay、原源码再采集、数值输出正确性是不同证据范围，当前报告没有豁免capture/数值缺口。
- 新93a9 S/OFF/large-capacity ON资格不能继承给finite full F；新应用还需逐输入、配置、RO/fallback和真实完整终验。
- Hotspot本地1kernel已被正确降为备用；histo/atomic、旧SpMV/Scan/Btree及H200新格式没有自动升级。
- 已有bytes/grammar/opcode/非原子属性应精确重绑复用，不要求重复全trace扫描或全部旧native；未来成本仍UNKNOWN，旧离线扫描耗时和INCOMPLETE elapsed未冒充正式walltime。

上述修订针对报告可发现性、计数与表述；无需因此停止或重启现有Conv ON，也无需重做已完成科学审查。
