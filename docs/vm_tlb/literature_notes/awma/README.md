# AWMA论文阅读笔记｜ChatGPT支线

更新：2026-10-02，Round21A source/input qualification。R20保持CLOSED。Round21的泛“双向图准备”问题已收窄为NequIP/OpenEquivariance atomic→deterministic图就绪成本；已具备一轮bounded Lane F Native资格/诊断的source与输入authority，174/Accel-Sim仍STOP。

## 当前入口

- [Round21A：模型/后端/真实输入资格](rounds/2026-10-02_ROUND_21A_SOURCE_INPUT_QUALIFICATION.md)：NequIP与MACE强路径证明Sobek式双CSR不是通用必需；保留更窄的OpenEquivariance atomic vs receiver-sorted deterministic readiness问题。固定OAM-S与官方Si extxyz输入，先做free-prep headroom，再决定是否在线准备。

- [Round21：R20后的问题发现](rounds/2026-10-02_ROUND_21_POST_R20_PROBLEM_DISCOVERY.md)：筛查3DGS、几何神经网络、Muon和生成式推荐。只保留“强软件之后的动态图就绪成本”作为准备优先级；不是已测瓶颈或硬件机会。
- [R21动态几何图准备卡](problem_cards/R21_DYNAMIC_GRAPH_READINESS_PREPARATION.md)：先核真实trained模型/输入/后端兼容性；prepared graph、GPU邻居构建和合法reuse先纳入基线。不是节点执行指令。
- [R21来源登记](empirical/ROUND21_SOURCE_REGISTER.tsv)：五篇论文正文关键部分、作者文章/官方资料与固定源码的阅读范围分别登记，不冒充全文复现。
- [R21证据与决策表](empirical/ROUND21_EVIDENCE_AND_DECISIONS.tsv)：源码事实、论文结果、假设和既有AWMA结果分开。

## R20最终状态：关闭，不重跑

最终执行：`hrl/awma-r20r5-hybrid-native-109-v1@57ffbd4a8c8fedb1f050913bd2801c76eb1a4e7c`，tree `45c273a8bab7c51ba77d7417bf6ef64fcda3fe05`。

最终审查：`hrl/awma-r20r5-hybrid-native-handoff-v1@0c6cda2f680fa93ed5ea7d4b098eef5044a8a0c4`，文件`docs/vm_tlb/chatgpt_handoff/awma/r20r5_hybrid_native_v1/STATUS_AFTER_R20R5_FINAL_CLOSURE.md`。

保留三种不同证据：固定always-worklist S1约66.6%退化是有效窄scope测量；O2=11.77%是跨run零开销估算；最终hybrid正式B0发生exact-niter失配，没有有效性能结论。关闭是投入/合同终点，不是所有active-world方法无收益的证明。

## 历史记录与解释边界

完整Round20及Round18导航、历史authority与更早README入口均原样保存在[Round21前README快照](README_BEFORE_ROUND21_2026-10-02.md)。原文献/实验文件未删除、未重写。

必须继承：

- R53有实际执行，`843ad43ad33153bf73a0e51aed6d8ac309356cae`，不能根据旧“仅设计”条目重开。
- R17中Q1快于整个Q32 batch不证明单query无残差；保留停止但不夸大充分性。
- R19 FP8是同表示软件诊断消除主要成本，不是stock TE已提供该融合，不外推所有低精度。
- IBP/GraphSAGE是因果诊断未资格化，不是dense staging零成本。
- CCE zero-init、两chunk fast-weight、selector/grammar等均有既有窄scope结果；不能换模型/名称重新发现。

## 默认研究与交付规则

问题→最近邻能力→真实输入→最小对照；模型资产不决定研究问题。允许小原型辅助发现，理想headroom只在其假设清楚时使用，不把结构比例叫可实现加速。

功能与observer分离、默认OFF；资格检查与真正采集合并滚动进行。新实验的失败输出应先保存再抛异常，不为追回旧失败数组重跑已关闭工作。Source/API存在不等于109 runtime合格，复用工程不继承科学结论。

Git仅保存代码、紧凑报告、索引和receipt。大资产/raw仍以164为authority，109是活跃副本，174不本地stage大trace。

分支：`hrl/awma-chatgpt-literature-notes-v1`。
