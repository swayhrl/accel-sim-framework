# r5 metadata：整批生成预算与实际并发空间分离

审查结论：批准原文的640MiB是整批collector/metadata生成预测，另明确`active_monitor_margin_bytes=2GiB`和按真实门单路滚动；没有把尚未启动三端metadata永久作为物理并发预约的条款。此前将全部remaining640同时扣df是实现附加的保守条件，不应冒充用户合同。本候选修正工程预约口径，不改变科学或资源边界。

物理空间：只对真实attempt（包括终态但metadata未闭合）、已提交future和本次proposed条件取并集，每个未闭合条件预约160MiB。未启动、未提交的后续条件等其启动前再预约。该160MiB独立于原2GiB监控余量。仍按原actual/合法readonly-forecast pending384MiB结果和monitor预约扣减；5GiB底线、CPU/RAM/Share门不动。

累计生成：始终保留完整未闭合metadata预测（初始640MiB），以及全部尚未产生的四端结果预测（初始1.5GiB），整批初始2.125GiB验证10/24GiB预算。原actual usage与历史生成从不减零；只有实际已写入结果目录才减少该端未来cap，只有原root精确闭合回执才退休metadata未来预测。终态失败/未验收metadata不因进程消失自动释放。这个口径也防止只检查当前384MiB而忘记后续三端生成预算。

首端无其他pending demand时，物理最低df从8GiB变为7.53125GiB（8,086,552,576B）；差额是尚未提交三端的480MiB预测，不是降低5+2或640生成预算。父窗口历史df加拟释放新scratch的示例可能仅剩117,862,400B余量；它不是实际PASS，必须真实释放后重新测df并通过所有原门。这里没有清理、迁移或实际启动。

候选代码：`tagpressure_metadata.py`（保留原closure验证，分离physical/generation），`INTEGRATION_DELTA.py`（原Coordinator helper的最小替换；原resource_gate不改）。Reserve/start/controller forecast的现有调用点不变。root须按当前已发布source基线审查、保留PREP和FINAL literal、重新publish/readback并更新CLIENT pins后才采用；本目录未改任何实际源。

22项有界synthetic控制通过，覆盖首端边界/差1B/不可借monitor、submitted去重、终态未闭合、全批生成耗尽、真实active stat/不能假已产生未来端、合法closure但不退款等。它们不是模拟器native或应用资格。此前候选备份保留，便于公开审计。
