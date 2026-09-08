# C12 / C5 激进并行追加指令

状态：`AUTHORIZED_AGGRESSIVE_PARALLEL_OVERRIDE`

本文件只覆盖 C12 原 Goal 中“P0 完成后才启动 P1”和“通常最多 6-way”的保守调度规则；**不改变任何 C11/C12 科学语义、22 点矩阵、hash、binary、config、registration、trace、terminal gate 或结果验收标准。**

当前目标：在保持结果科学有效性的前提下，更积极利用共享大机的空闲 CPU/内存，让彼此独立的 C5 arms 并行执行。

## 1. 核心原则

不同 C5 arm 是彼此独立的完整模拟任务。Host 上并行与否不改变模拟 cycle/IPC 语义，只要：

- 每个 arm 使用冻结的相同 binary/config/trace/registration identity；
- 每个 arm 有独立 output dir；
- 不共享可写 simulator state；
- 没有 OOM/资源异常导致不完整执行；
- 每个 arm 独立满足 terminal gate。

因此允许在两个 F0 尚未完成时，**猜测性地提前启动 P1/P2/P3 的独立 arms**。这些提前结果先标记为：

`SPECULATIVE_EARLY_EXECUTION_PENDING_BASELINE_GATE`

只有两个 F0 都 terminal PASS、identity/hash/preflight 未变化后，早跑的 arm 才可按自身 terminal gate 晋升为正式 C5 PASS。

如果 F0 暴露全局 binary/config/registration/launcher 语义问题，所有受影响的早跑 arm 必须 quarantine/invalidated 并按修复后的 identity 重跑；不能为了节省时间保留有疑问的数据。

## 2. 当前并发目标

不要终止当前健康运行的两个 F0。

在当前两个 F0 基础上，立即尝试把总 simulator worker 数提高到：

`TARGET_CONCURRENCY = 6`

即额外启动最多 4 个独立 arm。

优先顺序：

1. P1 剩余 arms；
2. P2 Lseg sensitivity；
3. P3 F1。

只要总 worker 未达到 target，调度器可从上述 priority queue 继续取下一个未启动、未完成、未锁定的 arm，不需要等待同阶段其他 arm 完成。

### 6-way 稳定后允许试 8-way

当 6-way 连续至少 5 分钟满足：

- memory PSI full <= 1%；
- io PSI full <= 2%；
- iowait <= 10%；
- MemAvailable >= 64 GiB；
- swap-in/out <= 4 MiB/s；
- 无 worker OOM / resource kill；
- CPU 尚有明显余量，且系统不是持续 >95% 忙；

允许提高到：

`TARGET_CONCURRENCY = 8`

8-way 仅是资源利用试探，不是科学必要条件。如果出现资源压力，自动退回 6→4→2，不把资源降级视为 Goal failure。

不要为了达到 8-way 而抢占/杀死其他窗口或系统进程。

## 3. 每-arm 独占锁，解决重复 launcher 风险

必须在启动任何新 arm 前实现一个轻量 per-arm ownership guard。

建议锁目录：

`/workspace/vm-m4b-speculative/c5-results/.arm_locks/`

每个 arm 唯一锁名必须包含 ROI + arm + lseg，例如：

- `prefill__f0.lock`
- `decode1__f7_lseg10.lock`

可以使用 `flock` 或原子 `mkdir` 实现。

要求：

- 同一 arm 任意时刻只能有一个 launcher owner；
- shell parent/pipe/tee 不应被误判为多个 simulator；
- 检查真正的 `accel-sim.out` child PID；
- 如果发现两个真正 simulator 写同一 output dir，立即只停止 C12 自己重复启动的后发 worker，保留最早合法 owner，并记录审计；
- 不得用模糊 `pkill accel-sim`、`killall` 或影响其他窗口的命令。

arm 完成或失败隔离后释放对应 lock。

## 4. 独立输出与原子状态

每个 arm 必须继续使用 C11 manifest 冻结的独立 output dir。

新增/保持一个 live 状态文件，例如：

`C12_LIVE_ARM_STATE.tsv`

至少记录：

- roi
- arm
- lseg
- state (`NOT_STARTED/RUNNING/PASS/FAILED_RETRY/INVALIDATED`)
- owner_pid
- simulator_pid
- lock_path
- start_time
- current_kernel_marker_count
- expected_kernel_count
- binary_sha256
- config_sha256
- trace_sha256
- registration_sha256
- attempt_id

状态更新应通过临时文件 + rename 或其他原子方式，避免多个 launcher 同时破坏状态表。

## 5. 早跑 arm 的晋升规则

猜测性提前运行的 P1/P2/P3 arm 不因为“早跑”而自动无效。

在两个 F0 PASS 后，对所有早跑 arm 做一次 promotion audit：

- binary hash == F0 binary hash；
- Core/Framework functional anchor一致；
- config/trace/registration hash未变化；
- output dir只存在一个合法 simulator owner；
- terminal marker/telemetry/conservation/arm-specific gate全部 PASS；
- 无资源 kill / truncated log。

全部满足：

`SPECULATIVE_EARLY_EXECUTION_PENDING_BASELINE_GATE -> PASS`

任一关键 identity 不同或 F0 揭示全局执行问题：

`-> INVALIDATED_AND_RERUN_REQUIRED`

## 6. 资源调度细化

每 30 秒采样：

- MemAvailable；
- memory/io PSI；
- iowait；
- swap MiB/s；
- 每个 worker RSS；
- 当前真正 simulator worker 数；
- CPU utilization/load。

### GREEN

- MemAvailable >= 32 GiB
- memory PSI full <= 1%
- io PSI full <= 2%
- iowait <= 10%
- swap-in/out <= 4 MiB/s

允许维持/增加并发，最高 8-way。

### YELLOW

- memory PSI full 1–3%，或 io 2–5%，或 iowait 10–20%，或 swap 4–16 MiB/s，或 MemAvailable 20–32 GiB

不启动新 arm；让健康的短/中等任务继续；batch 自然完成后把 target concurrency 减半。

### RED

- MemAvailable < 16 GiB
- memory PSI full > 5%
- io PSI full > 8%
- iowait > 25%
- swap-in/out > 16 MiB/s 连续两个窗口

停止新增 worker。仅当明确持续 thrashing/OOM 风险时，终止 C12 自己最新启动的资源受害 arm；保留 raw/sidecar 到 failed attempt 后，降低并发重跑。

少量 host-wide swap activity不是阻塞条件。

## 7. 失败隔离

某个 arm 失败时：

- 不杀其他健康 arm；
- 保存该 attempt 的 raw log / time-v / resource snapshot；
- 分类为 launcher/parser/resource/correctness；
- 普通问题修复后只重跑受影响 arm；
- parser bug 且 raw log完整时只重解析；
- resource victim 降并发后重跑。

只有会改变模拟语义的 Core/config/registration/trace/binary 修复，才触发原 C12 的全矩阵 identity invalidation 规则。

## 8. 优先队列建议

若当前两个 F0 已在运行，额外 4 个 worker优先：

- decode1 F2
- decode1 F5
- prefill F2
- prefill F5

若其中某点已启动/完成，则依次替换为：

- decode1 F7-L10
- prefill F7-L10
- decode1 F8-L10
- prefill F8-L10
- decode1 F9
- prefill F9

之后 P2，再 P3。

目的是尽快获得跨 ROI 的结构对照，不要求同一 ROI 全部先跑完。

## 9. 不变的科学边界

本追加指令不允许：

- 改 22 点矩阵；
- 根据中途性能跳过不利 arm；
- 改 PA mapping；
- 混合不同 identity；
- 用 A/C4 数字替代 C5 F0 baseline；
- 新增 F6/F3/F4/H0/KV segmentation/12K/M5；
- 修改 Window A/B；
- 把 host wall-clock 当作模拟性能指标。

## 10. 验收与最终状态

最终 22/22 的 terminal/科学验收仍完全遵循原 `C12_ACCEPTANCE_MATRIX.md`。

并行本身还必须通过 `C12_AGGRESSIVE_PARALLEL_ACCEPTANCE.md`。

最终状态仍只有：

`C12_C5_FULL_ROI_COMPLETE_READY_FOR_REVIEW`

或真正有证据的 architecture/provenance/correctness hard blocker。
