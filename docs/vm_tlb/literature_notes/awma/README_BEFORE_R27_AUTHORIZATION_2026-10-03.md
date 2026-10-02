# AWMA研究证据与文献笔记

## 最新入口｜2026-10-02，R26审查收口

- [R26集成容量审查](empirical/R26_TIED_WEIGHT_CAPACITY_REVIEW_2026-10-02.md)：接受冻结结论 `R26_INTEGRATED_BATCH_CAPACITY_EXTENSION_SUPPORTED`，限定于重复序列、tied-W五步完整训练流程；C1 B70/B71与S2 B71/B72各3/3端点。
- [R26当前STOP状态](plans/STATUS_AFTER_R26_REVIEW_2026-10-02.md)：Lane G/node109 COMPLETE/STOP；无自动后续GPU任务。
- [R26执行review pack](https://github.com/swayhrl/accel-sim-framework/tree/1a2485011b300cddd5137bbccb91dd6d30cfc22f/docs/vm_tlb/review_packs/AWMA_R26_TIED_WEIGHT_PRODUCTION_CAPACITY_BOUNDARY_109_V1)：执行commit `1a2485011b300cddd5137bbccb91dd6d30cfc22f`。
- [R26启动时README快照](README_BEFORE_R26_REVIEW_2026-10-02.md)、[原授权状态](plans/STATUS_AFTER_R26_PRODUCTION_CAPACITY_AUTHORIZATION_2026-10-02.md)及[原Goal](https://github.com/swayhrl/accel-sim-framework/blob/67bb4c00236e52657130dd91ddf44fb6a2e22c87/docs/vm_tlb/chatgpt_handoff/awma/r26_tied_weight_production_capacity_v1/LANE_G_R26_TIED_WEIGHT_PRODUCTION_CAPACITY_109_GOAL.md)仅作历史依据。
- [R25审查](empirical/R25_TIED_WEIGHT_BROADER_VALIDATION_REVIEW_2026-10-02.md)、[R24审查](empirical/R24_TIED_WEIGHT_NATIVE_REVIEW_2026-10-02.md)。

R26同批次B71见证支持S2显式容量模式比默认C1多运行一个physical batch；batch只是冻结序列的物理复制。B70完整step峰值S2反而高约3.83 MiB，两段formal计时均为MIXED。不能从本轮推断普遍显存下降、统一加速、全参数训练或部署就绪。R25 parent W/m/v位哈希未复现，R26用同一个披露并冻结的起点作两臂比较。Git pack核验与node164执行receipt的界线见审查文档。

**R26/R25/R24/R23G COMPLETE/STOP；F/R22F1、E/R22E STOP；R20 CLOSED。无新的AWMA GPU、174/Accel-Sim、profiler、hardware/PPA或deployment授权。**

## 方法与历史入口

- [Round22全面复审](rounds/2026-10-02_ROUND_22_RETROSPECTIVE_KERNEL_FAMILY_AUDIT.md)
- [34行边界账本](empirical/ROUND22_FAMILY_BOUNDARY_LEDGER.tsv)
- [Kernel-family-first规则](methodology/KERNEL_FAMILY_FIRST_REVIEW_V1.md)
- [Round22之前README快照](README_BEFORE_ROUND22_2026-10-02.md)

目标族直接响应、必要配套净成本、覆盖/非目标、完整边界分别报告；完整应用5%不是统一否决门。新方法不追溯改判旧实验。软件positive可独立保留，不自动成为硬件动机。
