# AWMA R20｜活跃world求解：资格、轻量Native与有界诊断

日期：2026-10-01。用户已批准本轮。状态：**AUTHORIZED_NOT_STARTED_BY_CHATGPT**。

## 0. 谁执行，执行到哪里

- Lane F / node109 / RTX4080：唯一Native生产者，复用原Lane F窗口。
- Lane E / 174-new、Lane G / 109：继续STOP，不另派任务。
- node164：输入、状态、raw和receipt的长期authority；109保留活跃副本。
- 不运行Accel-Sim；这里的MuJoCo物理仿真是被研究的GPU应用，不是微架构模拟器。

Handoff branch：`hrl/awma-r20-active-world-native-handoff-v1`
Execution branch：`hrl/awma-r20-active-world-native-109-v1`
Stage：`AWMA_R20_ACTIVE_WORLD_NATIVE_109_V1`
Scientific/design parent：`fb0da17a135f5f8485871abe1fbab66640fa8dcf`
Parent tree：`774cd049a4f3fa7160f5748a17511209a0523c4a`

入口以本目录为准；parent文献README/准备卡中的“所有lane STOP / 未授权”属于批准前快照，本文件仅将Lane F推进为本轮授权，不覆盖旧实验的STOP。

## 1. 阅读顺序

1. 本文件。
2. `docs/vm_tlb/literature_notes/awma/problem_cards/R20_ACTIVE_WORLD_SOLVER_PREPARATION.md`。
3. 本目录 `SOURCE_BINDINGS_AND_CONTRACT_NOTES.md`。
4. 本目录 `LANE_F_R20_ACTIVE_WORLD_NATIVE_109_GOAL.md`，连续执行到最终STOP。

不要求重新读完整Round01–20，也不重做R19、R17、R53或模拟器资格。

## 2. 单一问题

成熟MuJoCo Warp已经跳过完成world的算术、利用device条件图循环。在真实公开控制回放下，活动集合缩小时，剩余全world发射/索引/同步组织是否仍有可避免的完整物理step成本？

同数据附带记录约束容量与使用量，不新增容量实验或第二个工程方向。

## 3. 连续执行范围

源码/依赖与真实资产资格 → 实际conditional-graph运行 → 固定一个batch和回放窗口 → baseline重复性与状态恢复 → 活动集合/完整step观察 → 可行时一个在线活跃world诊断 → 正式配对计时 → 有稳定响应才解封后段验证窗口 → 发布并STOP。

普通路径、下载恢复、依赖和图捕获问题自行处理；不要每过一个工程阶段就等待用户。无需先证明5%理想headroom才允许有界原型；5%仅用于本轮是否值得后续投入的完整step筛选。

## 4. 不变的资源与发布规则

所有CUDA初始化、JIT、graph capture、物理step、计时与profiling必须持有：
`/data/c16/locks/c16_gpu_campaign.lock`

不抢占或kill其他campaign；CPU准备/分析可在锁外并行，GPU性能任务严格串行。不要busy-poll。

大数据直接发布node164，174-new只作已有通道，不本地stage大文件。不删除accepted数据，不重新建设data-plane。

最终发布同一个exact commit，push/fetch-back/remote SHA与tree验证，释放GPU锁、关闭本轮GPU进程并保持worktree clean。传输故障不重跑科学实验；使用既有HTTPS→HTTP/1.1→SSH→API有界fallback。
