# 并行与内存准入账本

主完成矩阵固定于UTC 2026-10-27T12:22:50.294507+00:00，当时80个本轮模型PID真实可核。较新的准入观察为2026-10-27T20:29:13.499240+08:00，真实本轮live=79。这些是不同时间，不强行相加。

| 项目 | GiB |
|---|---:|
| 宿主MemAvailable | 78.390 |
| cgroup当前内存 | 161.192 |
| cgroup硬上限 | 256.000 |
| cgroup可回收clean inactive file credit | 8.369 |
| 在跑模型RSS合计（共享页可能重复） | 123.044 |
| 自身未来增长预留 | 79.422 |
| 其它保留任务未来增长 | 2.327 |
| 全部未来增长预留 | 81.749 |
| 当前安全新增增长预算 | 63.353 |
| 预算slack | -18.395 |
| 174本地可用盘 | 39.854 |
| 最终provider要求可用盘 | 23.916 |

当前CPU配额384核等价，new executor容量384，合法CPU集合512逻辑/256物理/2NUMA；4仅是pre-exec窗口，不是模型总并发上限。新准入RAM pass=False，disk pass=True，pressure reasons=[]，cgroup OOM事件=0。现有健康模型不因预测预算不足而停止。历史DTC活进程在主快照另有3个，未并入本轮80。

安全增长预算来自min(宿主可用减8GiB、cgroup有效headroom减8GiB)×0.88；它不是实际已经占用的内存。实际内存仍空闲时，现有任务后续可能增长，故同一容量不能再次出售给新模型。输入预测优先同Core成功峰值记录，使用max(768MiB,1.2×历史峰值+256MiB)+128MiB结构余量；失败下界保守保留，无每点固定4/16GiB全局限制。RSS硬限和AS限单独登记。SOURCE ResourcePolicy在本目录RESOURCE_POLICY.json；实现及生产一致化wrapper在主包tools/l2_resources.py和agents/B/l2_consistent_admission_amendment_v1.py。

另有公平性问题：LavaMD的81.18GiB单点长时间未能进入；SGEMM18.67GiB、scalarProd11.49GiB也受已预约growth挤压。20:13的独立测量证明仅自身任务自然释放后的反事实预算足以容纳Lava，存在小任务持续回填使大任务靠后的风险。large_job_review中的75%释放credit保护/25%混填只是待审建议，尚未实现或应用；不承诺释放顺序和ETA，也未下调峰值或中断任何模型。需要审阅其对吞吐、覆盖和外部压力的权衡。
