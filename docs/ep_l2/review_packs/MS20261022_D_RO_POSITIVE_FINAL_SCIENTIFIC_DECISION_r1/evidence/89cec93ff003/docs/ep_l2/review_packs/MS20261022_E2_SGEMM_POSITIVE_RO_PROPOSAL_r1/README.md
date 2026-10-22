# SGEMM正向RO：仅申请一次新F及精确旧S复用修订

**待用户批准；新增应用0，中央登记/代码/生产main未修改。** 本提案只申请1个新F，原累计50→实际启动后51；失败也计费，不自动重试或转为两端方案。

C已对原完整SGEMM进行唯一一次离线认证：64480条RO行（读行的65.61%）、75423744次读lane-line引用（全局读引用的98.5866%），33792条行因写入排除。E独立核对了68项制品/分类/原始回执与输入范围，未重读trace正文。正向证书、新F配置、输入/profile独立资格与准确SHA均已封存。已有18门证据与E17项native/26预期检查只按同源适用性复用；没有重新执行。

同main61/d010/9dd、原完整1658916864指令/1kernel/3command、W/V/T/M=1、1168 payload、P1。新F只改5项证书绑定/readonly scope；普通选项与原S/F相同。原S E047仍有效，因T/M关闭时没有RO runtime，可作为比较锚点；但原比较规则把辅助证书SHA纳入不变量，必须明确批准BASELINE_EQUIVALENCE_AMENDMENT_FOR_APPROVAL.json的窄域等价复用修订，不能直接绕过accept_pair或改写旧记录。

|申请项|范围|
|---|---|
|完整应用|仅V5_SGEMM_MAIN61_POSITIVE_RO_F，1次|
|比较|同原S E047构成新显式探索比较；旧S/F原样保留|
|资源预案|1CPU、12GiB预留，原共享CPU/RAM政策不变；实际启动前全门禁|
|结果硬上限|端点384MiB，E资格metadata128MiB，collector32MiB；总544MiB封套|
|时间预估|暂按30–60分钟规划，旧F实测30.72分钟；新路径最坏耗时未知，不保证结束时刻，不恢复已取消截止/timeout|

C约6.9MB已生成制品保持计费，256MiB未用预留已释放；不再把旧800MiB预测全额重复计入。未来按真实累计账加尚未生成的本提案封套审查，不能归零或双计metadata。当前累计空间快照见CUMULATIVE_RESULT_AND_COST_PROPOSAL.json，不冒充启动时准入。

本实验先回答真实RO准入/事务、Tag-detach和正确退尽是否出现。RO覆盖不保证miss、pending冲突、detach或加速。完整终验有效但detach=0仍保留为有效零结果，不强迫触发；S/F不提供Tag单独因果收益。

A2现有源码/native图和D条件科学选择已接收；C最终证书已到，A2/D最后的本人metadata增量仍需其前台回读。E已独立闭合精确loader/域/证书绑定，不代写peer结论。任何实质矛盾均停止受影响未启动条件；运行前仍须批准后的原中央受控adoption与真实资源/身份准入。
