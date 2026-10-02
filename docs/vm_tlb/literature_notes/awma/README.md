# AWMA研究证据与文献笔记

更新：2026-10-02，Round22回顾性kernel-family审查。

**Lane E/F/G和174/Accel-Sim本轮均无新执行授权。R20维持CLOSED；R21A保留原MIXED/STOP。** 新评价规则不追溯改判旧实验，不是重跑旧Goal的许可。

## 当前入口

- [Round22全面复审](rounds/2026-10-02_ROUND_22_RETROSPECTIVE_KERNEL_FAMILY_AUDIT.md)：R21A逐组计时复算；R81等局部软件positive；C16低coverage停止理由修正；正确性/输入/模型边界与性能negative分开。
- [34行边界账本](empirical/ROUND22_FAMILY_BOUNDARY_LEDGER.tsv)：34行是问题/结果边界，不是34个独立新实验。逐项标本轮直接复核或继承材料。
- [Kernel-family-first规则](methodology/KERNEL_FAMILY_FIRST_REVIEW_V1.md)：目标族、必要配套成本、覆盖率/非目标退化、完整边界四层评价；5%不再作为所有机制统一否决门槛。
- [R21A逐组重算](empirical/R21A_RECOMPUTED_GROUP_TIMING.tsv)：由62af34149的DREADY_TIMING重算，无删样、补样或新测量。
- [R19F2 projection重算](empirical/R19F2_PROJECTION_RECOMPUTED.tsv)：由7b87638的STAGE_B_TIMING_P重算；不是独立验证。

## 关键判断

R21A：模型/数值资格已建立；整段Dready响应mixed；TP族响应、非TP退化与在线准备成本均未测。下一步应先设计最小分族观测，而不是把5%改成4%或自动打开Donline/holdout。

R81：预注册稀疏状态head降时44.8%–53.4%是真实局部软件结果，宽词表状态却退化6.7%–27.5%。不能只报其中一侧，已有软件近邻必须保留。

CCE、R19 FP8、fast-weight、R101 S128：应作为局部/算子级软件positive保留；原特定硬件动机关闭不等于成果为零。

R20：always-worklist完整solver慢66.6%是有效固定候选negative；late-only hybrid因formal B0 niter失败没有有效性能结论。原关闭决策不变，不启动救援实验。

## 历史索引

[Round22之前README快照](README_BEFORE_ROUND22_2026-10-02.md)保留Round21A、Round21、Round20及更早导航。原始review packs、raw、合同和执行标签均未修改。

Git保存代码与紧凑报告/索引；164保持大数据authority，109保留活跃副本，174不stage大trace。失败先保存输出与身份再退出。功能与observer默认OFF、分开控制。
