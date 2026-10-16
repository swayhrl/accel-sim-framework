# Lane 6｜论文与PPA并行

先完整阅读同目录README.md、COMMON_CONTRACT.md、COORDINATION_PROTOCOL.md，再执行本文件。公共合同单独保存，避免六份副本漂移。

本轮身份：Lane 6；执行分支：`hrl/ep-l2-ft20261016-lane6-v1`。这是待启动的连续执行Goal，不是运行状态。历史文档中的字母Lane不在本轮重命名范围。

## Goal

立即起草机制论文与硬件成本分析，随独立验证结果更新；不等待所有性能矩阵结束。只写有证据支持的事实，结果缺口保留明确占位。

## 执行顺序

1. 独立Framework分支，仅修改论文、文字说明、图表脚本及成本账；不得修改benchmark、baseline、机制policy或原科学CSV。
2. 阅读架构/章程与阶段证据，以“数据驻留、事务完成、WB staging生命周期不同”为总问题。明确WBUF外置及并池是本次用户确认，C16 primary是本轮实验选择，不是已流片参数证明。
3. 建立CLAIM_EVIDENCE_MAP：每个claim映射实现路径、定向测试和CSV；区分已实现、已运行、观测/影子、oracle和计划。
4. 现有sector reuse支持流式/复用差异，不等于TVD hit或payload borrowing收益。历史WBUF4/8/16只作shadow诊断，不和新真实B16混画为同配置性能。
5. 先完成引言、问题、架构状态与接口、实验设置、PPA方法。图位：原架构与统一角色、预算/端口表、性能/ideal参考、局部机制与静态重划分消融。本文档不是要求绘制美工图片，可以先用可编辑占位示意。
6. PPA分别核算数据RAM（C16 1168x128B/slice；C8 1160）、Tag pointer、generation、per-payload role/sector/pin、RO completion、descriptor链、WAD/TVD增量、allocator、目录查找和bank仲裁。共同下层数据queue成本保留；动态存储与控制state分别计数，不用C++ sizeof推RTL面积。
7. 有真实RTL则做针对变化模块的差分综合并记录工具/工艺/频率/约束；没有工艺或源不伪造门数与时序，输出参数化bit账和具体缺失信息。TVD +1cycle是假设的时序模型，不是已通过静态时序分析。
8. 从Lane 5/4接收绑定manifest的完整结果，脚本生成图；ideal参考与预算内实现分开标记。主表包含不加速/退化负载，不依性能选样本。
9. 不预写摘要加速数字或“完整EP-L2已验证”；最终论点服从结果，可收敛到WB pooling或TVD/RO有效组合，不为保留故事扩大实验。

## 必须产物

PAPER_DRAFT_ZH_V1.md（可再形成英文稿）、CLAIM_EVIDENCE_MAP.md、PPA_LEDGER.md、FIGURE_INPUT_MANIFEST、可重复制图脚本、剩余论文必需证据清单。

首个交付必须有真实正文，不只目录。不在本Goal核查或重新声明会议截止/页数；采用用户已有投稿规范，未核实时标注待核。
