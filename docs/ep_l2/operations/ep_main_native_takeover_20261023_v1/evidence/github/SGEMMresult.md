# SGEMM 的 detach=0 已得到定量解释

E051 已由原中央 API 接收为 `CURRENT_ACCEPTED_DIAGNOSTIC_POINT`，不是S/F性能配对。真实native exit0/wait0；完整 **1,658,916,864** 条指令、64slice、343,442 cycles，耗时31.10分钟。

|测量域|实际值|含义|
|---|---:|---|
|已接受全局读请求|2,452,480|原RO摘要的request-acceptance统计|
|已接受证书候选请求|2,317,312|正向证书实际被识别；不是空证书|
|可见RO候选head观测|2,282,704|head/物理周期观测，与请求计数不同|
|其中resident hit|2,282,704|可见候选全部缓存命中|
|实际RO事务／合并|0／0|没有进入RO事务生命周期|
|原始Tag reservation-fail|0|仅覆盖已探测head，不能外推被跳过路径|
|实际relieve／detach|0／0|没有可释放Tag的活跃RO事务|

**直接原因是本条件没有产生RO事务，因而没有可detach的RO受害者。** 可见候选命中已有缓存；这不是“发生Tag压力但detach失败”的证据，也不能表述为Tag在所有路径始终充足。2,672,548次可见head观测中105,742次上游跳过探测，原始压力为NA；其余2,566,806次探测未见全reserved同set压力。

旧SGEMM为空证书导致无RO候选，新SGEMM证书正向但无RO事务，是两个独立条件。旧FWT则由整个epoch同line写入排除全部131,072条含读line。这些上游解释均保留原身份，不能回填旧日志。

本端首次自动解析FAILED，是E解析器误拒“同343442周期的kernel结束快照→epoch关闭快照”。两组完整257条record仅epoch_closed从false变true，全部212计数不变。最小离线修复后重新验证原raw、完整指令/64slice/源等式/退出与资源退尽，并实际复核main/archive/config/input/oracle SHA；原中央追加补充验收。**原FAILED执行行、run_status、parser.log、HOLD历史及第51次费用完整保留，未重跑或退款。**

其他旧positive-RO应用已有RO事务，但缺少局部压力、候选过滤及前端门控的历史观测，原因仍UNKNOWN。E的完整Goal尚未完成；当前仅一次新应用授权已用尽。最低成本追加候选是CFD（旧端7.38分钟、51,678个RO事务）；必须先获额外科学范围批准并独立完成新资格，不自动启动。见conditional_followup中的精确元数据审查。

完整计数见 `NUMERIC_PROJECTION.json`、真实接受证据见 `CURRENT_ACCEPTED_POINT.json`。D可立即消费这一个已接收诊断点；D后续ACK不是E定量归因前置。
