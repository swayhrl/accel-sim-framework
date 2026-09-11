# C13 adaptive replay admission addendum

状态：`AUTHORIZED_OVERRIDE_FOR_RESOURCE_ADMISSION`

本 addendum 仅覆盖 C13 的**主机资源 admission / 并发调度策略**；不改变 C13 scientific matrix、执行 identity、验收语义、Selective contract 或结果解释边界。

背景：第一次 admission 审计在共享主机上观察到约 4–6% CPU idle、81–93 GiB available memory、memory/io PSI avg10=0，但由于 load/runnable 较高且 swap free 很低，采用了过于保守的全局 reject。该结果仍保留为基础设施审计证据，不是实验失败。之后 C13 改为**渐进式、自适应 admission**。

## 1. 不再作为单独 hard-reject 的指标

以下指标只能作为背景/趋势信号，不能单独阻止 1-way C13 replay：

- `load average > logical CPU count`；
- runnable task count 较高；
- swap 已占用较多或 swap free 很少。

特别地，swap free 低本身不能说明当前正在 swap thrash。必须结合 `vmstat` / `/proc/vmstat` 的实时 swap-in/out 速率和 memory PSI 判断。

## 2. Admission 使用实际 headroom

每次准备启动新的 full-ROI arm 前，连续采样至少 3 个窗口（建议 10–30 s 间隔），记录：

- logical CPU count；
- CPU idle / iowait；
- load average 与 runnable queue，仅作辅助；
- `MemAvailable`；
- memory PSI `some/full avg10`；
- IO PSI `some/full avg10`；
- 实时 swap-in/out rate；
- 当前 `accel-sim.out` 数量；
- C13 已运行 arm 的 RSS、CPU%、状态和前进迹象。

### GREEN — 允许增加一个 arm

同时满足：

- `MemAvailable >= 48 GiB`；
- memory PSI full avg10 `<= 1%`；
- IO PSI full avg10 `<= 2%`；
- iowait `<= 12%`；
- 实时 swap-in/out `<= 4 MiB/s`；
- CPU idle `>= 3%`，或等价可确认至少约 12 个逻辑 CPU 的持续 headroom；
- 没有 OOM / allocation failure /明显系统抖动信号。

在 GREEN 下：若当前 C13 无 full-ROI arm，启动 **1-way**；若已有 1 个健康 C13 arm 且至少稳定运行 3–5 分钟，可升为 **2-way**。

### YELLOW — 只允许 1-way，不增加并发

任一情况：

- CPU idle 约 `1.5–3%`；
- `MemAvailable 32–48 GiB`；
- memory PSI full `1–3%`；
- IO PSI full `2–5%`；
- iowait `12–20%`；
- swap-in/out `4–16 MiB/s`。

若已经有 1 个健康 C13 arm，则继续让它运行，但不启动第二个；若当前没有 C13 arm，可在连续三个采样窗口未恶化时试启动 1-way，并在启动后 3–5 分钟重新评估。

### RED — 暂停新启动

任一情况持续出现：

- CPU idle `< 1.5%`；
- `MemAvailable < 32 GiB`；
- memory PSI full `> 3%`；
- IO PSI full `> 5%`；
- iowait `> 20%`；
- swap-in/out `> 16 MiB/s`；
- OOM / repeated allocation failure /系统明显 thrashing。

RED 时不启动新 arm。除非本 C13 arm 自身出现资源失控或 OOM 风险，不主动杀掉已经健康前进的 C13 arm，更不得操作其他项目/用户进程。

## 3. 当前高负载主机的并发上限

只要整机平均 CPU busy 仍高于约 90%，C13 full-ROI replay **硬上限为 2-way**，即使内存富余也不升 4-way。

只有在多个采样窗口显示：

- CPU idle `>= 8%`；
- memory/io PSI 继续低；
- swap-in/out低；
- C13 单 arm RSS稳定；

才允许重新考虑 3–4 way。该提升不是本轮必需目标。

## 4. 渐进式启动顺序

资源紧张时优先保证“有一个诊断在持续前进”，而不是等待理想空闲窗口。

1. 先启动 1 个 P0 config-only arm；
2. 运行 3–5 分钟后重新采样；
3. 若仍 GREEN，再启动第 2 个独立 arm；
4. 若降为 YELLOW，保持当前 arm，不增加；
5. 某 arm terminal 后立即解析/验收，再按最新资源状态补下一个；
6. 不因其他项目 simulator 数量本身达到某个固定值而停，只依据实时资源 headroom。

优先级仍遵循 C13 Goal：先完成不需要新 binary 的 config-only diagnostics，再进入 Selective 相关 arm。

## 5. 单 arm内存模型

第一次成功启动后，以该 C13 arm 的实测 peak RSS `P`更新后续 admission：

`memory_required_for_one_more = 1.5 * P + 2 GiB`

同时至少保留 32 GiB系统/其他任务余量。因此第二个 C13 arm 只在：

`MemAvailable >= 32 GiB + memory_required_for_one_more`

时允许启动。

如果已有 C12/C13 同类 full-ROI arm 可提供稳定 RSS参考，可用于第一次1-way启动的预估，但第一次 C13 terminal 后必须用自己的实测值更新。

## 6. 资源公平与结果有效性

OS层CPU竞争会影响 wall-clock elapsed time，但不应被解释为 simulated GPU cycle 的架构效果。C13结果仍以 simulator 的 `gpu_tot_sim_cycle`、IPC、translation/cache telemetry 为科学指标；wall-clock仅用于资源管理。

不得因为主机负载不同而：

- 改变 simulator configuration；
- 跳过 primary diagnostic point；
- 修改 trace / registration / modeled PA；
- 将 elapsed time 当作架构性能比较。

每个arm继续执行既定 provenance / terminal / conservation validator。

## 7. 对已有 BLOCKED 状态的处理

此前 `FAILURE_RETRY_AUDIT.md` 中的 admission deferral 保留，不删除、不改写为错误。它代表 Attempt 0 的保守 admission 决策。

在本 addendum 生效后，C13状态应从“等待低全机负载”恢复为：

`C13_DIAGNOSTICS_ADAPTIVE_ADMISSION_AUTHORIZED`

只要至少达到 YELLOW 中允许的安全 1-way 条件，就继续 Goal；不需要重做已经通过的科学 preflight、config preparation、Selective artifact 或 validator。

成功状态仍为：

`C13_MINIMAL_DIAGNOSTICS_COMPLETE_READY_FOR_REVIEW`
