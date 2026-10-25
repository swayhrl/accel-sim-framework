# 当前全部失败点诊断（2026-10-25 22:40:27，北京时间快照）

本轮从7个失败开始，调查期间新增4个，快照共11个失败配置点、7套完整输入，逐点均已覆盖。后台模拟继续，因此此报告不声称覆盖快照之后尚未发生的失败。17套输入HOLD和25个fraction/trim排除项不混作失败模拟。

| 失败配置 | 点数 | 直接触发与诊断 | 证据边界 |
|---|---:|---|---|
| BFS DM、DH | 2 | 首kernel死锁；零目标寄存器全局ATOMG缺少M4完成通知，可耗尽128槽OO-PIB | 源码+真实组件CPU证实缺陷；历史dump未打印逐条PIB，确切满槽状态为高置信归因 |
| hybridsort DM、DH | 2 | 首kernel统计时真实OO-PIB仍非空；2048条零目标RED与同一完成缺口吻合 | 全首kernel SHA审计；历史剩余UID/数目未捕获；64SM绑定不等于实测CTA映射 |
| histo DM | 1 | 首kernel统计OO-PIB非空；128条零目标RED.MIN/MAX与同一缺口吻合 | 首kernel全读、SHA和指令数吻合；残留条目数不是实测 |
| myocyte CH、DM | 2 | 旧producer/receiver上限恰8192条，producer永久停发，约30.07秒后被freshness守护终止 | 连续8192成功send和原header纯CPU复现，直接因果已证实 |
| scalarProd DH | 1 | 只有6条遥测，首kernel批量trace/CTA初始化期间不刷新，约30.43秒超时 | 初始化不可观测窗口强支持；CPU解析、164/FUSE、pipe和调度贡献无法从旧记录唯一分解 |
| lavamd CM、CH | 2 | 同样6条遥测，批量加载CTA0..56/0..55，约30.58/30.68秒后被freshness守护终止 | 逐点raw/seq/send/资源均核对；同类观测窗口强支持，底层耗时分解未定 |
| vectorAdd DH | 1 | 旧聚合预留门槛仅差28.09375MiB，外层守护主动SIGTERM | 本点峰值RSS0.5586GiB，125次采样无新增OOM/swap/内存PSI，原BA无STOP；并非本点OOM |

最重要的源码发现：`writeback_complete` 以目标寄存器写回为主要完成条件，无返回值global RED/ATOMG返回false；两处返回路径只在true时关闭M4外部依赖。dispatch的retire只管PAPER_BASE，stores出口也不会处理已经解码为LOAD_OP的原子。真实源码函数和OO header的CPU fixture重现了零目标指令不能释放条目，128槽后拒绝下一准入；有返回值原子和fence控制可完成。少量泄漏可推进到收尾断言，大量集中泄漏可形成死锁。但缺少历史逐UID状态，不能把精确残留数量或每SM分配当作已观察事实，亦不能排除途中瞬时容量stall。

修复优先级：先补齐独立于目标寄存器、按UID聚合全部源响应、且仅执行一次的atomic completion，再补核心/kernel sidecar drain；不能直接删断言、伪造trace目标寄存器，或在dispatch提前宣布原子完成。遥测侧应在同步批量解析内部提供受限真实进度，不伪造已退休指令，也不直接关掉新鲜度/语义停滞守护。1M容量与新RAM规则已用于后续未花费点，不代表历史失败重跑成功。

本轮只做原始证据/源码阅读、受限trace新读及小型CPU逻辑复现：没有启动或重跑科学模拟，没有修改活动Core/Framework、旧分类、INTENT/DONE或历史账本。失败点没有accepted cycles，不能填零收益、负收益或计算缺臂四配置R。英文v0.23母版未改。

逐点身份、完整SHA、报告路径、确定性级别与修复建议见ALL_FAILURES_DIAGNOSIS_V1.json；分专题详见bfs、hybridsort、histo、telemetry（V3）、vectoradd目录。所有原始raw/progress/resources及真164归档/174-new恢复保持SOURCE_KEEP。
