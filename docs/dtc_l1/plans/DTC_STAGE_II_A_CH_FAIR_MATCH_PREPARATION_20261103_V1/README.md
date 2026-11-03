# DTC-L1 Stage II-A：CH公平匹配与逐kernel分析准备

**本包状态：规划与CPU-only资格准备完成；科学执行未授权。70候选未注册、0 grant、0模型启动。** 唯一论文母稿仍为用户确认的英文LaTeX v0.23，本轮不访问或修改母稿，不使用GitHub旧稿替代。

协调者DTC-MAIN与三个实际独立Agent完成本包。唯一推荐入口为本页；候选/资源为Agent A，逐kernel证据为Agent B，独立复核为Agent C。

## 先看结论

- 第一阶段以 `361fa6fa0700825bb9cda43e25b9fd1f60e0b262` 冻结：原始350格=325次新测量PASS＋6个合法P0引用＋18 archived negative＋1 engineering negative，即331 accepted。独立命名视图336是另一视图，不覆盖原始350。
- 原登记360启动身份均已终结。本轮不重启Goal/旧身份，不修改原矩阵、预算、owner或controller，不捕获trace，不运行109 GPU任务。
- 35个冻结输入每个准备CH-F128/F256，共70规划候选：64核心、2补充、4暂缓。核心是固定32输入×2；候选不是新grant或实际执行身份。
- 2补充：hybridsort-F256仅该F的四方比较可准备；lavamd-F128缺原始CH-P0，只能准备同F的CH/DH绝对比较。后者需独立审核约67.336GiB历史RSS及执行资源，不可用旧失败基线或IR补齐。
- 4暂缓：SYRK-F128/F256、hybridsort-F128、lavamd-F256。恢复前置见Agent A；本Goal不授权恢复或重跑。
- 固定 Core `9eedb3131937748f0492fa83aad37d3691118d70`，Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`，binary SHA256 `02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d`；1410/1410/1410/850MHz，L2 10MiB。配置逐字节/有效选项核验已完成。
- F64/128/256同时对应shared credit255/319/447；不能把它写成孤立队列容量变化。CH/DH仍有7项L1设计差异，不是等面积比较。

## 首批16候选：仅待未来授权

| 顺序 | 固定程序 | 选入理由 |
|---|---|---|
| 1 | convolutionSeparable | 水平/垂直卷积、halo和中间结果的阶段对照 |
| 2 | scan | 局部扫描、部分和、统一更新的依赖链 |
| 3 | 2DCONV | 单kernel 3×3重叠邻域 |
| 4 | ATAX | 两访问方向与中间向量依赖 |
| 5 | MVT | 不同方向与独立输出 |
| 6 | BICG | 列/行矩阵向量次序对照 |
| 7 | vectorAdd | 负响应流式边界对照 |
| 8 | GEMM | 下游扩容零响应对照 |

每个程序按F128、F256排序。该批次在任何新CH结果出现前固定，覆盖机制与正/负/零对照；不改变最终核心32/完整35身份。首批完成并审查通过后再制定其余48核心候选批次，不根据首批性能删改最终统计集合。

## 可复现入口

1. [第一阶段科学身份冻结](agents/A/PHASE_I_ORIGINAL350_FREEZE.json)、[独立集合核查](agents/C/INDEPENDENT_SET_AUDIT.json)。原始scan-M16在旧AUTO_SUMMARY显示PENDING_NO_RESULT，但有精确typed engineering-negative证书37842…，不是尚在运行。
2. [70候选矩阵](agents/A/CH_CANDIDATE_MATRIX.json)、[配置核验](agents/A/CONFIG_QUALIFICATION.json)、[首批16](agents/A/FIRST_BATCH.json)、[全部35六格计划](SIX_CELL_PAIRING_PLAN.json)。新CH周期均为null、未测量。
3. [分批、资源与归档资格](RESOURCE_AND_BATCH_PLAN.md)、[Agent A资格报告](agents/A/RESOURCE_AND_ARCHIVE_QUALIFICATION.json)、[CPU解析验证](agents/A/CPU_ONLY_PARSER_QUALIFICATION.json)。CPU准备PASS不等于原生模拟运行资格已授予。
4. [25个kernel机理与证据](agents/B/KERNEL_ANALYSIS_PREPARATION.md)、[机器可读矩阵](agents/B/KERNEL_HYPOTHESIS_MATRIX.json)、[对照与新观测设计](WORKLOAD_CONTROL_AND_OBSERVATIONS.md)。候选源码、trace和运行实测分栏。
5. [统计与硬件边界](STATISTICS_AND_HARDWARE_BOUNDARIES.md)、[独立科学复核](agents/C/SCIENTIFIC_REVIEW.md)、[Root集成资格](CPU_INTEGRATION_QUALIFICATION.json)。
6. [待批准的首批正式执行Goal](NEXT_EXECUTION_GOAL_PENDING_APPROVAL.md)。本文件不是执行批准。
7. [来源与旧计划状态差分](AUTHORITY_SOURCES.json)、[计划候选发布状态](CANDIDATE_RELEASE_STATE.json)、[无新实验完整性](NO_EXECUTION_INTEGRITY.json)、[成员SHA](MANIFEST.json)。发布提交与远端回读见 PUBLICATION_READBACK.json（单独后续发布回执，不纳入科学包自引用哈希）。

旧规划 `5ba029e60c2e7523b193043b345990c7ae52531c` 使用330/335及lavamd-Q64运行中的旧快照，原文保存在authority中。本包更新为终态331/336；方法规则仍沿用其匹配/共同集合/V2组合门槛。Atlas固定为 `47a097aad4406893a07f8d230e1e0a850609bf39`。

**结论边界：准备完成 ≠ CH已启动 ≠ 新CH性能已得到 ≠ 全35公平比较已完成。**
