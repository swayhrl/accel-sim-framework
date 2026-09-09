# C12 failure and retry audit

## Parser-only setup correction

在任何 simulator 启动前，C12 执行器首次读取 C11 command manifest 时使用了错误
字段名（manifest 实际为 `trace_sha256`、`exact_command`、`binary`，而非内部
别名）。该错误发生在静态 collect/preflight，未创建 C5 run directory、未启动
simulator、未改变输入或模拟语义。字段映射已做最小修正并重新通过静态 C11
validator。

## Runtime attempts

运行中的 arm、终端状态、失败原因和任何重试会写入 `ARM_STATUS.tsv`。失败的原始
目录绝不覆盖；如果需重新执行，将移入本 C12 的失败隔离区并保留 SHA-256 索引。

### P1 detached-launcher pre-simulator termination

`P1_DETACHED_LAUNCHER_TERMINATED_20260908T0758Z` 中保留了 Prefill/Decode1
的 F2/F5 四个不完整 launcher 目录。该 launcher 在 trace-list 复制/链接期间即
已终止：四个目录都没有 `run.log`、`C12_ATTEMPT.json` 或 simulator 输出，因此
没有启动 `accel-sim.out`、没有 kernel marker、没有 telemetry，也不构成 C5
attempt 或性能结果。为避免覆盖或混入，这些目录已经移动到 C12 专属失败隔离区；
随后以相同冻结 manifest 和新的、每 arm 独占锁 owner 启动了当前四个真实 arm。

### Decode1 F0 parser-only reparse

Decode1 F0 于 `2026-09-08T15:59:27Z` 正常结束（exit `0`）。原始 `run.log`
完整，`740/740` kernel marker 与 `740/740` telemetry record 均通过，且对象与
PTE 守恒均通过；其 SHA-256 固定为
`96097ee02fff4b31219339bf673e53af826d8b9c98cb3dd1d3657767b8e0025d`。首次
collector 将合法浮点 `gpu_tot_ipc=119.4444` 错当作整数字段，并错误解析 GNU
`time -v` 的 `h:mm:ss` elapsed 形式。因此该 arm 最初仅以
`FAILED_DIAGNOSING` 隔离，**没有重跑 simulator**。

解析器现将 IPC 验证为有限浮点，并以 GNU time 标头的最后 `):` 分隔符解析 elapsed
（含前导制表符），随后仅对同一 raw log 重解析。结果为 `PASS`，elapsed 为
`30657.0` 秒，冻结 Core、binary、config、trace、registration 与 raw-log SHA
均未变化。该修复不改变任何模拟语义，也不使其他 arm 的 identity 失效。

### Scheduler child-command correction

Decode1 F0 释放一个 worker 后，审计发现 scheduler 构造 Python child 命令时漏掉
`c12_c5_replay.py` 脚本路径；唯一 child 因此立即退出且没有创建任何候选 arm 的
run directory 或启动 simulator。该 scheduler 只有该一个僵尸 child、没有控制
任何 `accel-sim.out`，故在确认七个真实 C12 worker 独立存活后，仅重启了该
scheduler。修复后的命令显式包含 replay 脚本路径。当前 host 的 `load1` 约为
`713/512` CPU，未满足 8-way admission；scheduler 因而正确维持 7-way，待资源
恢复后以冻结 queue 的下一个 `decode1:F8:10` 填槽。此项纯属调度/launcher 修复，
不变更任何 C5 输入、身份或模拟语义。

### 资源采样

`RESOURCE_HISTORY_V3_TRUE_SIM.tsv` 记录每 30 秒的真实 simulator PID/RSS、PSI、
swap activity 和 iowait。到本次审计更新为止，曾有单窗口的 PSI 或低于 4 MiB/s
的 swap 波动；均未伴随 C12 worker 被杀、OOM、日志截断或 identity 改变。依据
C12 aggressive-parallel acceptance，它们只作为调度观测，不使任一正在运行的 arm
失效。任何将来达到失败阈值的 arm 会独立归档、诊断和重跑，健康 worker 不受影响。

### Scheduler 6-way refill admission correction

审阅 aggressive-parallel addendum 后发现，scheduler 原先把升至 `8-way` 的严格
`MemAvailable >= 64 GiB` 与 CPU-load 条件误用于所有补槽。因此在普通 GREEN
（`MemAvailable >= 32 GiB`、PSI/iowait/swap activity 正常）而非 8-way GREEN 的
窗口，worker 完成后可能错误地不补足 `6-way`。调度器已最小更正为：普通 GREEN
目标为 6-way；只有同时满足严格内存与 CPU 条件时目标为 8-way。此修改只影响未来
从冻结 queue 启动哪个未运行 arm，不改 binary、Core、config、trace、registration、
输出目录或任何 simulator 行为。为使已运行的 supervisor 使用该修复，将仅终止该
scheduler parent 并重新启动它；其现有 replay child 与 `accel-sim.out` 不发送任何
signal，继续作为原有独占 owner 运行。

实际处置发生于 `2026-09-08T16:46Z`：精确终止的是旧 scheduler PID `1747210`；
`decode1:F8:Lseg10` replay child `1747213` 随即由 PID 1 接管，真实 simulator
`1748018` 保持运行并继续增加 CPU time。新 scheduler PID `1801183` 使用已验证的
修正脚本启动。没有向任何 `accel-sim.out` 发送 signal，未创建重复 output owner。

### Decode1 F2 parser-only reparse

Decode1 F2 于 `2026-09-08T17:05:03Z` 正常结束（exit `0`）。原始日志 SHA-256
为 `62acffd0a634a532db5fe5a1e8028ff2898aa2ee8a8753121c87205e8023a642`，完整包含
`740/740` kernel marker 与 telemetry record，object/PTE 守恒均通过。旧常驻
collector 再次将合法 `gpu_tot_ipc=119.4444` 判为整数错误，并将 GNU time 的
`9:07:12` 错读为 `12` 秒；这是与 Decode1 F0 相同的 parser-only 缺陷。

于 `2026-09-08T17:05:30Z` 使用当前修正解析器只重解析该不变 raw log。F2 的
terminal status 为 `PASS`，elapsed 为 `32832.0` 秒，所有冻结 identity/hash 和
simulation output 均未变化；没有重跑 simulator。由于 Decode1 F0 已 PASS，F2
已通过该 ROI 的正式 baseline gate。

### Decode1 F5 payload-versus-arm-budget validator correction

Decode1 F5 正常以 exit `0` 完成，原始日志 SHA-256 为
`673bce96c31510bd471baf9d9076217df48f8f5d23dc0f2b0ef7b2082a3a3c5c`，并具有完整
`740/740` marker/telemetry、object/PTE 守恒。旧 validator 同时有已知 IPC 整数解析
错误，并错误要求 telemetry 的 `vm_pwc_physical_f5_charged_bits` 等于整个 F5 fair-arm
预算 `64745`。实际 telemetry 正确报告 physical 120-entry PWC payload 为 `8370` bits；
矩阵独立地以 `vm_fair_arm_charged_bits=64745` 收取 PWC 加 exact-TLB remainder 的完整
F5 arm 成本。

validator 已改为核对 PWC payload `8370` 和既有 matrix arm-budget 字段。仅重解析同一
raw log 后 F5 为 `PASS`（elapsed `33548.0` 秒）；没有重跑 simulator，也没有改变
冻结 binary/config/trace/registration/Core 身份。

### Decode1 F7-Lseg10 parser-only reparse

Decode1 F7-Lseg10 于 `2026-09-08T17:48Z` 正常结束（exit `0`）。其 raw log
SHA-256 为 `da8055ea20b99d14267a992b59435af6f02d12da42a766f426082e7bc1d6b72a`，
含 `740/740` kernel marker 和 `740/740` telemetry record。旧常驻 collector 唯一
报告 `NONINTEGER:gpu_tot_ipc=119.9043`；该值是合法有限浮点，属于已记录的
parser-only 问题。

当前 parser 于同一 raw log 上复核，得到 `PASS`、cycles `34432059`、IPC
`119.9043`、peak RSS `569608` KiB，并通过对象/PTE 守恒及 F7-Lseg10 arm
invariants。没有执行 simulator 重跑，也没有改变任何冻结身份或其它 arm。

### Live-arm state snapshot serialization correction

Decode1 F9 于 `2026-09-09T03:56:21Z` 正常结束（exit `0`）；其 immutable
validation sidecar 已证明 `740/740` kernel marker、`740/740` telemetry、对象/PTE
守恒以及所有 frozen identity 均为 `PASS`，raw-log SHA-256 为
`b8628dae1c47866a0d739f07c921d89d64722f62e5eefbe0d45b4ffadd253d8c`。但 live
state 一度显示为 `NOT_STARTED`。根因是多个独立 launcher 虽以原子 rename 写 TSV，
却没有互斥整个“读取磁盘侧车 → 派生 22-arm 快照 → 替换 TSV”的区间；一个较早读取的
快照可以在 F9 validation 写入后覆盖较新的状态。

执行器现以 review-pack 内的 `C12_COLLECT.lock` 序列化完整 collect 快照，并在
`2026-09-09T03:58Z` 仅从既有不变的 sidecar/raw log 重建 `C12_LIVE_ARM_STATE.tsv`。
F9 正确恢复为 `SPECULATIVE_EARLY_EXECUTION_PENDING_BASELINE_GATE`，等待 Prefill
F0 的正式 baseline gate。该修复不读取或修改 simulator 输入，未向任何
`accel-sim.out` 发送 signal，也不要求重跑任何 arm；它只防止 live 审计表被旧快照
回退。为使持续 30-second monitor 装载该 non-semantic 修复，精确终止并重启的仅是
旧 `--monitor` Python PID `1166068`；它不拥有 simulator child。新的 monitor 在
`2026-09-09T04:11Z` 启动后，C12 真实 simulator 数仍为 `8`。

随后观察到 monitor 的 marker counter 使用全文件 `read_text()`，对多小时 raw log
产生不必要的约 `272 MiB` 瞬时 RSS。counter 已改为等价的流式逐行计数，并仅重启
该 monitor（PID `2695298` → `2697893`）；启动后 RSS 约 `28 MiB`。这是 host-audit
开销修复，不改变 marker 定义、任何 raw log、实验输入或 simulator execution。

### Prefill F0 parser-only reparse and baseline promotion

Prefill F0 于 `2026-09-09T04:54:06Z` 自然完成（exit `0`），raw-log SHA-256 为
`8f7bbc5a0e1263ca264c2b4f892d4bc4e02faf570cfd7df327b98a27ac326db7`。其完整原始
输出含 `692/692` kernel marker、`692/692` telemetry record、对象/PTE 守恒、冻结
Core/binary/config/trace/registration identity，且 `time -v` 记录零 swaps。旧常驻
P0 collector 仍装载 IPC integer-validator，因而把合法有限浮点
`gpu_tot_ipc=295.2881` 单独标为 `NONINTEGER`，暂记 `FAILED_DIAGNOSING`；这不是
simulator、资源或科学语义失败。

当前 parser 使用 `finite_float` 对 rate statistic 校验，在完全不变 raw log 上的
parser-only reparse 得到 `PASS`、cycles `62490238`、elapsed `77144.0` seconds，
errors 为空。没有启动或终止其它 simulator，未改任何 C5 input。至此 Prefill/Decode1
两个 F0 都 terminal PASS；collector 已将具备完整 terminal gate 的 Decode1 早跑 arms
晋升为正式 PASS，其余仍在运行的 Prefill arms 保持 pending，直至各自自然完成并验证。
旧 finalizer 已依据当时的 `FAILED_DIAGNOSING` 侧车退出；在 F0 reparse 后，仅重启该
non-simulator finalizer（新 PID `2855891`），其状态已恢复为
`WAITING_FOR_22_TERMINAL_ARMS`。未向任何 live worker 发送 signal。

### Prefill F2 parser-only reparse

Prefill F2 自然完成时 exit 为 `0`，raw-log SHA-256 为
`e4fc67d645c01f9588898f9cad6e021db4dde4619558edcac24d3575a881b914`，完整包含
`692/692` kernel marker、`692/692` telemetry record、对象/PTE 守恒以及不变的
frozen identity。它由装载旧 IPC integer-validator 的 P1 collector 初步标为
`FAILED_DIAGNOSING`，唯一错误是合法浮点 `gpu_tot_ipc=291.4973`。

当前 `finite_float` parser 对同一 raw log 重解析为 `PASS`（cycles 不变、elapsed
`84042.0` seconds、errors 为空）；未重跑、移动或改写 simulator 输出，未向其余
8-way batch 的任何 live worker 发送 signal。该 arm 现在可作为正式 Prefill F2
C5 结果参与后续同 ROI F0 对比。

### Prefill F5 and F7-Lseg10 parser-only reparses

Prefill F5 与 Prefill F7-Lseg10 都以 exit `0` 自然结束，分别保留完整的
`692/692` marker/telemetry、对象/PTE 守恒及冻结 identity。F5 的 raw-log SHA-256 是
`9881d28fd3570cd6333bfac0d07f3435b8f96fa68f39ce9235fe564cc3237b8a`；F7-Lseg10 的是
`6d29515bf7e393da19cab337122eb98836c998b2ec5bd4e1a54cfba599fa800d`。两者最初由旧
P1 collector 标记为 `FAILED_DIAGNOSING`：F5 同时报告合法浮点
`gpu_tot_ipc=291.8642` 为 noninteger，并使用旧的 F5 whole-arm-budget 几何检查；
F7-Lseg10 的唯一错误是合法浮点 `gpu_tot_ipc=291.1845`。

当前 parser 对完全不变的 F5 raw log 核对 physical-PWC payload `8370` bits 与独立的
fair-arm budget `64745` bits；对 F7-Lseg10 使用有限浮点 IPC 校验。两点均在
`2026-09-09T07:28Z` 后的 parser-only reparse 中得到 `PASS`，无 simulator 重放、无
Core/config/trace/registration/binary 修改，且没有向其余 8-way live workers 发送
signal。F5/F7-Lseg10 因而均可作为正式 Prefill C5 结果参与同 ROI F0 对比。
