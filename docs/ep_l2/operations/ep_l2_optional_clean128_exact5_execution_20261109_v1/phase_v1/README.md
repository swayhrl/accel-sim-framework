# Stencil EXT0/EXT2 阶段分析审查入口

**后续状态：**用户已明确授权新增 Stencil EXT1 一个点；当前因 Native 空间准入 HOLD，仍未绑定正式新 Spec、登记或启动。见 [授权后现场回执](authorized_v1/README.md)。下列审查文档保留授权前的历史状态。

1. [EXT1 单点审查结论](EXT1_REVIEW_20261111.md)：建议批准一个新增点用于机制归因；执行授权仍待明确给出。
2. [100-kernel 分析及判断](EP_L2_STENCIL_PHASE_AND_EXT1_DECISION_20261110.md)：已接受两点的同源对照、守恒与证据边界。
3. [Stencil EXT1 单点精确申请草案](EP_L2_STENCIL_EXT1_EXACT_REQUEST_DRAFT_20261110.md)：**待明确授权**；没有登记、启动或借旧余额。
4. [逐项证据](PHASE_EVIDENCE.json)、[100 行 CSV](PHASE_ROWS.csv)、[小型汇总](PHASE_SUMMARY.json)；`analyze_stencil_phase.py` 在 174-new 对已接受 gzip raw 做一次流式校验，`summarize_phase.py` 可重算汇总。

本目录是现有五点执行分支的分析补充，原 `final_v1/` 正式验收与归档不变。
