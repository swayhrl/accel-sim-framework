# DTC memory risk review V1 — read-only, not applied

可以用受控单点试验评估更激进的准入，但现有证据**不能证明**削减增长预留后仍绝不跌破10GiB。建议先测试已登记、从未消费的 Lava DH-P0；不一次启动125点，不降低任何canonical RSS/AS硬cap，不改变Core、输入或科学身份。

## 实测数字与含义

本包数字对应 `READONLY_EVIDENCE.json` 快照，非持续实时状态；采样顺序也不是宿主机所有指标的原子快照。

| 项目 | GiB / 说明 |
|---|---:|
| 新实验79个绑定模型的RSS合计 | 120.599 |
| 全部82个观测模型RSS合计 | 140.491 |
| 其中其他模型 | 19.891 |
| 当前最低直接headroom：min(host MemAvailable, cgroup max-current) | 80.060 |
| 原准入预算：(最低可用量−8GiB)×88% | 63.476 |
| 现有模型未来增长预留，包括peer | 81.470 |
| 单个Lava DH-P0预测峰值 | 81.178 |
| Lava原硬cap，保持不变 | 122.767 |

所以“约63GiB安全headroom”与“约80GiB实际headroom”主要是预算定义不同，不能混用。已驻留RSS已经体现在可用内存中；增长预留是额外未来需求，不应再把全部RSS重复扣一遍。RSS求和可能重复计算共享页面，与旧快照的匿名PSS不能直接等同；时刻变化和自然结束也会改变总数。

197条同Core成功回执的观测RSS：中位0.770GiB、p90=2.5GiB、p95=9.262GiB、最大67.336GiB。它们混合程序、配置和工程验证合同，且已完成样本偏向短任务；这不是35程序独立同分布样本，也不是所有模型可采用9.262GiB硬上限的证据。

Lava四条同Core成功回执覆盖CM/CH/DM/DH，观测峰值67.278–67.336GiB，宿主运行3.34–6.18小时。四条DONE的SHA独立回读匹配。其81.178GiB预测来自 `1.2×历史最大观测峰值 +0.25GiB +0.125GiB`，比最大观测峰值多13.842GiB，具有可解释来源。历史采样峰值仍可能漏掉短突发；四条记录不能给未来分配速率或峰值硬上界。

## 有无可以释放的保守余量

只读尾窗发现：hybridsort、两条SYRK、GEMM、3MM最近约346秒的35个采样RSS基本恒定；cutcp略下降。2DCONV只出现约0.000384GiB/s的正增长。Lava成功CH的末尾191秒保持67.278GiB，然后自然结束为0。这说明晚期模型仍按完整峰值留增长空间，可能过度保守。

但这些采样间隔约10.2秒，且只覆盖晚段。它们不能排除采样间突发、下一个kernel的加载增长，也不能证明所有79点以后都不增长。Lava何时达到67GiB无法由末尾窗口和最终DONE重建；另三条旧Lava资源日志超过1MiB压缩或16MiB解压限额，明确未全量扫描。不能把缺失成长曲线解释成零增长。

读取边界：只读每点末尾256KiB的记录内容。gzip资源文件无法直接把压缩尾块当JSON，本包仅对≤1MiB的小资源文件有限解压，单文件解压硬限16MiB，再保留末尾窗口；超界跳过。未扫描大型模拟raw日志。

## 三种准入办法比较

| 办法 | 机会 | 主要风险 |
|---|---|---|
| 完整未来峰值预留 | 对同时增长较保守，维持现合同 | 大作业饥饿，晚期平稳模型仍占增长预算；预测本身也非严格上界 |
| 对未来增长打折 | 可回收平稳模型的部分预算 | 缺乏相关性与burst上界；并发增长相关时折扣失效；不应压低canonical硬cap |
| 实际headroom＋快速监控 | 可以先让一个大模型推进、积累真实增长曲线 | 只能条件保护，外部突变/大alloc可能跨采样击穿；暂停保留RSS，可能等待自然释放甚至死锁 |

当前81.470GiB预留加Lava81.178GiB，总未来预测162.648GiB，而直接headroom减10GiB仅70.060GiB。整体按50%打折仍需81.324GiB，不够；按25%打折可准入，但隐藏121.986GiB预测增长，不能叫“保持10GiB已证明安全”。仅去掉Lava的13.842GiB预测padding也无法解决此总缺口。

## 操作系统能力与未证明项

实测kernel6.8.0-45、Python3.10.12，`os.pidfd_open` 和 `signal.pidfd_send_signal` 均可用；精确generation绑定可避免PID重用误伤。这里只检查API存在，不向模型发送信号。

宿主swap约2GiB且仅45,056字节空闲；不能指望swap承接新大输入。当前cgroup `memory.max=256GiB`、`memory.high=max`、`memory.swap.current≈19.3MiB`。cgroup2挂载为rw/nsdelegate，root的访问检查显示可写，但未实际测试controller委托/子group创建/写入成功；`cgroup.subtree_control` 为空。不可据此直接更改共享memory.high、memory.max或全局swap。

SIGSTOP不会腾出已驻留RSS。暂停一个60GiB模型仍占60GiB；若所有能完成释放内存的作业都暂停，headroom不会因暂停自动回升。恢复条件不满足时需要自然完成或外部释放，而非反复SIGCONT试探。旧worker还可能把暂停解释为producer stale或wall timeout，所以必须先通过A/B的暂停感知frontend资格，不能直接暂停当前79个健康模型。

## 建议的可测pilot

目标：`E2-DTCL2MLP-ddb6806316876a85-DH-P0-V1`。现已登记、未consumed；Core9eedb313 / FW02775fd7。实际启动必须仍由唯一owner经原生入口消费该合法身份，不reset、不regrant、不降低122.767GiB cap。

1. 先确保monitor ACK、pidfd/generation绑定及pause-aware frontend资格。heartbeat≤1秒、headroom样本年龄≤0.5秒，新的大pilot数量最多1；有未观测启动claim时不继续加点。
2. 采用直接 `min(host MemAvailable, cg max-current)`，不把推测可回收file credit当保证。无新增OOM/max事件、活跃swap-out或明显PSI，且headroom≥30GiB，才允许该单点进入受控试验。
3. 建议20GiB停止新准入并提前暂停此已绑定pilot；10GiB作为紧急floor/违约报警，不能等到10GiB才首次采样。暂停动作不记作释放内存。其他健康模型应继续拥有完成与自然释放的通道。
4. ≥30GiB连续10秒、压力解除、heartbeat新鲜后，一次只恢复一个；恢复后60秒不同时增加新作业。若所有进展源都暂停且无释放，显式工程审查，不自动把paused算finished。
5. 起步120秒以250ms轻量采样headroom、VmRSS/VmHWM，测最大单步增长、达到64GiB时刻、监控延迟与暂停后RSS；稳定后可改1秒。保留暂停区间，令timeout/producer合同正确识别，而非写失败替代结果。

阈值需通过实测校准：`pause ≥ floor + 最大增长率×(采样间隔+样本年龄+动作延迟) + 外部突发 + 测量误差`。例如增长≤8GiB/s、三个延迟各0.25s、外突≤2GiB、误差≤1GiB时，所需pause为19GiB，20GiB才条件足够。当前尚未证明这些上界；单次45GiB外突可从50直接跌至5，即使下一拍暂停也已越线。

`memory_guard_cpu_model.py` 的18项fake-trace检查覆盖迟滞、heartbeat、身份、单pilot、恢复冷却、RSS保留、死锁、压力门和burst击穿。它不调用任何OS进程控制API；通过测试不等于获得真实内存安全上界。

本包未启动模型、发送信号、改sysfs/swap、降低cap或修改生产合同。由DTC-MAIN审阅A/B资格与本报告后决定是否实施单点pilot。
