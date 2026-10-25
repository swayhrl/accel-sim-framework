# DTC-MAIN repair validation operations handoff

冻结时间（UTC）：2026-10-25T16:02:29.718631+00:00。本包包含 212 个源工具/结构化元数据文件，共 3358675 bytes；逐文件来源、大小与SHA见 `HANDOFF_COPY_MANIFEST.json`。本包是操作与证据交接，不是全部模拟通过的声明。

本轮修复沿三条线推进：

1. Core 修复零目的寄存器原子指令的真实返回 completion，并在本 kernel 的 DTC 侧车排空前延后完成发布，保留 IO/OO 的服务顺序、宽度及 Ref0 retained-cacheline 语义。
2. Framework 在同一 simulation thread 的真实 CTA/文本及 tracez 解析边界提供有界 cooperative heartbeat，仍用最后已退休 instruction 值，保留原DTC_AG7身份/序列/phase/terminal协议、1M record上限、10秒节流、30秒freshness及600秒semantic-retirement规则。没有外部假心跳。
3. Observer 修复 `/proc` 自然退出竞态：以实际身份、进程退出和原始输出证据完成新 generation 的收尾，不把权限/身份故障当作正常结束，不补造旧回执。

既有 RAM 修复另行保留来源：每任务初始工作集预留4 GiB，随真实RSS增长；16 GiB运行硬上限不变。4 GiB不是内存kill阈值，资源充足仍是实际派发前提。

源身份冻结为 Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`、Core `9eedb3131937748f0492fa83aad37d3691118d70`；二进制和库仅以构建收据/SHA引用，不进入本包。实际启用还须满足源发布readback、R13与runner资格收据；最终状态以对应request/UUID及真实进程与结果证据为准。

新增独立验证预算为 **23 = 13 个修复点 + 10 个组件 sentinel**。sentinel覆盖VecAdd及mixed engineering input的 LEGACY/BASE/IO/OO/SECTOR 五配置，仅作正确性验证；不得混入普通完整workload的性能集合。新请求使用新UUID，旧spent UUID、原source身份和失败账本均保留，不reset或refund。

原72套输入×4配置的288点矩阵保持原历史source身份。新Core可影响atomic completion/排空行为，因此这23点不能拿来静默替换原288点中的失败或缺失项，也不能把repair与旧source结果拼成统一科学性能结论。原accepted、negative、HOLD证据均保留；fraction/trim仍排除。旧AG8R1不重启，历史账本不改。最后确认的英文论文母版仍为 **v0.23**，本包不晋升论文版本。

原CFD-DM（`97c43b01-9628-490f-839e-4a2a8126122e`）与b+tree-DM（`f6c79f5f-6b0e-42d7-a5be-c3013fa7aaba`）收尾竞态缺少原NATIVE_EXIT/DONE/科学资格闭合。它们保持UNACCEPTED、accepted_cycles=null、charged=1、SOURCE_KEEP。独立forensic仅允许R13对后续派发跳过旧缺失回执的等待；没有补造p.wait返回码、NATURAL、DONE、EXIT或PASS，原矩阵仍不完整。

后台并行分两组：原矩阵最多40路，新repair验证最多23路（13修复+10 sentinel），后者不计入原40路上限。上限不等于实际运行数量；实际运行服从真实RAM、写入预留和资源资格。174-new保留至少5 GiB本地安全余量，并纳入已知未完成写入；结果通过真164归档和独立native恢复核验，不能仅凭文件存在宣称归档完成。

CPU资格和构建通过不等于科学输入已跑通。全部新验证点尚未完成严格whole-input、自然结束、source/runtime/人口/侧车排空、真164归档及native恢复核验之前，状态保持验证进行中，不声称“修复已全部跑通”。失败、负结果与任何新的工程异常均按原证据保留，不自动反复重跑。

包内保留候选/模板文件时，其文件名和原status不改；它们属于准备来源，不能冒充已注册或已执行的最终spec。执行应使用最终资格与manifest明确绑定的源文件。

本包不包含raw、日志payload、二进制、build树、trace或dataset。已归档原始证据通过各报告的原路径和内容SHA引用。`source_tools/`保留源工具；`qualification_build/`保留构建与CPU资格；`repair_metadata/`保留scope/spec/cap/manifest；`operations/`保留observer与旧attempt forensic；`diagnosis/`保留逐点诊断；`existing_RAM_fix/`保留已有RAM修复来源。
