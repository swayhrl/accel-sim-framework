# AWMA论文阅读笔记｜ChatGPT支线

更新：Round18，2026-10-01。文献、作者源码、执行receipt与研究判断分开。当前Lane E/174-new、Lane F/109、Lane G/109全部STOP。

## 当前入口

- [Round18全面横向复审](rounds/2026-10-01_ROUND_18_COMPREHENSIVE_FRONTIER_REVIEW.md)：41项原始来源，15项正文关键部分、26项原始摘要；另核3份作者仓库文档。覆盖低比特、执行编译、MoE、SSM/TTT、扩散、Agent、视频、混部、压缩、通信、稀疏、翻译及可靠性/能耗/异构外围。
- [来源登记](empirical/ROUND18_SOURCE_REGISTER.tsv)：指定版本/阅读深度/限制，不将取回失败当作者未公开。
- [60条实验与分析证据](empirical/ROUND18_EXPERIMENT_EVIDENCE.tsv)：含摘要级aggregate，不称所有记录具备完整复现配置。
- [AWMA边界账本](empirical/ROUND18_AWMA_BOUNDARY_LEDGER.tsv)：做过什么、未做什么、仍未知什么及核查深度。
- [候选与最小检验](problem_cards/R18_SHORTLIST_AND_MINIMAL_TESTS.md)：优先准备低比特表示就绪、动态工作集；fast-weight条件保留。不是execution Goal。
- [Round18勘误：R53实际已执行](rounds/2026-10-01_ROUND18_ERRATUM_R53_EXECUTION.md)：R53 authority为`843ad43ad...`，最终`R53_ALGORITHM_CHANGE_NOT_MAPPING_GAIN_V1`；后续动态执行不得重命名复跑该边界。

## 需要首先继承的解释修正

R17R1正式execution标签与raw保留，但**Q1比完整Q32 batch先完成，不能证明没有单query可优化残差**。本轮研究判断是“质量合格的成熟软件基准已建立，GPU-local残差仍未归因/未资格化”；不重启实验、不改历史证据。

R53已实际执行并收口为`R53_ALGORITHM_CHANGE_NOT_MAPPING_GAIN_V1`；Round18正文中“未取得完成receipt”的说法以勘误文件为准。

Round16分别是：R102输入未资格化；VLA工作真实但state/lifetime目标成本未知；CCE特定zero-init成本经局部软件协议消除。不同终点不能都算“整个领域无空间”。

允许现象驱动与文献驱动小原型并行；5%不是所有探索的统一前置条件。冻结基线不等于禁止候选改变明确的结构/策略。

## 最新执行authority（只读引用）

- Round16收口：`31d585dc44f90eb70f83603c8b87a2d06efff01a`，`docs/vm_tlb/chatgpt_handoff/awma/round16_dual_lane_v1/FINAL_ROUND16_CLOSEOUT_2026-09-30.md`。
- R17R1：`29ecc6e5e37005046b1a563c830bed9ae58af656`，`docs/vm_tlb/review_packs/AWMA_R17R1_GRAPH_SEARCH_109_V2/FINAL_DECISION.md`。
- R17 LaneG最近邻：`f72aca7938a1b2e8bb2f62953e308444babd8489`，独立CPU文献分支；本轮引用其已报告结果，不合并其worktree。
- R53执行：`843ad43ad33153bf73a0e51aed6d8ac309356cae`，`docs/vm_tlb/review_packs/AWMA_R53_ONLINE_WORKSET_QUALIFICATION_V1/FINAL_DECISION.md`。

## 历史索引

完整的Round01–17导航、基础11篇阅读笔记、旧commit索引与74条历史workload口径，保存在同目录的[更新前README快照](README_PRE_ROUND18.md)。原文献文件未删除、旧实验未重写。

近期历史入口：
- [Round17检索筛选](rounds/2026-09-30_ROUND_17_RETRIEVAL_PROBLEM_SCREEN.md)
- [Round15横向收口](rounds/2026-09-30_ROUND_15_HORIZONTAL_CLOSEOUT_AND_CURRENT_FRONTIER.md)
- [Round11宽范围算法与数据流](rounds/2026-09-27_ROUND_11_ALGEBRA_COMPRESSION_AND_CLOSED_LOOP.md)
- [Round09跨方向文献](rounds/2026-09-27_ROUND_09_BROAD_SIDE_RESEARCH.md)
- [Round06 R53设计](rounds/2026-09-27_ROUND_06_R53_RESEARCH_AND_DESIGN.md)：设计不是完成receipt。
- [Round04问题发现](rounds/2026-09-26_ROUND_04_PROBLEM_DISCOVERY.md)：旧优先级不是当前执行命令。

## 使用规则

原始来源→具体实验组→控制变量/实际硬件→证据层级→适用边界。作者观察、我们的推断、候选假设分开；缺失保持未知。不得把吞吐摊销、profiled局部比例、模拟器干预差值直接叫真实可加运行时间或硬件收益。

不同轮次有重复阅读，篇数不能直接累加。KEY不是逐字全文审计；ABS不是完整实验资格；源码可获取不是已在109运行。原论文PDF不入仓库；大raw/模型仍按node164 authority、109活跃副本、174不存大trace规则执行。

分支：`hrl/awma-chatgpt-literature-notes-v1`。目录：`docs/vm_tlb/literature_notes/awma/`。
