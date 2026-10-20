# 资源合同草案：全部 NON_EXECUTABLE，未授权实施

旧规则正确应用与信号适用性必须分开裁决。此次三资格点精确吻合，STOP历史结论不变。对长时间 trace-driven GPU 模拟，数据不足以证明“cgroup full avg10>25三次”专门测得该任务持续无进展或即将产生安全损害；root仍有大量CPU活动，共享范围可能包含其他工作。也不足以证明可安全取消该保护。IO full 是停顿压力，host与cgroup范围不同，绝不互换。

现有实现约每10.15–10.29s采一次完整资源快照，资格点约30.6–30.8s更新一次；三高点只保证首次至第三次约60s的稀疏资格观察，不是90s连续原始停顿。avg10为平滑趋势，既可能跨越短暂恢复，也不能填补采样空白。源代码仅在资格点更新/reset I/O 计数；非资格低点不会重置（swap有更快reset注释，不适用于IO）。本次所有触发后观察均高，改成“任一低点reset”仍会在同一点停止。无数据支持改25、延长到某任意时长或以host通过来覆盖cg失败。

| 草案 | 收益与主要失败模式 | 最低额外遥测 | 公平性与完整结果验收 | 必须另批的具体变更 |
|---|---|---|---|---|
| A：保持原runtime三资格点STOP | 保留已审计保守边界；共享I/O/正常等待也可能永久消耗完整模拟预算，长任务暴露机会更高 | 为解释下次停机，至少封存cgroup/祖先controls、scope与完成进展序列；规则本身不依赖新增遥测 | 全臂使用同规则和资源准入；STOP计消耗但不计性能，禁止只保留幸存臂；不允许把AG6三封存身份复活 | 即使不改规则，任何新cohort/UUID/budget与新模拟都要授权 |
| B：严格准入 + runtime压力告警、持续无进展、安全条件分离（推荐设计审查） | 保留安全条件的立即处理；避免仅因共享PSI就把仍工作的模拟判无进展。失败模式是忙循环被CPU计数误判进展，或告警放行损害邻居；必须有资源上界和失效关闭 | 时间戳、PID/start_ticks、明确完成语义的instructions/CTA/kernel序列；同时保存paired PSI total/avg、controls/祖先、进程io/faults、设备增量与输出增长。若完成遥测缺失/陈旧则UNAVAILABLE，不能以CPU/rchar/stdout增长替代 | 保留完整host+cgroup paired R2、>5GiB+expected-write、memory/OOM/identity/输出设备与总量限制。原其它门槛不隐式变化。新合同全臂同源、同插桩、同进展判定和同资源上界；终态仍需natural exit0+完整input+strict与身份闭合；warning不生成PASS | PSI从独立runtime终止转为告警的语义；进展采集/故障处理；无进展窗口与恢复条件；共享I/O影响的终止条件；guard/Core任何修改、资格测试和新预算全部另批 |
| C：仍以runtime PSI终止，加入每次观察reset和迟滞/total增量窗口 | 避免稀疏高点跨过已观测恢复；可较清楚表达持续性。对本次全高序列无自动挽救，不能消除共享scope误归因；更密采样本身也增加开销 | 每次实际采样时间、PSI total差、全部恢复点和缺样标记、设备等待与实际进展；完整有界时间窗覆盖，而非只三个点 | 固定全臂cadence与缺样处置；平滑avg与累计stall各有语义，禁止事后调参选幸存结果；所有STOP仍非性能PASS | 任何新退出阈值/窗口/迟滞数值、采样cadence、reset/缺样逻辑及资格验证须独立审批；本数据不支持设新数值 |

B 的可测进展定义草案：在同一PID/start_ticks、同一input/kernel/ROI下，记录“已执行并提交的模拟指令”或“已完成CTA/已完成kernel”的单调计数及UTC+monotonic时间，跨kernel有明确定序。只有实际完成语义可驱动无进展判定；CPU ticks只是liveness辅助，读取字节只是前端消费。当前这些计数均 UNAVAILABLE；thread block 坐标不是完成回执。窗口时长、初始化/长kernel阶段、采样缺失/陈旧处理与证据边界必须在未来新cohort前固定；本包不写可执行注册、不选数值、不回算speedup。

最小未来仪表分两层（仅草案，当前不执行）：

1. 对另行授权的新cohort，在既有资源采样点封存host/cgroup identity与可读祖先io.max/weight/latency、mount/device/inode、io.stat、root+事件已证实helpers+coordinator的io/fault/CPU、输出字节/文件数、dirty/writeback与PSI total增量，保留不可见项UNAVAILABLE。只收已知进程和项目归属，避免全盘/外部命令行扫描。
2. 若模拟本来没有语义进展导出，单独审查低开销单调计数设计与行为等价性。只有第一层仍不能区分共享设备延迟与控制器限制时，再考虑另批最小请求延迟/限速归属仪表；绝不在本轮attach、benchmark或试跑。所有遥测开销纳入合同，映射capture反复哈希的优化也只能另批，不能牺牲身份审计。

推荐下一授权决策：接受本诊断的“触发已证实、底层根因未唯一闭合”，批准 B 的设计/遥测合同审查方向，继续冻结运行授权；若选择未来实验，须另立独立cohort和明确新预算，不能退款/恢复旧AG6。C作为敏感性设计保留，不提出无依据的放宽数值。BA仍0/32、独占fullsim dispatcher；无AE/AD晋升、F仍null，原科学选择规则与原44/GM12等证据不变。
