# 已接受CFD：增量事实定位

新binary OFF **79,093**、ON **79,742**，ON多 **649周期（+0.82055%）**；两端143,129,372条完整指令、5kernel、64slice。下表来自两份已完成原生raw的准确UID/名称/原生时间字段，并与恢复接收回执核对。未读取SAD/Vector活动raw，未重复大文件SHA、native或应用。

| UID | Kernel | OFF周期 | ON周期 | ON−OFF |
|---|---|---:|---:|---:|
| 1 | initialize_variables | 7,056 | 7,056 | 0 |
| 2 | initialize_variables | 7,055 | 7,055 | 0 |
| 3 | initialize_variables | 7,031 | 7,031 | 0 |
| 4 | compute_step_factor | 9,998 | 10,003 | +5 |
| 5 | compute_flux | 47,953 | 48,597 | +644 |
| 最终残量 | 最终累计−命名kernel之和 | 0 | 0 | 0 |

649周期精确闭合；其中644发生在kernel5，5发生在kernel4。这仅定位耗时差异，不能唯一归因于某个机制。

ON最终标签是 **UNKNOWN**，唯一缺口为全部64slice的 **MissQ拒绝计数覆盖不完整**：原生报告peak1/8192、denial-checks0，但若干直接 `size<capacity` 分支不经过统一拒绝计数，E明确置 `counter_covered=false`。不能把报告0变成“所有路径没有拒绝”。其余已覆盖容量均未触发资格阈值；最大已覆盖峰值/保守上界为1570/65536=2.39563%。Tag的timed-clean、timed-dirty、host-prefill成功替换均为0，64slice替换覆盖已确认；Tag峰值采用resident identity保守上界。

汇总事实：OFF/ON lower-read packets为212,308/206,448；lower-WB bytes为3,983,744/0；logical copy-read/write各31,123/0；物理bank grants为1,638,275/0。ON的0物理grant来自DATA_FREE诊断，非正常硬件P1吞吐结果。容量与服务同时改变，不能把流量变化或重叠WAIT相加解释为649周期因果。

完整mangled名称、累计cycles/instructions、原raw准确行号、接收回执SHA、逐资源峰值/覆盖及Tag替换见 `CFD_INCREMENTAL_D_FACTS.json`。保留原FAILED parser证据及费用；当前有效端点指向独立parser恢复回执。原MAIN五组GM0.9977331348587999不变，本轮仅为单独容量/数据服务诊断事实，供D继续机理分析。
