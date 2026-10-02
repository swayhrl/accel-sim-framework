# AWMA研究证据与文献笔记

## 最新入口｜2026-10-02，R25审定；R26已授权并发布handoff

- [R26最新授权状态](plans/STATUS_AFTER_R26_PRODUCTION_CAPACITY_AUTHORIZATION_2026-10-02.md)：Lane G/node109唯一新GPU任务；目前为AUTHORIZED/HANDOFF_READY，未据此宣称节点已经启动。
- [R26研究计划](plans/R26_TIED_WEIGHT_PRODUCTION_CAPACITY_PLAN_2026-10-02.md)：统一C1/S2组件、32步trajectory/checkpoint恢复、唯一batch轴的真实完整训练步容量边界。
- [R26完整Goal](https://github.com/swayhrl/accel-sim-framework/blob/67bb4c00236e52657130dd91ddf44fb6a2e22c87/docs/vm_tlb/chatgpt_handoff/awma/r26_tied_weight_production_capacity_v1/LANE_G_R26_TIED_WEIGHT_PRODUCTION_CAPACITY_109_GOAL.md)：从精确handoff HEAD执行，禁止结果后调tile/输入/判据。
- [R25接受审查](empirical/R25_TIED_WEIGHT_BROADER_VALIDATION_REVIEW_2026-10-02.md)：C1跨两点更快/省显存；S2额外容量跨模型成立，速度方向不跨模型保持。
- [R25历史收口状态](plans/STATUS_AFTER_R25_REVIEW_2026-10-02.md)：记录当时STOP状态，当前授权以R26最新状态为准。
- [R24审查](empirical/R24_TIED_WEIGHT_NATIVE_REVIEW_2026-10-02.md)：保留单点容量实证与原decision边界缺口记录。
- [本次更新前README快照](README_BEFORE_R26_2026-10-02.md)：旧R23G/Round24入口原文，旧“无新授权”不能覆盖R26。

R26只做accepted Llama的tied-weight-only训练集成。context与输入内容固定，复制
冻结序列增加physical batch；不把它称为多样数据训练或新holdout。主判据是同一
batch C1自然OOM、S2真实完成训练步的3/3复现，不以target peak数字替代能力验证。

**R25/R24/R23G COMPLETE/STOP；F/R22F1、E/R22E STOP；R20 CLOSED。**
**无174/Accel-Sim、profiler、hardware/PPA或deployment授权。**

Git保存代码和紧凑evidence；node164保持大型raw/checkpoint authority。所有CUDA/JIT
持有共享GPU lock。R26收口后STOP，不自动扩展到下一阶段。

---

## 历史Round22入口

- [Round22全面复审](rounds/2026-10-02_ROUND_22_RETROSPECTIVE_KERNEL_FAMILY_AUDIT.md)
- [34行边界账本](empirical/ROUND22_FAMILY_BOUNDARY_LEDGER.tsv)
- [Kernel-family-first规则](methodology/KERNEL_FAMILY_FIRST_REVIEW_V1.md)
- [Round22之前README快照](README_BEFORE_ROUND22_2026-10-02.md)

目标族直接响应、必要配套净成本、覆盖/非目标、完整边界分别报告；完整应用5%不是
统一否决门。新方法不追溯改判旧实验。软件positive可独立保留，不自动成为硬件动机。
