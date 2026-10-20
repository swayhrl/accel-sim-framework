# 根因矩阵

总体 `ROOT_CAUSE_UNRESOLVED`。直接触发原因已知：冻结 cgroup I/O full PSI 规则。造成该范围 I/O 等待的唯一任务、请求或设备限制尚不确定。

| 判断/候选机制 | 置信标签 | 直接证据与可能路径 | 反证/限制 | 缺失的区分指标 |
|---|---|---|---|---|
| cgroup PSI 冻结规则触发 | OBSERVED | 28样本、三资格点26.50/60.09/56.22；精确间隔复算一致 | 这是策略触发原因，非设备根因 | 无；RECOMPUTATION 已足够复核触发 |
| 共享 cgroup 中其他 I/O 活动/共享存储拥塞参与 | SUPPORTED_HYPOTHESIS | q1-q3 cgroup9:127仍读273.75MB/66833次，已证实AG6三实例+coordinator read_bytes均无增长；host md127写等待高 | 不可逐字节做减法归属；缓存、writeback、退出进程/线程记账、层叠设备会妨碍归因；低host PSI不能排除共享设备拥塞 | 历史作用域/祖先映射、项目归属的请求延迟与阻塞时长 |
| AG6 自身持续 trace 冷读触发高压 | DISFAVORED（限触发窗口） | cat 最后 read_bytes=105,807,872、rchar=555,356,272；早期确有 trace/helper 读取 | 从row15至row28均持平；q1-q3 root/helper均无新读取。不能排除此前读入、预取或延迟写回影响 | 时间戳绑定trace消费/完成计数、异步I/O归属；本轮不读trace |
| root major faults/交换抖动 | DISFAVORED | root及helpers majflt=0；memory PSI=0、pswpin/out和cg swap无增长 | minflt增加是内存分配/轻缺页，不能直接解释为存储等待 | 更细存储等待需要另行仪表；无资格生成新证据 |
| 观察者重复哈希/映射工程开销 | OBSERVED（开销）；UNRESOLVED（作为STOP根因） | 8369 captures；源码每次重哈希映射文件；coordinator首末rchar增100,334,069,583B，CPU增11472ticks，写字符64,689,442B | read_bytes始终0，主要是缓存/元数据；q1-q3 CPU仅149ticks、wchar+670,917B、write_bytes+737,280B。高压阶段已脱离密集mapping期 | 每capture耗时、缓存命中、write/fsync阻塞、排队与writeback归属 |
| 小输出/事件 flush、fsync 或文件系统元数据延迟 | UNRESOLVED | 8369 maps小文件、事件flush、资源日志；可能引起元数据/回写等待 | stdout仅48KB且触发窗口不变；大小不能排除长延迟。审计过的 capture/logger 路径未调用fsync，未保存全程序或底层fsync证据 | 单次write/close/fsync等待、文件与设备映射、输出增长时序 |
| cgroup io.max/weight/祖先或延迟控制限速 | UNRESOLVED | 高cg低host与限制兼容，但不是限制证据 | 历史未记录；当前io.max空、weight100只是当下且祖先不可见，不能追溯证明或否定 | 运行时及祖先限制快照、限速延迟/控制器计数 |
| writeback/overlay artifact 文件系统效应 | UNRESOLVED | cg/host写持续；当前overlay，历史output dev156/mount4461 | 无历史mountinfo/dirty统计，无法断言历史同一backing filesystem或哪个写入者 | 历史mount/device provenance、dirty/writeback/归属延迟 |
| 磁盘空间、OOM/内存安全门槛 | DISFAVORED | disk>=41.95GiB，host available>=275GiB，cg headroom>=191GiB，OOM/Swap无增长 | 不排除设备慢；空间充足不能推出无I/O压力 | 不影响本次STOP归类 |
| 模拟完全无活动/自然完成/性能结果 | DISFAVORED（完全无活动）；OBSERVED（未完整验收） | q1-q3 root CPU增6147ticks且每样本R；三实例受控-9；STRICT失败 | CPU活跃可来自忙循环，不能等于有语义进展或完成；stdout坐标无完成证明 | 完成instructions/CTA/kernel/cycle的单调计数与时间序列 |

PSI 的多 CPU 聚合和范围人口差异可解释“root活跃与高cg full并存”，无需假设读数错或强行认定限速。其为压力信号、非单任务进展计。参见 [内核接口](https://docs.kernel.org/accounting/psi.html) 与 [v6.8 多CPU模型](https://github.com/torvalds/linux/blob/v6.8/kernel/sched/psi.c)。发行版精确历史内核实现仍未封存。

此前全监控时段 host full最高7.34、cg最高65.13。前三分钟cg=0；row21出现5.25，row22首次>25；后续每个已存样本均>25，未见恢复窗口。策略本次无WARN、无内存警告。低于门槛的未采样间隙不可重建。
