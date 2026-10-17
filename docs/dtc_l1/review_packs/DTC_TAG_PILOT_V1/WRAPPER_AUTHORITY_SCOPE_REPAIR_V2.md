# Wrapper authority scope repair V2

2026-10-17，北京时间12:12起，V1临时调度器发现两个新EP-L2进程，记录`AUTHORITY_CONFLICT_HOLD_NO_FURTHER_LAUNCH`。两个已启动GEMM继续原样运行；其余五点没有启动。当时无terminal或新的完整性能结果，本次不读取部分周期做决定。

只读核查确认：进程来自独立`/workspace/results/ep_l2_ft20261016/`；binary SHA=`23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee`，configs含ep_l2_ft_mode而无gpgpu_dtc选项，输入为独立vectorAdd；四个原DTC锁均无owner。内存/IO/pressure均在原T阈值内。原HOLD是包装器把**任何其它项目模拟器**都当成DTC launch authority竞争的误报，没有发现DTC锁/源/输入冲突或严重资源冲突。证据在EXTERNAL_PROCESS_CLASSIFICATION_V1.json及原RESOURCE_SAMPLES。

用户Goal明确允许普通runner/index/manifest包装的确定性修复，并要求检查其它项目资源；没有要求机器上只有DTC项目。V2只修正这个归属判定：同一来源指纹且无DTC配置的EP-L2 FT进程单列为other project；未知进程、其它DTC simulator/authority和旧锁owner仍阻止启动。所有项目仍计入同一host/cgroup memory、swap、disk、IO pressure，原数值阈值和最多2个**新DTC**并行不变。不因新结果改变参数或选择规则。

所有原文件（含POLICY、七点manifest/spec、配置、已封存66文件）保持逐字节不变。新增版本只涉及wrapper：wrapper_scope_v2.py、run_pilot_v2.py、attempt_v2.py。没有改Core、runtime、parser、输入、Tag/PIB/finite服务、评分、timeout或失败保留规则。V1使用过宽的外部进程分类，其原0-conflicting-external约束在V2按已核项目归属执行；不是把不明DTC冲突设为合法。

交接只作用于本T自己的临时foreground进程：核对V1 PID/start_ticks、保留V1状态和HOLD，再结束该调度器（不向任何runner、time group或simulator发信号）。确认其进程及flock已释放后，V2取得**同一T锁**。两条RUN_START/spec/UUID/PID/start_ticks逐项核对后只读adopt，不重启、不延长原runner已持有的timeout；未来五点沿用原UUID与原完整spec，仅不可变runner版本单独记录。始终只有一个T合法临时authority，无第二套persistent dispatcher；原A及EP-L2所有进程/锁只读。

修复版本及收据在任何后续attempt前push+fetch-back。最早原七点预注册提交仍是ebdbbc753，在全部新性能之前已推送回读。本修复不能抹去V1 HOLD或变成新的科学模型身份；最终矩阵及报告披露两代wrapper和交接。若adoption/源/输入/真实资源检查失败，保留STOP，不靠修改模拟器或重发UUID消除。
