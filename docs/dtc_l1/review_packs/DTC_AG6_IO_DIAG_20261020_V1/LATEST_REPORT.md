# AG6 I/O 资源诊断：封存证据审查

结论：`ROOT_CAUSE_UNRESOLVED`。冻结 I/O STOP 规则执行正确；现有证据不能将其等同于 AG6 停止前无进展、磁盘耗尽或 cgroup 限速。推荐科学裁决优先审阅方案 B 的资源合同设计与最小遥测需求，暂不批准任何模拟、旧 UUID 重用、门槛修改或实验预算。

证据基线：Goal `02ead59800e4559f90e17e28c898a7846c292b67`，历史事实锚点 `d9c192544622579a93d3efad98f56f82536c2fbe`；原 `huangrulin-174`，独立 worktree、独立证据目录。执行源码不是按当前文件名推定：RUN_START 指向的 `62323c40df0add726cae52a96ca946e589f00343`、manifest SHA 与全部 49 个注册源码 SHA 已逐一核验。详见 [来源](IO_SOURCE_PROVENANCE.md)。

28 行完整封存监控一次流式提取，独立复算三个资格点：

| UTC（北京时间为次日 +8h） | cgroup full avg10 | host full avg10 | 资格计数 |
|---|---:|---:|---:|
| 2026-10-19 16:57:13.230020 | 26.50% | 3.87% | 1 |
| 2026-10-19 16:57:44.032941 | 60.09% | 6.27% | 2 |
| 2026-10-19 16:58:14.835502 | 56.22% | 6.23% | 3 → STOP |

间隔 30.802927342 / 30.802555226 秒，资格计数与发布回执完全一致。实际 fork monotonic=9180789395716963；RUN_START 16:53:38.034051Z → 规则触发 → guard 16:58:15.396452Z 封存（wall 277.3427 秒）→ wrapper 16:58:16.004615Z 收尾异常。三实例历史 returncode=-9；本轮未发信号。自然 exit0、完整 cycles、有效性能结果均不存在；后续 KeyError/retirement join 不是第二次性能测量。

最有区分力的观察：

- 首资格点至 STOP 的 61.6055 秒内，root CPU 增长 6147 ticks（若 USER_HZ=100，约 61.47 CPU 秒）；root/helper 的 rchar、read_bytes、wchar 均持平，root majflt 始终 0。CPU 活跃能反驳“已证实整体无活动”，不能证明模拟指令/CTA 正确完成。未保存可用的完成进展序列。
- 同窗口共享 cgroup 的 `9:127` 增长 273,747,968 read bytes / 66,833 reads 与 56,659,968 write bytes；`8:80` read=0、write=15,605,760 bytes。不能跨堆叠设备求和。同期 host `md127` 完成写的累计等待/次数约 492.42ms；这是共享设备级拥塞线索，不能定位到某任务、某文件或限速器。
- 监控父进程前期读取字符量累计约 100.33GB、写字符约 64.69MB，源码确实在每次 mapping capture 重验并重哈希已映射文件，形成显著观察者负担。它的 read_bytes=0；触发窗口仅增加约 0.74MB 写入且不再大规模哈希，不能把前期负担直接判为后期 PSI 的唯一根因。
- 磁盘最低 45,047,496,704B（约 41.95GiB）；host/cgroup memory full avg10 均 0，swap/OOM 计数无增长。磁盘、OOM、交换抖动不支持为此次停止原因。

PSI 是范围内停顿压力指标，不能解释为磁盘利用率或限速证明。多 CPU 的聚合会让部分执行与较高 full PSI 并存；不可用低 host PSI替代 cgroup PSI，也不可将共享 cgroup 直接视为 AG6 专属范围。参见 [Linux PSI 文档](https://docs.kernel.org/accounting/psi.html) 与 [Linux 6.8 实现说明](https://github.com/torvalds/linux/blob/v6.8/kernel/sched/psi.c)。

主要缺口：历史 io.max/io.weight/祖先限制和挂载拓扑未保存；没有请求级延迟、fsync 阻塞、dirty/writeback 与来源归属；没有完成指令/CTA/kernel 的时间序列。当前一次只读快照 io.max 为空、weight=100，但仅为 CURRENT_ONLY_NOT_HISTORICAL，不能排除历史或不可见祖先的限制。

请科学裁决 [A/B/C 草案](RESOURCE_POLICY_OPTIONS.md)：A 保持保守 STOP；B 将 runtime PSI 告警、实际安全条件与可验证的持续无进展区分，仍保留严格 paired R2、>5GiB/预期写入、memory/OOM/identity；C 提出连续窗口与恢复迟滞设计，但没有足够证据设定新数值。推荐先批准 B 的设计审查与未来遥测合同；任何实现、资格测试、新实验均需另行明确授权。

AG6=1/4 已消耗、0有效、3 UUID 封存；BA=0/32；O provisional、F=null。原 44/GM12/T/U、旧 selection、BA 分支/原始数据、Core/guard/模型均未修改。本轮模拟/测试/fixture/编译/benchmark 启动为 0，进程信号为 0。诊断完成后 STOP，等待科学裁决；无自动继续、轮询或后台任务。

审阅入口：[完整时序](STOP_RECONSTRUCTION.tsv)、[进程计数](OWN_PROCESS_COUNTERS.tsv)、[设备计数](CGROUP_DEVICE_DELTAS.tsv)、[根因矩阵](ROOT_CAUSE_MATRIX.md)、[预算边界](BUDGET_AND_SCIENCE_BOUNDARY.json)、[发布回读](PUBLICATION_READBACK.json)。
