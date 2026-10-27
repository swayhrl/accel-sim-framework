# DTC-MAIN 进度与内存策略补充审阅 V2

本包是 commit5178408 的独立补充，不替换其冻结快照、原始结果或历史合同。主Goal继续执行，尚未完成全35扫描、有效组合和正式CH匹配。本包没有启动、暂停、重启或终止任何模型，也没有部署下面的guard候选。

结果固定于UTC 2026-10-27T13:50:23.775316+00:00：350格中accepted 172（新166+合法引用6）、运行76、pending 102。原始reason旁路扫描172闭合点，identity/evidence/sum mismatch全部0，字段缺失保持None。单独采样的实际进程状态见PROCESS_RESOURCE_STATUS.json，时间2026-10-27T21:54:09.339640+08:00；准入观测见RESOURCE_ADMISSION_STATUS.json，时间2026-10-27T21:54:12.170851+08:00。不将不同时刻强行相加。

- [新增ATAX/BICG/3DCONV周期与计数器证据](NEW_FOCUS_EVIDENCE.md)、[逐程序/配置完整结构化表](results/dashboard/report.json)、[交互看板](results/dashboard/dashboard.html)。部分样本不是最终统一配置结论。
- 当前准入观测：实际own live 75，宿主available 109.528GiB；cgroup current/max 184.418/256GiB，clean inactive file credit 27.780GiB；未来增长预留79.087GiB，安全增长预算80.399GiB。后两者是预测账本，不是已占RSS。CPU额度仍384，模型数量由动态资源准入决定。
- [A候选报告](components/A/guarded_admission_v1/REPORT.md)：66项CPU组件资格；[B说明](components/B/memory_guard_v1/README.txt)：52项dummy CPU资格。源码、资格脚本、真实只读shadow及SHA随包，全部**PRODUCTION_HOLD**；不能把组件测试称为旧supervisor真实暂停资格。
- [兼容性阻碍的精确源码/SHA/行号](components/A/guarded_admission_v1/PAUSE_SUPERVISOR_COMPATIBILITY_BLOCKER.json)：receiver drain在生产者年龄>30秒后失败，native supervisor据此TERM/KILL；同时暂停supervisor也不满足真实资源采样cadence。现有running点均不具备长暂停资格，不能静默更改其合同、伪造心跳或降低旧strict。
- [仅未来点的pause-aware合同设计](components/A/pause_aware_contract_design_v1/DESIGN.md)：只读草案、未实现、未注册、未跑真实资格。分别保留真实wall、认证pause、active时间；资源采样持续，600秒semantic间隔扣认证pause，90day wall不延期。模拟cycles可比性仍须真实对照资格，不能冒称旧合同身份。
- [历史内存风险核算](components/E/memory_risk_v1/MEMORY_RISK_REVIEW.md)：Lava存在同Core完整运行约67.3GiB实测峰值，81.18GiB预测并非任意16GiB一刀切。短时间RSS平稳不能证明后续不会增长。暂停保留RSS，只能抑制未来增长。

当前更紧padding的逐输入强身份核算仍在进行，尚未部署；未知/foreign/未观测claim不因看到空闲内存而折扣。不得把本草案作为实际调度策略或授权回执。

审阅重点：新增partial结果是否算对；raw reason的重试语义与None是否正确；当前headroom/RSS/增长预算是否混淆；旧worker为何不能被直接暂停；未来观测合同草案的完整性。原35普通输入/7未决、Core9eedb313/FW02775fd7/binary02a28936、DRAM850MHz、10MiB L2容量/映射/DTC固定，v0.23母稿保持。只读工程分析不更改任何科学点状态。
