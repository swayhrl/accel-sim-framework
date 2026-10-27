# DTC-MAIN 当前完成情况：ChatGPT审阅入口

**执行中，非最终性能结论。** 主实验快照：北京时间2026-10-27 20:22:50；资源补充观察：2026-10-27T20:29:13.499240+08:00。所有快照逐文件原子读并记录SHA，不声称全系统同一事务。后台模拟和唯一owner继续运行。

| 第一轮350格 | 数量 |
|---|---:|
| 新strict/164归档/native restore PASS | 139 |
| 精确匹配P0引用 | 6 |
| 合计accepted | 145 /350 (41.43%) |
| 真实PID核实RUNNING | 80 |
| 尚未启动PENDING | 125 |
| 失败/工程异常 | 0 |

新请求技术额度344，主快照已消耗219、剩余125；另6引用不消耗新身份。这是第一轮精确额度，不是全阶段总次数上限。后续合理扩边、组合、匹配CH仍需自然推进。当前matrix revision=0。历史DTC活进程另计3。

入口顺序：

1. [ChatGPT审阅提示与问题](CHATGPT_REVIEW_PROMPT.md)
2. [35输入×10格完整cycles/状态表](WORKLOAD_MATRIX.md)
3. [部分参数收益与全部非中性案例](PERFORMANCE_PARTIAL.md)
4. [并行度、内存增长预算与大任务待审建议](RESOURCE_AND_PARALLELISM.md)
5. [可下载后本地打开的交互看板](dashboard/dashboard.html)、[机器JSON及逐源SHA](dashboard/report.json)
6. [真实模型PID/资源观察](PROCESS_RESOURCE_STATUS.json)、[最新准入账本](RESOURCE_ADMISSION_STATUS.json)、[历史身份/源保持证明](CAPTURE_RECEIPT.json)

当前八种profile共同完成只有6/35，约占全35预计指令量0.47644%，名单为gaussian, histogram, transpose, heartwall, BlackScholes, lud。不能据短作业先完成的样本宣布全套无效或选赢家。P0当前CH/DH仅17/35配对，GM=0.996112634，正/等/负=12/0/5；仍是部分覆盖。非P0 CH缺失、相对收益改善及正式候选资格尚未完成。

本次新扫描全部145个已accepted闭合日志，压缩/原文SHA、INTENT/DONE/EXIT/strict/归档链和kernel/stream覆盖核对，错误0；全部145项与看板精确匹配，正理由字段50项，其和全部与aggregate闭合，未打印95项仍None。完整旁路证据在closed_raw_reasons.json，未改冻结proof或原始raw。计数是重复拒绝尝试，不是唯一请求、等待时间或全局周期比例。gpu_stall_dramfull实为ICNT入口阻塞。既有三负例基线压力表见[此前已验证的CH/DH对照](../../agents/D/raw_reason_v1/BASELINE_STRIDED3_COMPARISON.md)。

科学边界：35普通冻结输入；7未决不晋升；不恢复72扫描、不混入派生b+tree/hotspot和fraction/trim。Core9eedb3131937748f0492fa83aad37d3691118d70，Framework02775fd795cde5aae1480d81cee6eb481d0a08f4，binary02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d。DRAM850MHz，L2容量10MiB/映射/DTC架构固定，仅entries/merge/miss queue/FRFCFS；FRFCFS共享credits=F+191的耦合如实披露。L1跨设计容量/Tag/服务/面积并未配平。

已应用：同一PID1498278 owner，动态88%增长准入、384容量、4pre-exec、一致化资源口径、生命周期保护、事务journal。V2补充搜索规则先在source commit927c8bd0公开，再于20:11接入；84CPU资格，安装对部分快照输出0新proposal，无新增grant。1%仅material标签，完整35持续正改善扩边；最佳统一配置包括不足1%时必须CH35匹配；最终outer journal guard保持。见[版本规则](../../SUPPLEMENTARY_SEARCH_V2_REVIEW.md)和[实际激活ACK](SUPPLEMENTARY_SEARCH_V2_ACTIVATION_ACK.json)。原始V1工具、plan及历史UUID/预算保持。

尚未完成：全35×全部初始配置终结、有效扩边与组合、正式统一候选CH匹配、最终套件GM与潜力配置。最高资源不能冒充最佳性能或未探索设计的上界。自然trace完成不等于已证明整应用数值正确性；英文v0.23母稿不变。未自动重试消耗过的点。

原生运行根：/root/data/dtc_l2_mlp_exploration_20261027_v1。结果归档：/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1。原始日志/trace/binary不入Git，结构化证据及其SHA在包内，原始体核验需要相应164资产。此审阅包自身还需检查ARCHIVE_RECEIPT.json的true164 CRC/SHA/native restore证明。
