# EP-L2 Source5 阻塞路径代码审查

2026-11-11，EP-L2 Main。审查对象为已冻结 Source5 Core `3d3887bb2e8d5073d13b0792ff9116834e89fe2f`、六点实际采用的 host 执行链，以及 Native 事务与后台收尾入口。只读审查；没有修改固定 Source/Spec、登记预算或启动模型。六点已 `CLOSED_ACCEPTED` 的事实只证明这六个固定输入与配置完成，不证明任意新配置不会阻塞。

## 结论与需处理项

### P1：运行监视器可被共享锁无期限挂住，进而反压模型 stdout

`runtime/host_stencil_ext1_bound_v1/ep_perf_common_v2.py:89-95` 的 `locked()` 默认执行阻塞式 `flock(LOCK_EX)`，没有超时或继续服务模型输出的机制。`ep_perf_native_wv_modes_draft.py:301-349` 在读取 `Popen(..., stdout=PIPE)` 的同一个循环中，每约 2 秒调用 `update_claim()`；其 `:249-260` 先等待全局 `ADMISSION.lock`，在状态变化或 4 MiB 写入承诺变化时又嵌套等待 Native `REGISTRY_UPDATE.lock`（`ep_perf_common_v2.py:116-159`）。若任一锁的持有者长时间不返回，监视器停止读取 pipe，模型可能因 pipe 写满而停住；`:346-347` 的 wall limit 也只有循环继续时才能生效。启动前 `:238-240` 的资源门也可无限等待锁。Linux 进程退出会释放 `flock`，但活着且卡在 I/O 或别的等待中的持有者不会。

这是一条从代码可推出的条件性阻塞链，**不是六点曾发生该故障的证据**。修正建议：为启动前锁等待设有界失败；运行中用非阻塞尝试与有界重试，持续排空 stdout 并检查硬截止；写入承诺更新若暂不可发布，保持保守的旧承诺并暂停新的准入，超过明确时限则停止本次运行并保留一次消费记录。同步检查全部 family 副本及锁顺序，不直接改已冻结回执。

### P2：扩展模式的 L2 flush 路径不具备通用收尾资格

`src/gpgpu-sim/ep-l2-tvd-cache.inc:447-453` 的 `tvd_epoch_cleanup()` 在扩展模式下调用 `tvd_reclaim_one((unsigned)-1, now)`；`:198-201` 将其导向 `optional_bank_reclaim()`，而该函数 `:38-39` 把 `payload_id % 4 != bank` 当作过滤条件。当 `bank=(unsigned)-1` 时，任何 0..3 银行都不可能被选中，循环立即结束；若 Base 中仍有 CLEAN 或 WB_COMPLETE 项，随后 `assert(m_tvd->occupied()==0)` 失败。即使补上全银行选择，该回收器仍按两周期选择器工作，首次调用会返回 `false`，固定 `now` 的同步 `while` 不能完成排空。模式 2 曾填充 Ext 时，`:449-450` 还会先显式抛出“runtime cleanup profile is not qualified”。`gpu-cache.h:3104-3105` 的 `flush()/invalidate()` 均调用此路径；`gpu-sim.cc:2316-2333` 在 `-gpgpu_flush_l2_cache=1` 时可触发。配置校验 `gpu-cache.h:3383-3389` 没有排除该组合。

六份正式 `FROZEN_SPEC.json` 的 `-gpgpu_flush_l2_cache` 均为 `0`，因此这**不是当前六点的运行中阻塞**。但新 Source/新工作负载若打开 flush，会得到非预期终止或已明确不支持的运行路径。下一工程版应在配置期明确拒绝扩展模式加 flush，或实现并验证可计价、保留写回与 lease 的 Base/Ext 排空；在此之前不得把该组合列入可启动配置。不能把 `-1` 简单改为某一银行并声称完整支持模式 2。

### 性能阻塞：当前已计价，但仍缺 Ext 专属等待分解

`ep-l2-tvd-cache.inc:243-273` 对 Base miss 先查 Base，再经下一次共享查询周期查 Ext；`:65-78` 的 Base selector 还需两周期。这些是模型中有意加入的结构性等待。Stencil 同 Source5 的 EXT0/1/2 应用周期为 `4,768,893 / 4,787,045 / 4,786,427`，迁移包 `+18,152`、CLEAN 包 `−618`；GEMM 迁移包为 `−533`，不能把 Stencil 方向推广到所有输入。当前 `unexported_ext_waits=UNKNOWN`，所以不能断言额外查询独占导致 Stencil 回退；下一工程门应导出负/正 Ext probe、等待及端口竞争的可核分项，避免把宽泛 `block_payload` 事件当作独占周期。

## 已核的进展保证及边界

- 目录 `begin_read()`、`response_commit()`、`cancel_read()` 均更新 revision（`ep-l2-tvd-directory.h:288-317`）；写回 `lower_accept()`/`set_done()` 也更新 revision（`:401-414`）。这支持 `optional_bank_reclaim()` 在等待读 lease 或写回终态改变后重新选行。当前代码和既有 CPU 资格没有显示这一条会永久卡在旧快照。
- Ext DROP 后把旧 ticket 置为哨兵（`ep-l2-tvd-cache.inc:290-306`）；历史曾发生“重读已死 Ext 行占住唯一 indexed view”的活锁，修复在 Core `6fbf8176...`，已包含在 Source5。固定 CPU 证据覆盖非 RR atomic、full write、missing sector、pinned RR fallback 与同银行回收/写回完成；本审查复用该证据，没有重跑历史实验。
- 执行监视器自身有 wall、RSS、结果大小、物理 ENOSPC 和显式 ABORT 检查（`ep_perf_native_wv_modes_draft.py:321-359`），但这些检查不能解除上述阻塞式锁等待。后台验收/发布脚本分别有 48/52 小时上界；新运行仍需每次重新确认身份、锁与资源。

## 审查范围与下一动作

本轮逐段阅读了扩展查询/selector/spill/reclaim、目录 lease 和 revision、FT 替换/银行队列、L2 前后端、host stdout/限额/锁、Native transaction、归档锁与后台终态。没有运行新模拟或大 Trace，也没有修改任何已接受点的 Source。审查没有发现六个冻结点仍在等待结果；其父请求已收为 `CLOSED_COMPLETED`。

下一件具体工程工作：在**新版本**中先给锁等待加有界、可排空 pipe 的处理，并给扩展模式加 flush 配置门或完整排空实现；用最小 CPU 用例验证“锁被占用时监视器仍排空输出并按时停止”及“mode1 Base 非空时 flush 配置被拒绝/正确排空”。之后再做 Ext 负查询短路的可行性与成本门。任何新完整应用点仍需独立科学授权和新 Source/Spec 绑定。
