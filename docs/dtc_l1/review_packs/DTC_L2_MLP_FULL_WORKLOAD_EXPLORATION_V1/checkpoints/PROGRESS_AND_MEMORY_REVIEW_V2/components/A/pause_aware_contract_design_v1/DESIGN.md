# Future-point-only pause-aware 观测合同草案

**仅设计，未实现；所有 guard 候选保持 PRODUCTION_HOLD。0 模型、0 注册、0 生产更改，禁止真实 SIGSTOP。** 暂停意图不能授权改写旧历史或既有 worker 的观测身份。

## 1. 身份与时钟

仅对**尚未消耗、启动前明确登记新版观测合同**的未来点启用；Core/FW/binary、输入范围、配置与模拟时钟均固定。登记新的 receiver、运行策略、guardian、strict 及资格源码 SHA、唯一 owner/token、eligible generation 和日志合同。已有 consumed/running 点没有资格，不能热补丁、重启或覆盖为新版结果；旧 strict/旧 PASS 保留原意。

保留真实宿主单调时钟 `W`；另派生 `A=W−P`，其中 `P` 仅累计经认证的暂停区间。两者及模拟 cycles 分别记录。**不能改写 producer 的 mono_ns、seq、completed 或制造暂停心跳。** UTC 用于展示；不跨 boot 拼接单调时钟。

## 2. 分开处理四种约束

| 约束 | 新合同所需行为 |
|---|---|
| receiver freshness：30s | 保留真实到达时间和 producer 时间、严格顺序/凭据/输入检查；对“记录年龄、相邻记录间隔、drain 无新记录”分别扣除认证暂停交集。只有已确认停住的 eligible generation 获得豁免。恢复后必须在限定的**活跃时间**内收到真实新记录，否则失败。 |
| resource sample cadence：10s，最大30s | supervisor 与 guardian 持续运行，以真实 `W` 采样资源；暂停只针对模型，不暂停采样器。采样缺口仍失败，不能因模型暂停而豁免整个宿主安全监测。 |
| semantic retirement：600s | 按 `A` 衡量真实 completed 增长间隔；暂停不算活跃停滞。phase 改变、guard 心跳、重复计数均不能重置该计时；未获认证的间隔照常累计。 |
| wall deadline：7,776,000s | 保持真实 `W` 的截止时间，暂停不延期；另报 active elapsed 和 paused elapsed。超时不得转成 NATURAL。 |

暂停资格须在首次真实 producer 身份/INIT、PID/maps、基线资源与 guardian ACK 完备后生效。外部停止、未知 job-control/tracer 停止、SIGTERM/SIGKILL、数据丢失不享有暂停豁免。

## 3. 可认证的 journal 与恢复

每次记录独立事件：`PAUSE_INTENT → PAUSE_CONFIRMED → RESUME_INTENT → RESUME_CONFIRMED`，带 request/point/UUID、PID/start、boot、owner PID/start、guard TID/start/token、源/策略 SHA、真实单调时间和原因。使用 pidfd、实际进程状态及恢复后的执行/真实记录证据确认；**发出信号不等于停住或恢复成功**。

有界过渡时间单列；不能在确认前任意回溯扩大豁免。每段资源样本引用 journal 前缀长度/SHA，最终冻结完整事件链、guard 故障与持有句柄状态。重复/乱序、未知恢复、无法闭合的暂停、guard 不健康或身份改变均 HOLD/失败，不能靠补日志验收。故障冻结不能假定释放 RSS，也不能盲目 CONT；不得通过清空历史来重建健康状态。

## 4. Strict 与科学身份

新版 strict 仍逐项验证同一输入群体、实际 options、cycles、全部 kernel/CTA/指令、资源上限、真实 PID 生命周期、自然退出与真实 NATURAL。另独立重算暂停区间、`W/A/P`、freshness 和600s间隔，并闭合 journal/资源/guard/退出证据；原合同未证明的数值正确性仍标 UNPROVEN。

将“经合同允许的宿主暂停”与“终止性 abort”分开记录；不能把含暂停的运行伪称旧合同 `no_prior_stop`。报告使用**新版观测合同身份**；旧 strict 不降门，也不把改造后的通过称为旧 PASS。缺少恢复/自然退出证据时保持未接受。

宿主 SIGSTOP 原则上不推进模拟 cycles，但这需要验证：排查宿主时钟/随机种子驱动路径，并用同输入对照检查总/逐 kernel cycles、群体和结果。验证一致后可声明架构、配置及模拟 cycles 可比；不能声明与旧运行拥有完全相同观测合同，更不能据此补齐旧失败。

## 5. 最小资格与登记门

- **CPU**：注入真实时钟与 journal；覆盖30s边界、跨600s、初始/恢复记录、迟到包、暂停中终止、PID复用、丢/乱事件、采样缺口、超时、guard故障及失败闭合。全程不合成 producer 成功证据。
- **真实工程资格**：先独立 strace dummy 验证 pidfd/暂停确认/恢复/故障闭合；不能替代模拟器资格。
- **未来点真实资格**：登记一个有足够观测窗口的冻结小输入，CH/DH 使用同一新合同，完成无暂停与受控暂停对照。至少一次真实暂停跨30s；跨600s可合并到同次暂停，或先由主协调者明确批准较小真实覆盖及相应限制。必须自然完成、独立 strict、周期一致和归档恢复核验通过。失败身份保留，重试另登记。

新合同/资格点须由主协调者报告并明确登记批准，保留所有既有 spent 和预算；不能 reset 取额度。**未解决旧 supervisor 的30s冲突前，不将其纳入任何 guardian 的暂停 eligible 集合。** 当前仅交付设计，未进行上述资格或实现。

依据：`../guarded_admission_v1/PAUSE_SUPERVISOR_COMPATIBILITY_BLOCKER.json`；本目录 `EVIDENCE.json` 提供精确路径、SHA、行号及当前科学源身份。
