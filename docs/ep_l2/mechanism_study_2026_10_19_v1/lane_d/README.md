# D线交付与复现

Authority：d9263fa2431592b33e900d9b48c6f20029d8b544；分支hrl/ep-l2-ms20261019-d-analysis-v1。原174。控制HEAD不是runtime源码。

- OPPORTUNITY_TABLE.csv：10个旧H0当前接受B/U端点＋5个旧C7e候选上下文，YES/NO/UNKNOWN；NO是此观测scope实测0，缺失不填0。
- INPUT_SELECTION.json / INPUT_REGISTRATION_INDEX.json：四个预登记完整输入、五候选及理由；input_registrations为E接口需要的不可变小包装，不是另一套runner。E唯一登记/启动owner，D只交inbox。仅核原件路径/command hash/尺寸并复用已提交body hash，不大复制、不重复全量hash。
- STATISTICS_REQUEST_TO_A.md：一次性最小统计需求，已以efdcc170cd85cec7e7e5902d8926c2dbe39a50ee推送/回读并交共享request。
- RESULTS_AND_INTERPRETATION.md：W/V/R四层解释及历史边界；同名CSV只接本轮E接受新配对。历史H0/R19、四模式、microopt三个source组独立，表间重叠不重复计数。
- UNRESOLVED_QUESTIONS.csv：只阻塞受影响条件；SOURCE_MANIFEST.json与TERMINAL_FIELD_EVIDENCE.json保留小型来源/64slice证据，不改原raw。

仓库根目录运行python3 util/ep_l2/mechanism_study_lane_d/derive_initial.py可重建离线派生表，最多读每个定点raw尾部2MiB；先验证旧current acceptance身份。不要改已交E的input_registrations；新科学选择要显式revision。运行python3 util/ep_l2/mechanism_study_lane_d/sync_intake.py单次处理E当前接受pair。没有simulator/编译/下载/迁移/清理入口，没有轮询器。

工具测试：PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s util/ep_l2/mechanism_study_lane_d -p 'test_*.py' -v。8项检查跨binary拒绝、missing/0、负结果、非研究配置未知、幂等及资格撤回、旧campaign和短片段隔离；全部synthetic receipt，仅证明分析工具，不是应用仿真。

D接收约定：E ledger accepted_results引用原receipt path/SHA/identity；accepted_pairs给baseline_attempt_id/variant_attempt_id/mechanism/comparison_group/status，并明确nonresearch_config_equal或等价E比较证据。D只验证引用和比较基本一致性，不重复E生产资格。字段缺失时保留受影响pair为HOLD并适配已有正式来源；不以包装缺失暂停整轮。

EN-v17、旧接受指针/日志/冻结发布和其他项目均未修改。无新接受事件时保留checkpoint，不宣称Codex/后台runner仍在工作。

续行r2：派生表现在逐端点保留run-key、profile、diagnostic/subset/oracle原标签、vendor、E qualification/selection/invariant身份及完整compact mechanism_metrics。配对内嵌endpoint引用必须与当前E accepted_results指针一致，防止静默重绑定。缺失边界仍UNKNOWN，不从计数或profile名称推断。8项D工具测试＋1项冻结E7434cbf09的真实D消费者兼容测试PASS；都是临时synthetic receipts，原E62项既有测试不重复运行。A3f9c5bf仅接口发布、binary仍null，不能将活跃草稿统计当生产数据。
