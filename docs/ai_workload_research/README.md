# AI-ARCH｜AI负载体系结构研究科研协调入口

> **新窗口完整交接（2026-10-13）：** [AI-ARCH Discovery handoff V1](AI_ARCH_DISCOVERY_HANDOFF_CONTEXT_2026-10-13_V1.md)。AI-ARCH是总研究计划，本ChatGPT窗口承担Discovery与现阶段总协调；AWMA继续原独立窗口，C16作为历史证据保留。

**角色：研究规划与证据导航分支。不是C16/AWMA的统一实验代码主干，不是任何执行Goal的授权源。**

研究范围：AI训练与推理；LLM、MoE、多模态、推荐、GNN、科学计算/3DGS等非LLM应用；单GPU、多GPU、CPU–GPU协同；计算、调度、数据就绪、片上资源、Cache/TLB、通信、存储、状态生命周期与可靠性。


## 当前组合入口（2026-11-09）

- [当前状态](CURRENT_STATE.md)与[固定 authority 索引 V2](AI_ARCH_RESEARCH_AUTHORITY_INDEX_V2.md)：Q1 已完成且有限结论经独审与科学窗口接受；T16 是原基线，数值敏感性保留，未晋升硬件候选。3DGS PRIMARY、Hybrid/KV SECONDARY、MoE H200 CONDITIONAL、Qwen PARKED。
- 固定入口：[Q1 执行](https://github.com/swayhrl/accel-sim-framework/tree/5787826ca21f7af958e6e1c1f828d62fd58a1ec4/docs/ai_workload_research/runs/AI_ARCH_Q1_COMPLETION_109_V1)、[完整交接](https://github.com/swayhrl/accel-sim-framework/tree/00abf55d44ad02a18d529eb0afe4d02dc0ceadfe/docs/ai_workload_research/handoff/AI_ARCH_FULL_HANDOFF_20261109_V1)、[已接受有限独审](https://github.com/swayhrl/accel-sim-framework/tree/06355f73caaa6f38697d9acac94ac81a47c27e62/docs/ai_workload_research/reviews/AI_ARCH_Q1_INDEPENDENT_REVIEW_20261109_V1)。[状态供给反事实 Main 报告](https://github.com/swayhrl/accel-sim-framework/blob/be7fe374c1402498eeab3d3f3be97a9eb01667ab/docs/ai_workload_research/reviews/AI_ARCH_Q1_STATE_SUPPLY_COUNTERFACTUAL_MAIN_V1/REPORT.md)待科学窗口审查，单一 `shN` 驻留实验只是设计、未执行。
- [已接受研究组合历史入口](https://github.com/swayhrl/accel-sim-framework/tree/f88e40123f4060328aa50a16d22fa328cee51cfe/docs/ai_workload_research/discovery/AI_ARCH_NEXT_STAGE_PORTFOLIO_REVIEW_V1)保留；当前 `NO_GPU_PROBE_READY`。本协调更新不启动 GPU。
- [A80原完整快照](https://github.com/swayhrl/accel-sim-framework/blob/ed365741b230718f6ffc1ccbed125fc2566aac15/docs/ai_workload_research/CURRENT_STATE.md)：保留A79锁冲突STOP、formal0及全部旧边界；不是当前任务监控。

## 从这里开始

- [统一问题图谱 V1](AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md)：按负载/约束组织问题、已知现象、未知前提和潜在架构研究方向。
- [C16 × AWMA跨项目证据索引 V1](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)：每条证据的实验范围、实际结论、测量层级和固定来源。
- [当前项目状态](CURRENT_STATE.md)：最新可核对的科研入口与待审结果，供两个ChatGPT协调窗口使用。
- [协调与变更规则](COORDINATION_PROTOCOL.md)：如何更新、如何避免干扰独立实验及已有结果。

## 本分支与两个项目的关系

- 本分支只收录跨项目科研底稿、固定Git证据入口、文献调研和研究决策；**不会把C16与AWMA实验分支直接合并到一起**。
- C16的历史结果仍以各自accepted commit及review pack为科学依据；AWMA已有机制、软件实验和正在进行的任务仍以各自合同及review pack为依据。
- 研究图谱中的科学状态不覆盖原实验`PASS/FAIL/STOP`；新的上层研究优先级也不改变任何已冻结模型、输入、容差、源码或模拟器参数。
- 两个项目可只`git fetch`并阅读此分支的Markdown，无需人工转发文件或切换现有执行worktree。

## 固定状态入口（2026-10-13，历史非实时）

- C16最新Problem Discovery Reset：[`635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f`](https://github.com/swayhrl/accel-sim-framework/commit/635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f)，目前无获准的C16 native任务。
- C16 Stage A收口：[`ccd6928bfb420d1e4c554ec0e377bb8fbe377501`](https://github.com/swayhrl/accel-sim-framework/commit/ccd6928bfb420d1e4c554ec0e377bb8fbe377501)，`TERMINAL_PARTIAL`，不得解释为AI没有新瓶颈。
- AWMA R27R3事前交接：[`29ce051f982f3854bd4392a94e4195c59340123b`](https://github.com/swayhrl/accel-sim-framework/commit/29ce051f982f3854bd4392a94e4195c59340123b)，原Goal/STOP规则不变。
- AWMA R27R3执行提交：[`7bd31fae4c54e121d54743a803d978ee02a64959`](https://github.com/swayhrl/accel-sim-framework/commit/7bd31fae4c54e121d54743a803d978ee02a64959)，独立[AWMA科学审阅](https://github.com/swayhrl/accel-sim-framework/blob/d6e9bbfb562814bcd5dc5adb444d3c572e7f446b/docs/vm_tlb/literature_notes/awma/empirical/R27R3_B0_REFERENCE_REPEATABILITY_REVIEW_2026-10-13.md)已接受`R27R3_B0_REFERENCE_NOT_REPEATABLE`有限STOP；B0-B0完整梯度25个元素超原容差，组件根因未定位且无容量实验。详见[跨项目E-A13](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)及[同步边界](R27R3_INDEPENDENT_REVIEW_SYNC_2026-10-13.md)。
- AWMA研究笔记（已审阅后的状态）：[`f0a6ec310c09cd011fffbe8a5ca22d6effacdf6b`](https://github.com/swayhrl/accel-sim-framework/commit/f0a6ec310c09cd011fffbe8a5ca22d6effacdf6b)；当前R27R3已STOP，协调分支不产生新实验授权。

## 一条重要边界

本协调分支的提交、合并、标签更新或文件维护，都**不自动批准GPU执行、模型下载、重编译、Profiler、模拟器、硬件实验、holdout、重启/修改运行中的Goal**。具体执行必须由对应项目单独审核并形成冻结合同。
