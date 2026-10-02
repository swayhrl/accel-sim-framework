# AWMA研究证据与文献笔记

## 最新入口｜2026-10-03，R27单轮Goal已授权并发布handoff

- [当前授权状态](plans/STATUS_AFTER_R27_AUTHORIZATION_2026-10-03.md)：仅Lane G/node109的R27为AUTHORIZED/HANDOFF_READY；发布不代表已启动。
- [R27合并轮次计划](plans/R27_VARIED_BATCH_CAPACITY_PLAN_2026-10-03.md)：同一Goal内顺序完成R26原始证据读回、固定多样输入、容量端点，以及仅positive时的32步/恢复。
- [R27完整Goal](https://github.com/swayhrl/accel-sim-framework/blob/5144bde8f9d7b399a596395e0c88ee89025b3a6f/docs/vm_tlb/chatgpt_handoff/awma/r27_varied_batch_capacity_v1/LANE_G_R27_VARIED_BATCH_CAPACITY_109_GOAL.md)：精确handoff HEAD `5144bde8f9d7b399a596395e0c88ee89025b3a6f`；不在通过闸门之间额外开轮次。
- [R26接受审查](empirical/R26_TIED_WEIGHT_CAPACITY_REVIEW_2026-10-02.md)：重复序列五步流程下C1 B70、S2 B71；B70完整step峰值S2略高且计时MIXED。
- [R26历史STOP状态](plans/STATUS_AFTER_R26_REVIEW_2026-10-02.md)、[本次更新前README快照](README_BEFORE_R27_AUTHORIZATION_2026-10-03.md)仅作当时状态依据。
- [R25审查](empirical/R25_TIED_WEIGHT_BROADER_VALIDATION_REVIEW_2026-10-02.md)、[R24审查](empirical/R24_TIED_WEIGHT_NATIVE_REVIEW_2026-10-02.md)。

R27使用单一固定WikiText-2 raw **train** token bank，batch内和step间内容变化；只测已限定的Llama tied-W流程。容量搜索只改变物理B；source/input/判据在观察容量前冻结。负面或不稳定结果即STOP，不调数据、tile或容差。C1仍默认，S2仍是显式capacity opt-in。无formal计时、部署、全参数训练或硬件/PPA扩展。

**R27仅Lane G/node109 AUTHORIZED/HANDOFF_READY；R26/R25/R24/R23G COMPLETE/STOP；F/R22F1、E/R22E STOP；R20 CLOSED。174/Accel-Sim无新任务。**

## 方法与历史入口

- [Round22全面复审](rounds/2026-10-02_ROUND_22_RETROSPECTIVE_KERNEL_FAMILY_AUDIT.md)
- [34行边界账本](empirical/ROUND22_FAMILY_BOUNDARY_LEDGER.tsv)
- [Kernel-family-first规则](methodology/KERNEL_FAMILY_FIRST_REVIEW_V1.md)
- [Round22之前README快照](README_BEFORE_ROUND22_2026-10-02.md)

目标族直接响应、必要配套净成本、覆盖/非目标、完整边界分别报告；完整应用5%不是统一否决门。新方法不追溯改判旧实验。软件positive可独立保留，不自动成为硬件动机。
