# 最小语义进展可行性：SOURCE_ONLY / NOT_PRODUCTION_QUALIFIED

源码存在可用的完成指令与 CTA 完成事件，但冻结 AG6 的监控接口没有提供可绑定身份、时间、ROI 的实时语义进展序列。可以推荐未来单独授权一个 opt-in 遥测集成与端到端资格工作项；不能据本轮离线策略测试推荐立即启动新 AG6 cohort，不能宣称旧 AE_GEMM 会完成或可无限安全继续。

本审查完整读取 BB2 Goal 与 BB 的根因矩阵、报告、来源说明及 stdout 小型证明。Core 源码直接取已存在 Git 对象 `c8090115bd57512b1b23fca7d925301fa620c751`，不是任何 worktree 的 current tip；Framework/已执行 guard 取 `62323c40df0add726cae52a96ca946e589f00343`。精确 blob 与行号见 [SOURCE_PROGRESS_PROOF.json](SOURCE_PROGRESS_PROOF.json)。只读源码；没有编译、测试、fixture、模拟、模型二进制或 trace 内容读取，也未改任何生产文件。

## 1. 实际可用信号与语义

以下 Core 行号均属于 c8090115；Framework 与 guard 行号属于 62323c40。

| 候选量/事件 | 精确来源与实际语义 | 当前输出/实时限制 | 可接受用途 |
|---|---|---|---|
| 完成的模拟线程指令 | `src/gpgpu-sim/shader.cc:2352–2371`，`warp_inst_complete()` 以 `inst.active_count()` 增加 `gpu_sim_insn`，随后调用 `inst.completed()`；不是宿主 CPU 指令、不是发射数，也不是固定每 warp 加 32 | `gpu_tot_sim_insn + gpu_sim_insn` 在 `gpu-sim.cc:1832` 输出；`update_stats():1553–1571` 先累加总量再清当前量，裸 `gpu_sim_insn` 会重置 | 优先采用同一进程/ROI 的 coherent 累积和；在模拟线程安全点取样，不能外部无同步地读取两个量 |
| 完成 CTA | `shader.cc:5581–5588`，最后一个 CTA 线程退出使 `m_cta_status` 归零时增加 `ctas_completed` 和 `gpu_completed_cta`；`gpu-sim.h:632` 是递增入口 | `gpu_completed_cta` 在 `init():1512` 与 `update_stats():1571` 清零；`gpu-sim.cc:1227` 注册到 perf counters；`shader.cc:5593–5597` 有受 LIVENESS 条件控制的 Finished CTA 输出。它不是已发射 `gpu_tot_issued_cta` | 未来另加不重置的进程累积完成 CTA，或严格带 epoch 的无损转换；当前不能把裸字段当作跨 kernel 单调指标 |
| kernel 结束事件 | `shader.cc:5613–5624`，无更多 CTA 且 kernel 无 running CTA 时进入 `set_kernel_done()`；`gpu-sim.cc:1034–1050` 记录 end_cycle、将 UID 放入队列；`:1024–1031` 的 `finished_kernel()` 弹出队列 | 同一个 `set_kernel_done()` 也被 `stop_all_running_kernels():1053–1059` 调用。队列长度并非单调量，队列事件也不天然证明自然完成 | 需要自然完成原因与取消/限制/异常原因区分，累计唯一自然完成 UID；不能把取消清理变为 COMPLETE |
| 周期 liveness 文本 | `gpu-sim.cc:2562–2590` 条件路径输出 `gpu_tot_sim_insn + gpu_sim_insn` 并 flush stdout | 受模拟周期采样、墙钟频率与 `DTRACE(LIVENESS)` 控制；另一周期路径 `:2874–2888` 只更新计时而无同类指令打印。文本没有 root PID/start_ticks、单调时钟或 ROI 合同；阻塞时不保证心跳 | 仅诊断候选，不能直接认定已经存在合格实时协议 |
| kernel 边界统计 | Framework `gpu-simulator/accel-sim.cc:122–147` cleanup 调用 `print_stats()`/`print_counters()`；`:150–171` simulate 在 active 且未 finished 时持续循环 | 大 kernel 内部不保证输出；`:72–85` 同样处理限额命中/非 active。统计输出及进程退出均需检查结束原因 | 可用于结果闭合，不能替代运行中 watchdog |

指令完成增加足以证明本合同所定义的已完成模拟工作增加；它不证明 AE/AD 数值正确、结果有效或性能收益。CTA/kernel 完成事件更粗，在长 kernel 内可能长时间不变。模拟周期推进、CPU ticks、log 大小、trace 消费量、CTA 坐标/发射事件均不是上述完成语义。

## 2. 冻结监控为什么不能直接接入 B

冻结 `prepared_ag6/dispatch_ag6_v2.py:381–389` 获取资源与 authority、root `majflt`，调用 `runtime.observe()`，把 snapshot/decision/own 写入资源日志；没有读取模拟完成指令/CTA/kernel。`resources_v2.py:107–122` 只是 host/cgroup 资源策略组合。既有 stdout 的封存证明中完成指令、CTA/kernel/cycle 序列为 UNAVAILABLE；本轮不再扫描原始 stdout 或大 trace。

BB 的 q1–q3 root CPU 增长 6147 ticks 证明仍有 CPU 活动，但不能排除忙循环。28 行历史回放中的 `semantic_progress=UNAVAILABLE` 是不可补造的证据缺口，结论只能是 `UNDETERMINED_PROGRESS_NO_PRODUCTION_PROMOTION`。任何合成指令/CTA 增长都必须另标 `DECLARED_SYNTHETIC`。

## 3. 最小前瞻接口合同（本轮未实现）

建议一个由模拟线程安全点产生的有界小 record；外部 monitor 只读取已注册的独占通道，不读 `/proc/PID/mem`，不注入调试器。最小字段：

- schema/version、递增 sequence、producer monotonic timestamp；consumer 同时保留读取 monotonic timestamp，检测延迟、空洞、截断与时钟倒退。
- 同一 root PID/start_ticks、启动 nonce/image generation、精确 Core/Framework/config/input/ROI 身份摘要；由当前 ownership/loaded-image 审计另行验证，不只信任 payload 自报 PID。
- coherently sampled `completed_active_lane_instructions_total`（上述累积和）、进程累积 completed CTA；可选唯一自然完成 kernel 计数与 UID/stream；simulated cycle 仅作诊断。
- phase/epoch 与明确的 run-end reason：NATURAL、ABORT、LIMIT、ERROR 分开。取消/限额、外部 STOP、记录缺口不得晋升为自然结束。

读取通道必须有界且不阻塞模拟线程，固定大小或有界追加、明确 flush/原子发布语义；满/失败、序列丢失或 monitor 异常均触发保守 insufficient evidence 的闭合动作。实际发布频率、大小与观测开销必须在未来资格工作中测量，本轮不承诺开销数字。

持续无完成量不必然异常：解析/初始化、内存操作长等待、kernel 边界及无 active-lane 指令等可能合法。未来应按源代码可证明的 phase 定义完成指标、最大无退休期限与诊断责任。phase 自报不能无限续租；只有预先科学批准的有界 phase 合同允许 grace，必须受全局 deadline 与实际安全/公平性保护约束。若该阶段的上界无法证明，状态是 INSUFFICIENT_EVIDENCE 并按预授权 fallback 闭合，不能擅自发明 watchdog 时长或以 cycle/CPU 活动解除 STOP。

同 PID/start_ticks/generation/ROI 中断、重置计数无合法 epoch、reversed/stale timestamp、计数回退、缺失度量、scope 不明、consumer gap 或自然闭合证据不全均不得认定合格进展。恢复只能从新的完整且连续证据重建窗口；已经 STOP 的运行不能复活。

## 4. mapping 重哈希减负候选（SOURCE_ONLY，未实施）

冻结 `mapping_roles.py:176–193` 每次完整 snapshot 对每个已映射文件调用 `verify_file()`，后者 `:100–106` 经 `file_record():54–79` 全文件 SHA256；`guarded_process.py:85–97,165–176` 在 mapping syscall 前后等事件 capture。BB 记录 8369 captures、coordinator rchar 增 100,334,069,583B，read_bytes=0。这是实际观察者读取负担；它不是已证明的设备冷读量或 STOP 唯一根因。

可单独设计一次完整内容验证加每事件身份/映射验证的缓存：key 绑定 boot/mount namespace、进程 start_ticks/image generation、manifest hash、canonical path、device/inode/size/mode/owner/ctime/mtime/link 与内容 hash；每次仍完整解析 stopped maps 并验证已注册路径、device/inode、offset/权限、loaded-image 与精确 ownership。exec/fork generation、映射新增/移除/替换、mprotect/权限改变、文件身份变化、缓存失效与闭合时触发重新内容验证；保留每次 capture、事件与缓存命中/验证依据的可审计记录。

**生产前提是可证明文件内容在缓存有效期内不可修改。** 只看 inode/size/mtime 或持有只读 fd 都不提供该保证，尤其相同账户/root 可写文件；inotify 事件也不是完整无竞态的内容证明。如果不能建立冻结内容对象及其 enforceable immutability、正确加载对象绑定和 mutation/overflow fallback，必须保持原逐次哈希。该方案没有本轮实现或测试，实际节省量及安全等价性未证明；不得删减 PID/start_ticks、generation、loaded-image 或前后 stopped snapshot 检查来换速度。

## 5. 真实资格缺口及最小未来授权

本轮纯策略 CPU 测试即使通过，也只验证离线状态语义。生产缺口至少包括：真实进展生产与完整身份桥接、跨统计重置与并发 kernel 的计数语义、合法无退休阶段有界合同、freshness/monitor failure fallback、替代 PSI STOP 的实际 I/O 影响/公平性规则及可接受 deadline、通道与保护器整合、自然/异常结束因果闭合、实际开销和一次端到端资格证据。模拟进展不证明共享存储对其他项目没有危害；此项不能靠完成指令增长消除。

最小下一步授权应先明确独立 opt-in 源码集成/构建/受控资格的范围、资源合同与量化参数，再单独决定是否包含一次有界端到端运行及其预算/UUID。任何运行前必须重新满足 unchanged paired host+cgroup R2、实际输出挂载严格 >5GiB 且有预计写入余量、OOM/memory/swap/identity/authority/deadline 等保护，BA `/root` 仍是未来 fullsim 唯一 dispatcher。批准新 runtime STOP 语义与任何新的 AG6 cohort 都是用户科学裁决；不能用本包代授。旧 AG6 1/4 consumed、0 accepted、3 UUID SEALED，BA 0/32，F=null，均不变。
